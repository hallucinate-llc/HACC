#!/usr/bin/env python3
import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Optional

from PIL import Image


ROOT = Path("/home/barberb/HACC")
WORKSPACE = ROOT / "workspace"
EXHIBIT_COVER_ROOT = WORKSPACE / "exhibit_cover_pages"
OUT_JSON = WORKSPACE / "evidence_binder_duplicate_analysis_2026-04-09.json"
OUT_MD = WORKSPACE / "evidence_binder_duplicate_analysis_2026-04-09.md"
CACHE_DIR = WORKSPACE / "evidence_binder_duplicate_analysis_2026-04-09_cache"
RENDER_DIR = CACHE_DIR / "renders"
TEXT_DIR = CACHE_DIR / "texts"


@dataclass
class ExhibitRecord:
    family_dir: str
    cover_page: str
    exhibit_label: str
    source: str
    source_kind: str
    source_exists: bool
    normalized_text_len: int = 0
    text_hash: Optional[str] = None
    text_simhash: Optional[str] = None
    image_hash: Optional[str] = None
    text_excerpt: str = ""


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_capture(cmd):
    return subprocess.run(cmd, check=True, text=True, capture_output=True).stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def normalize_text(text: str) -> str:
    text = text.replace("\x0c", "\n")
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str):
    return [tok for tok in normalize_text(text).split(" ") if tok]


def text_simhash(text: str) -> Optional[str]:
    tokens = tokenize(text)
    if len(tokens) < 10:
        return None
    shingles = []
    if len(tokens) >= 3:
        shingles = [" ".join(tokens[i:i + 3]) for i in range(len(tokens) - 2)]
    else:
        shingles = tokens
    weights = Counter(shingles)
    vec = [0] * 64
    for shingle, weight in weights.items():
        h = int(hashlib.blake2b(shingle.encode("utf-8"), digest_size=8).hexdigest(), 16)
        for i in range(64):
            if (h >> i) & 1:
                vec[i] += weight
            else:
                vec[i] -= weight
    out = 0
    for i, val in enumerate(vec):
        if val >= 0:
            out |= (1 << i)
    return f"{out:016x}"


def hamming_hex(a: str, b: str) -> int:
    return (int(a, 16) ^ int(b, 16)).bit_count()


def average_hash(image_path: Path, size: int = 8) -> str:
    img = Image.open(image_path).convert("L").resize((size, size))
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if p >= avg else "0" for p in pixels)
    return f"{int(bits, 2):0{size * size // 4}x}"


def parse_cover_pages():
    records = []
    for cover_path in sorted(EXHIBIT_COVER_ROOT.rglob("*_cover_page.md")):
        if "_tab_cover_page.md" in cover_path.name:
            continue
        text = cover_path.read_text(errors="replace")
        label = match_backtick_block(text, "EXHIBIT LABEL") or cover_path.stem
        source = match_backtick_block(text, "SOURCE FILE") or ""
        family_dir = cover_path.parent.name
        source_kind = classify_source(source)
        source_exists = False
        if source_kind == "path":
            source_exists = Path(source).exists()
        records.append(
            ExhibitRecord(
                family_dir=family_dir,
                cover_page=str(cover_path),
                exhibit_label=label,
                source=source,
                source_kind=source_kind,
                source_exists=source_exists,
            )
        )
    return records


def match_backtick_block(text: str, heading: str) -> Optional[str]:
    pattern = rf"`{re.escape(heading)}`\s+`([^`]+)`"
    m = re.search(pattern, text, re.S)
    if not m:
        return None
    return m.group(1).strip()


def classify_source(source: str) -> str:
    if not source:
        return "missing"
    if source.startswith("Not yet obtained.") or source.startswith("Reserved:"):
        return "placeholder"
    if source.startswith("/"):
        return "path"
    return "note"


def cached_path(prefix: str, source_path: Path, ext: str) -> Path:
    digest = sha256_text(str(source_path))
    return TEXT_DIR / f"{prefix}_{digest}.{ext}"


def extract_eml_text(path: Path) -> str:
    with path.open("rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    parts = [
        f"subject: {msg.get('subject', '')}",
        f"from: {msg.get('from', '')}",
        f"to: {msg.get('to', '')}",
        f"cc: {msg.get('cc', '')}",
        f"date: {msg.get('date', '')}",
        "",
    ]
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_content()
                    break
                except Exception:
                    pass
    else:
        try:
            body = msg.get_content()
        except Exception:
            body = ""
    parts.append(body or "")
    return "\n".join(parts)


def extract_pdf_text(path: Path) -> str:
    cache = cached_path("pdf", path, "txt")
    if cache.exists():
        return cache.read_text(errors="replace")

    text = ""
    try:
        text = run_capture(["pdftotext", "-layout", str(path), "-"])
    except Exception:
        text = ""

    # If pdftotext gets little or nothing, OCR a few pages.
    if len(normalize_text(text)) < 200:
        ocr_chunks = []
        with tempfile.TemporaryDirectory(prefix="binder_pdf_ocr_") as tmp:
            prefix = Path(tmp) / "page"
            try:
                run(["pdftoppm", "-f", "1", "-l", "5", "-r", "150", "-png", str(path), str(prefix)])
                for img_path in sorted(Path(tmp).glob("page-*.png")):
                    try:
                        ocr = run_capture(["tesseract", str(img_path), "stdout", "--psm", "6"])
                    except Exception:
                        ocr = ""
                    if ocr.strip():
                        ocr_chunks.append(ocr)
            except Exception:
                pass
        if ocr_chunks:
            text = text + "\n\n[OCR]\n" + "\n".join(ocr_chunks)

    cache.write_text(text, encoding="utf-8")
    return text


def extract_image_text(path: Path) -> str:
    cache = cached_path("img", path, "txt")
    if cache.exists():
        return cache.read_text(errors="replace")
    try:
        text = run_capture(["tesseract", str(path), "stdout", "--psm", "6"])
    except Exception:
        text = ""
    cache.write_text(text, encoding="utf-8")
    return text


def render_pdf_first_page(path: Path) -> Optional[Path]:
    out = RENDER_DIR / f"{sha256_text(str(path))}.png"
    if out.exists():
        return out
    try:
        run(["pdftoppm", "-f", "1", "-l", "1", "-r", "120", "-png", "-singlefile", str(path), str(out.with_suffix(""))])
    except Exception:
        return None
    return out if out.exists() else None


def analyze_source(record: ExhibitRecord):
    if record.source_kind != "path" or not record.source_exists:
        return

    path = Path(record.source)
    suffix = path.suffix.lower()
    text = ""
    image_hash = None

    try:
        if suffix in {".md", ".txt"}:
            text = path.read_text(errors="replace")
        elif suffix == ".eml":
            text = extract_eml_text(path)
        elif suffix == ".pdf":
            text = extract_pdf_text(path)
            rendered = render_pdf_first_page(path)
            if rendered and rendered.exists():
                image_hash = average_hash(rendered)
        elif suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif"}:
            text = extract_image_text(path)
            image_hash = average_hash(path)
        else:
            try:
                text = path.read_text(errors="replace")
            except Exception:
                text = ""
    except Exception:
        text = text or ""

    normalized = normalize_text(text)
    record.normalized_text_len = len(normalized)
    if normalized:
        record.text_hash = sha256_text(normalized)
        record.text_simhash = text_simhash(normalized)
        record.text_excerpt = normalized[:280]
    record.image_hash = image_hash


def cluster_exact_source(records):
    groups = defaultdict(list)
    for rec in records:
        if rec.source_kind == "path" and rec.source_exists:
            groups[rec.source].append(rec)
    return {k: v for k, v in groups.items() if len(v) > 1}


def cluster_exact_text(records):
    groups = defaultdict(list)
    for rec in records:
        if rec.text_hash and rec.normalized_text_len >= 80:
            groups[rec.text_hash].append(rec)
    return {k: v for k, v in groups.items() if len(v) > 1}


def cluster_near_text(records, max_distance=6, min_text_len=200):
    candidates = [r for r in records if r.text_simhash and r.normalized_text_len >= min_text_len]
    parents = {id(r): id(r) for r in candidates}
    ref = {id(r): r for r in candidates}

    def find(x):
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parents[rb] = ra

    for a, b in itertools.combinations(candidates, 2):
        if a.source == b.source:
            continue
        if hamming_hex(a.text_simhash, b.text_simhash) <= max_distance:
            union(id(a), id(b))

    groups = defaultdict(list)
    for rec in candidates:
        groups[find(id(rec))].append(rec)
    return [grp for grp in groups.values() if len(grp) > 1]


def cluster_exact_image(records):
    groups = defaultdict(list)
    for rec in records:
        if rec.image_hash:
            groups[rec.image_hash].append(rec)
    return {k: v for k, v in groups.items() if len(v) > 1}


def cluster_near_image(records, max_distance=5):
    candidates = [r for r in records if r.image_hash]
    parents = {id(r): id(r) for r in candidates}

    def find(x):
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parents[rb] = ra

    for a, b in itertools.combinations(candidates, 2):
        if a.source == b.source:
            continue
        if hamming_hex(a.image_hash, b.image_hash) <= max_distance:
            union(id(a), id(b))

    groups = defaultdict(list)
    for rec in candidates:
        groups[find(id(rec))].append(rec)
    return [grp for grp in groups.values() if len(grp) > 1]


def rec_line(rec: ExhibitRecord) -> str:
    return f"- `{rec.exhibit_label}` in `{rec.family_dir}`: [{Path(rec.source).name}]({rec.source})"


def write_markdown(records, exact_source, exact_text, near_text, exact_image, near_image):
    lines = []
    lines.append("# Evidence Binder Duplicate Analysis")
    lines.append("")
    lines.append("This note compares exhibit sources across the evidence binder using exact-source grouping plus text/OCR and image fingerprinting.")
    lines.append("")
    lines.append("Method:")
    lines.append("")
    lines.append("1. parse original `SOURCE FILE` values from exhibit cover pages;")
    lines.append("2. extract text from `.md`, `.txt`, `.eml`, and `.pdf`;")
    lines.append("3. OCR images and image-based PDFs where needed;")
    lines.append("4. compute normalized-text hashes, text simhashes, and image perceptual hashes;")
    lines.append("5. report exact duplicates and likely near duplicates.")
    lines.append("")
    total = len(records)
    real = len([r for r in records if r.source_kind == "path" and r.source_exists])
    lines.append(f"Records analyzed: `{total}`")
    lines.append(f"Existing path-backed exhibit sources analyzed: `{real}`")
    lines.append("")

    lines.append("## 1. Exact Source Reuse")
    lines.append("")
    if not exact_source:
        lines.append("No exact source-path reuse detected.")
    else:
        for source, group in sorted(exact_source.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            lines.append(f"### {Path(source).name}")
            lines.append("")
            lines.append(f"Source: [{source}]({source})")
            lines.append("")
            for rec in group:
                lines.append(f"- `{rec.exhibit_label}` in `{rec.family_dir}`")
            lines.append("")

    lines.append("## 2. Exact Text/OCR Duplicates")
    lines.append("")
    if not exact_text:
        lines.append("No exact normalized-text duplicate groups detected beyond exact source reuse.")
    else:
        for _, group in sorted(exact_text.items(), key=lambda kv: (-len(kv[1]), kv[1][0].source)):
            lines.append(f"### Text group anchored by `{Path(group[0].source).name}`")
            lines.append("")
            for rec in group:
                lines.append(rec_line(rec))
            if group[0].text_excerpt:
                lines.append("")
                lines.append(f"Excerpt: `{group[0].text_excerpt[:220]}`")
            lines.append("")

    lines.append("## 3. Likely Near-Text Duplicates")
    lines.append("")
    if not near_text:
        lines.append("No strong near-text duplicate clusters detected at the current threshold.")
    else:
        for idx, group in enumerate(sorted(near_text, key=lambda g: (-len(g), g[0].source)), start=1):
            lines.append(f"### Near-text cluster {idx}")
            lines.append("")
            for rec in group:
                lines.append(f"{rec_line(rec)}")
                lines.append(f"  - normalized text length: `{rec.normalized_text_len}`")
                lines.append(f"  - text simhash: `{rec.text_simhash}`")
            lines.append("")

    lines.append("## 4. Exact Image Duplicates")
    lines.append("")
    if not exact_image:
        lines.append("No exact image-hash duplicate groups detected.")
    else:
        for _, group in sorted(exact_image.items(), key=lambda kv: (-len(kv[1]), kv[1][0].source)):
            lines.append(f"### Image group anchored by `{Path(group[0].source).name}`")
            lines.append("")
            for rec in group:
                lines.append(rec_line(rec))
            lines.append("")

    lines.append("## 5. Likely Near-Image Duplicates")
    lines.append("")
    if not near_image:
        lines.append("No strong near-image duplicate clusters detected at the current threshold.")
    else:
        for idx, group in enumerate(sorted(near_image, key=lambda g: (-len(g), g[0].source)), start=1):
            lines.append(f"### Near-image cluster {idx}")
            lines.append("")
            for rec in group:
                lines.append(f"{rec_line(rec)}")
                lines.append(f"  - image hash: `{rec.image_hash}`")
            lines.append("")

    lines.append("## 6. Best Practical Use")
    lines.append("")
    lines.append("Use exact-source and exact-text groups as the safest dedup targets first.")
    lines.append("Use near-text and near-image groups as review targets before removing anything.")
    lines.append("Where a duplicate is removed, keep the tab cover page and exhibit cover page and incorporate the master source by reference.")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    records = parse_cover_pages()
    for rec in records:
        analyze_source(rec)

    exact_source = cluster_exact_source(records)
    exact_text = cluster_exact_text(records)
    near_text = cluster_near_text(records)
    exact_image = cluster_exact_image(records)
    near_image = cluster_near_image(records)

    payload = {
        "records": [asdict(r) for r in records],
        "exact_source_groups": {
            source: [asdict(r) for r in group] for source, group in exact_source.items()
        },
        "exact_text_groups": [
            [asdict(r) for r in group] for group in exact_text.values()
        ],
        "near_text_groups": [
            [asdict(r) for r in group] for group in near_text
        ],
        "exact_image_groups": [
            [asdict(r) for r in group] for group in exact_image.values()
        ],
        "near_image_groups": [
            [asdict(r) for r in group] for group in near_image
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_markdown(records, exact_source, exact_text, near_text, exact_image, near_image)
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
