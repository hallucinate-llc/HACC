#!/usr/bin/env python3
"""Retry downloads with Playwright and search Brave as a double-fallback.

Workflow:
 - Load `research_results/documents/download_manifest.json`
 - Find entries where `content_type` does not contain 'pdf' or file is missing/small
 - Attempt Playwright re-download (browser context)
 - If still missing, run Brave search for likely PDF matches and try to download alternates
 - Update `download_manifest.json` for any recovered files

Requires: `playwright` installed and optional `BRAVE_API_KEY` env var for Brave API.
"""
from __future__ import annotations

import json
import os
import re
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except Exception:
    HAS_PLAYWRIGHT = False

ROOT = Path(os.getcwd())
RAW_DIR = ROOT / "research_results" / "documents" / "raw"
MANIFEST_PATH = ROOT / "research_results" / "documents" / "download_manifest.json"

MIN_PDF_SIZE = 512  # bytes — treat smaller as suspicious


def load_manifest() -> Dict:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_manifest(m: Dict) -> None:
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2, ensure_ascii=False)


def looks_like_pdf_bytes(data: bytes) -> bool:
    return data[:5] == b"%PDF-"


def save_bytes(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def try_playwright_download(url: str, dest: Path, timeout_ms: int = 90000) -> tuple[bool, str]:
    if not HAS_PLAYWRIGHT:
        return False, "playwright not available"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()
            resp = None
            try:
                resp = page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            except Exception as e:
                context.close()
                browser.close()
                return False, f"goto failed: {e}"

            try:
                body = resp.body() if resp else b""
            except Exception:
                body = b""

            ctype = (resp.headers.get("content-type") if resp else "") or ""
            if ("application/pdf" in ctype.lower()) or looks_like_pdf_bytes(body):
                save_bytes(dest, body)
                context.close()
                browser.close()
                return True, f"saved from response (content-type={ctype or 'unknown'})"

            try:
                locator = page.locator("a[href$='.pdf'], a[href*='.pdf']").first
                if locator.count() > 0:
                    href = locator.get_attribute("href")
                    if href:
                        if href.startswith("/"):
                            pdf_url = page.url.rstrip("/") + href
                        else:
                            pdf_url = href
                        resp2 = page.goto(pdf_url, wait_until="networkidle", timeout=timeout_ms)
                        try:
                            body2 = resp2.body() if resp2 else b""
                        except Exception:
                            body2 = b""
                        c2 = (resp2.headers.get("content-type") if resp2 else "") or ""
                        if ("application/pdf" in c2.lower()) or looks_like_pdf_bytes(body2):
                            save_bytes(dest, body2)
                            context.close()
                            browser.close()
                            return True, f"followed link and saved (content-type={c2 or 'unknown'})"
            except Exception:
                pass

            if body:
                save_bytes(dest, body)

            context.close()
            browser.close()
            return False, f"not a PDF (content-type={ctype or 'unknown'})"
    except Exception as e:
        return False, f"playwright error: {e}"


def search_brave_for_pdf(query: str, count: int = 10) -> List[str]:
    # lazy import to avoid hard dependency if not used
    try:
        from collect_brave import BraveCollector
    except Exception:
        return []

    # Rate limit and backoff to avoid hitting Brave API rate limits (HTTP 429).
    RATE_LIMIT_DELAY = float(os.environ.get("BRAVE_RATE_LIMIT_DELAY", "0.5"))
    MAX_RETRIES = int(os.environ.get("BRAVE_MAX_RETRIES", "3"))

    bc = BraveCollector()
    attempt = 0
    results = []
    while attempt < MAX_RETRIES:
        try:
            results = bc.search(query, count=count)
            break
        except Exception as e:
            msg = str(e)
            # If we see a 429 or rate-limit in the error, backoff and retry
            if "429" in msg or "Too Many Requests" in msg or "rate" in msg.lower():
                sleep_for = (2 ** attempt) * RATE_LIMIT_DELAY
                time.sleep(sleep_for)
                attempt += 1
                continue
            # For other errors, give up and return empty
            return []

    # polite pause between successive Brave queries
    try:
        time.sleep(RATE_LIMIT_DELAY)
    except Exception:
        pass

    urls = []
    for r in results:
        if r.get("url"):
            urls.append(r.get("url"))
    return urls


def try_http_download(url: str, dest: Path, timeout: int = 30) -> tuple[bool, str]:
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.content
        ctype = (r.headers.get("content-type") or "").lower()
        if ("application/pdf" in ctype) or looks_like_pdf_bytes(data):
            save_bytes(dest, data)
            return True, f"saved via requests (content-type={ctype or 'unknown'})"
        else:
            # save anyway for debugging
            save_bytes(dest, data)
            return False, f"not a PDF (content-type={ctype or 'unknown'})"
    except Exception as e:
        return False, f"http error: {e}"


def main():
    m = load_manifest()
    downloads = m.get("downloads", [])

    problematic = []
    for item in downloads:
        filepath = item.get("filepath")
        url = item.get("url")
        ctype = (item.get("content_type") or "").lower()
        size = item.get("file_size") or 0
        file_exists = filepath and Path(filepath).exists()

        if not file_exists or ("pdf" not in ctype) or size < MIN_PDF_SIZE:
            problematic.append(item)

    if not problematic:
        print("No problematic downloads found.")
        return

    print(f"Found {len(problematic)} problematic downloads; attempting recovery...")

    recovered = 0

    for item in problematic:
        url = item.get("url")
        filepath = item.get("filepath")
        dest = Path(filepath) if filepath else RAW_DIR / (str(int(time.time())) + ".pdf")

        print(f"Trying Playwright: {url}")
        ok, note = try_playwright_download(url, dest)
        print(" ->", "OK" if ok else "FAIL", note)
        if ok:
            stat = dest.stat()
            item["filepath"] = str(dest)
            item["download_date"] = datetime.now().isoformat()
            item["file_size"] = stat.st_size
            item["content_type"] = "application/pdf"
            recovered += 1
            continue

        # If playwright failed, try Brave search fallback using filename heuristics
        fname = url.split('/')[-1]
        # Clean URL fragments and query
        fname = re.sub(r"[?#].*$", "", fname)
        if fname:
            query = f'"{fname}" filetype:pdf'
        else:
            # fallback: search by domain + probable title words
            domain = re.sub(r"https?://(www\.)?", "", url).split('/')[0]
            query = f'site:{domain} filetype:pdf'

        print(f"Searching Brave for: {query}")
        candidates = search_brave_for_pdf(query, count=10)
        tried = 0
        for c in candidates:
            if tried >= 6:
                break
            tried += 1
            print(f" Trying candidate: {c}")
            ok2, note2 = try_http_download(c, dest)
            print("  ->", "OK" if ok2 else "FAIL", note2)
            if ok2:
                stat = dest.stat()
                item["filepath"] = str(dest)
                item["download_date"] = datetime.now().isoformat()
                item["file_size"] = stat.st_size
                item["content_type"] = "application/pdf"
                recovered += 1
                break

        if not item.get("file_size") or item.get("file_size") < MIN_PDF_SIZE:
            print(f"Could not recover: {url}")

    save_manifest(m)
    print(f"Done. recovered={recovered}")


if __name__ == "__main__":
    main()
