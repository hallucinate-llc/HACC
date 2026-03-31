#!/usr/bin/env python3
"""playwright_redownload.py

Attempt to re-download problematic "PDF" URLs using a real browser context.

This is useful when servers return HTML challenge/login pages to plain HTTP
clients, but allow a browser to fetch the real PDF.

Outputs overwrite the hashed filenames in research_results/documents/raw.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Response


RAW_DIR = Path("research_results/documents/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Target:
    doc_id: str
    url: str


TARGETS: list[Target] = [
    Target(
        doc_id="36569dd9f987a996afefc9d54375067e",
        url="https://www.oregon.gov/ohcs/development/Documents/admin/09-16-2021-DEI-Agreement.pdf",
    ),
    Target(
        doc_id="4e61daf9249f61c5361c07e4550f5841",
        url="https://www.oregon.gov/ohcs/development/Documents/admin/09-02-2021-detailed-survey-report.pdf",
    ),
    Target(
        doc_id="11925ba57cc06a39fad9a6dc5a8cc1f0",
        url="https://www.racialequityalliance.org/wp-content/uploads/2016/11/gare-racial-equity-action-plans.pdf",
    ),
    Target(
        doc_id="24cbe0113967a4f6725bb7683d5ad024",
        url="https://www.racialequityalliance.org/wp-content/uploads/2015/10/gare-racial_equity_toolkit.pdf",
    ),
]


def looks_like_pdf_bytes(data: bytes) -> bool:
    return data[:5] == b"%PDF-"


def save_bytes(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def try_save_response_body(resp: Optional[Response], dest: Path) -> tuple[bool, str]:
    if resp is None:
        return False, "no response"

    try:
        ctype = (resp.headers.get("content-type") or "").lower()
        body = resp.body()
    except Exception as e:
        return False, f"failed to read response body: {e}"

    if "application/pdf" in ctype or looks_like_pdf_bytes(body):
        save_bytes(dest, body)
        return True, f"saved from response (content-type={ctype or 'unknown'})"

    # Save anyway (diagnostic) so we can inspect what came back.
    save_bytes(dest, body)
    return False, f"response was not PDF (content-type={ctype or 'unknown'})"


def redownload_one(page, target: Target, timeout_ms: int) -> dict:
    dest = RAW_DIR / f"{target.doc_id}.pdf"

    # Prefer page.goto so we get whatever a browser sees (JS challenges, redirects).
    resp = None
    try:
        resp = page.goto(target.url, wait_until="networkidle", timeout=timeout_ms)
    except Exception as e:
        return {
            "doc_id": target.doc_id,
            "url": target.url,
            "ok": False,
            "method": "goto",
            "error": f"goto failed: {e}",
        }

    ok, note = try_save_response_body(resp, dest)
    if ok:
        return {
            "doc_id": target.doc_id,
            "url": target.url,
            "ok": True,
            "method": "goto",
            "note": note,
            "bytes": dest.stat().st_size,
        }

    # If we got HTML, try to find an actual PDF link on the page and navigate to it.
    try:
        locator = page.locator("a[href$='.pdf'], a[href*='.pdf']").first
        if locator.count() > 0:
            href = locator.get_attribute("href")
            if href:
                # Resolve relative links.
                pdf_url = href
                if href.startswith("/"):
                    pdf_url = page.url.rstrip("/") + href
                resp2 = page.goto(pdf_url, wait_until="networkidle", timeout=timeout_ms)
                ok2, note2 = try_save_response_body(resp2, dest)
                return {
                    "doc_id": target.doc_id,
                    "url": target.url,
                    "ok": ok2,
                    "method": "follow_link",
                    "note": note2,
                    "bytes": dest.stat().st_size,
                    "followed": pdf_url,
                }
    except Exception:
        pass

    return {
        "doc_id": target.doc_id,
        "url": target.url,
        "ok": False,
        "method": "goto",
        "note": note,
        "bytes": dest.stat().st_size if dest.exists() else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=90_000)
    args = parser.parse_args()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        for t in TARGETS:
            res = redownload_one(page, t, args.timeout_ms)
            results.append(res)
            status = "OK" if res.get("ok") else "FAIL"
            extra = ""
            if res.get("method") == "follow_link" and res.get("followed"):
                extra = f" (followed {res['followed']})"
            print(f"{status}: {t.doc_id} -> {res.get('bytes', 0)} bytes [{res.get('note') or res.get('error','')}]{extra}")

        context.close()
        browser.close()

    ok = sum(1 for r in results if r.get("ok"))
    print(f"Done. {ok}/{len(results)} looked like PDFs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
