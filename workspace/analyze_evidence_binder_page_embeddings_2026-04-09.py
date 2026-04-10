#!/home/barberb/HACC/.venv/bin/python
import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import fitz
import numpy as np
import pytesseract
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer


ROOT = Path("/home/barberb/HACC")
WORKSPACE = ROOT / "workspace"
PDF_PATH = WORKSPACE / "evidence_binder_full_lean_2026-04-09.pdf"
MANIFEST_PATH = WORKSPACE / "evidence_binder_full_build_2026-04-09" / "manifest.txt"
CACHE_DIR = WORKSPACE / "evidence_binder_page_embedding_analysis_2026-04-09_cache"
PAGE_META_JSON = WORKSPACE / "evidence_binder_page_embedding_analysis_lean_2026-04-09.json"
PAGE_META_MD = WORKSPACE / "evidence_binder_page_embedding_analysis_lean_2026-04-09.md"


@dataclass
class Component:
    family: str
    exhibit_label: str
    component_type: str
    path: str
    page_count: int
    binder_page_start: int
    binder_page_end: int


@dataclass
class PageRecord:
    binder_page: int
    family: str
    exhibit_label: str
    component_type: str
    component_path: str
    page_in_component: int
    text_len: int = 0
    text_hash: Optional[str] = None
    image_hash: Optional[str] = None
    text_excerpt: str = ""
    text_neighbor_page: Optional[int] = None
    text_neighbor_score: Optional[float] = None
    image_neighbor_page: Optional[int] = None
    image_neighbor_score: Optional[float] = None


def normalize_text(text: str) -> str:
    text = text.replace("\x0c", "\n").lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def avg_hash_image(img: Image.Image, size: int = 8) -> str:
    gray = img.convert("L").resize((size, size))
    pixels = np.asarray(gray, dtype=np.float32)
    avg = pixels.mean()
    bits = (pixels >= avg).astype(np.uint8).flatten()
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return f"{value:0{size * size // 4}x}"


def parse_manifest(manifest_path: Path):
    text = manifest_path.read_text(errors="replace").splitlines()
    family = None
    current = None
    entries = []
    for line in text:
        if line.startswith("## "):
            family = line[3:].strip()
            continue
        if line.startswith("- "):
            label = line[2:].strip()
            current = {"family": family, "exhibit_label": label}
            entries.append(current)
            continue
        if current is None:
            continue
        m = re.match(r"\s+(tab|cover|source):\s+(.*)", line)
        if m:
            current[m.group(1)] = m.group(2).strip()
    return entries


def build_components(entries):
    components = []
    page_cursor = 1
    for entry in entries:
        for component_type in ("tab", "cover", "source"):
            path = Path(entry[component_type])
            doc = fitz.open(path)
            page_count = doc.page_count
            doc.close()
            components.append(
                Component(
                    family=entry["family"],
                    exhibit_label=entry["exhibit_label"],
                    component_type=component_type,
                    path=str(path),
                    page_count=page_count,
                    binder_page_start=page_cursor,
                    binder_page_end=page_cursor + page_count - 1,
                )
            )
            page_cursor += page_count
    return components


def render_page_image(doc: fitz.Document, page_index: int, dpi: int = 144) -> Image.Image:
    page = doc.load_page(page_index)
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    mode = "RGB" if pix.n < 4 else "RGBA"
    return Image.frombytes(mode, [pix.width, pix.height], pix.samples)


def extract_page_text(doc: fitz.Document, page_index: int, img: Optional[Image.Image] = None) -> str:
    page = doc.load_page(page_index)
    text = page.get_text("text")
    if len(normalize_text(text)) >= 80:
        return text
    if img is None:
        img = render_page_image(doc, page_index)
    ocr = pytesseract.image_to_string(img)
    if len(normalize_text(ocr)) > len(normalize_text(text)):
        return text + "\n\n[OCR]\n" + ocr
    return text


def source_page_indices(records):
    return [i for i, r in enumerate(records) if r.component_type == "source"]


def cluster_from_neighbors(records, neighbor_info, score_key, min_score):
    parent = {i: i for i in range(len(records))}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, neighbors in neighbor_info.items():
        for j, score in neighbors:
            if score >= min_score:
                union(i, j)

    groups = defaultdict(list)
    for i, rec in enumerate(records):
        groups[find(i)].append(rec)
    return [grp for grp in groups.values() if len(grp) > 1]


def top_neighbor_map_from_embeddings(embeddings, top_k=6):
    sims = embeddings @ embeddings.T
    idxs = np.argsort(-sims, axis=1)[:, :top_k]
    out = defaultdict(list)
    for i in range(len(embeddings)):
        for j in idxs[i]:
            if j < 0 or j == i:
                continue
            score = sims[i, j]
            out[i].append((int(j), float(score)))
    return out


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    entries = parse_manifest(MANIFEST_PATH)
    components = build_components(entries)

    binder = fitz.open(PDF_PATH)
    if binder.page_count != components[-1].binder_page_end:
        raise RuntimeError(f"Binder page count mismatch: pdf={binder.page_count}, manifest={components[-1].binder_page_end}")

    records = []
    for comp in components:
        for offset in range(comp.page_count):
            binder_page = comp.binder_page_start + offset
            page_idx = binder_page - 1
            img = render_page_image(binder, page_idx, dpi=120)
            raw_text = extract_page_text(binder, page_idx, img=img)
            norm_text = normalize_text(raw_text)
            image_hash = avg_hash_image(img)
            records.append(
                PageRecord(
                    binder_page=binder_page,
                    family=comp.family,
                    exhibit_label=comp.exhibit_label,
                    component_type=comp.component_type,
                    component_path=comp.path,
                    page_in_component=offset + 1,
                    text_len=len(norm_text),
                    text_hash=hashlib.sha256(norm_text.encode("utf-8")).hexdigest() if norm_text else None,
                    image_hash=image_hash,
                    text_excerpt=norm_text[:220],
                )
            )

    binder.close()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    text_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    image_model = SentenceTransformer("clip-ViT-B-32", device=device)

    source_idxs = source_page_indices(records)
    source_texts = [records[i].text_excerpt if records[i].text_excerpt else "" for i in source_idxs]
    # Use full normalized text reconstructed from excerpts is not enough; rebuild from cached hashes impossible.
    # For embedding we need page text again from binder pages, so use a second pass from excerpts where excerpt exists.
    # To avoid reopening everything in cache-less form, use excerpt for short pages and render-level similarity via image embeddings.
    # For pages with more text, reopen component page directly.
    full_texts = []
    binder = fitz.open(PDF_PATH)
    for idx in source_idxs:
        page = binder.load_page(records[idx].binder_page - 1)
        text = page.get_text("text")
        if len(normalize_text(text)) < 80:
            img = render_page_image(binder, records[idx].binder_page - 1, dpi=120)
            text = extract_page_text(binder, records[idx].binder_page - 1, img=img)
        full_texts.append(normalize_text(text))
    binder.close()

    text_embeddings = text_model.encode(
        full_texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")

    binder = fitz.open(PDF_PATH)
    source_images = [render_page_image(binder, records[i].binder_page - 1, dpi=120) for i in source_idxs]
    binder.close()
    image_embeddings = image_model.encode(
        source_images,
        batch_size=16,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")

    text_neighbors_local = top_neighbor_map_from_embeddings(text_embeddings, top_k=8)
    image_neighbors_local = top_neighbor_map_from_embeddings(image_embeddings, top_k=8)

    # Write best neighbor onto the page records.
    for local_i, global_i in enumerate(source_idxs):
        if text_neighbors_local.get(local_i):
            nbr_local, score = text_neighbors_local[local_i][0]
            records[global_i].text_neighbor_page = records[source_idxs[nbr_local]].binder_page
            records[global_i].text_neighbor_score = round(score, 4)
        if image_neighbors_local.get(local_i):
            nbr_local, score = image_neighbors_local[local_i][0]
            records[global_i].image_neighbor_page = records[source_idxs[nbr_local]].binder_page
            records[global_i].image_neighbor_score = round(score, 4)

    exact_text_groups = defaultdict(list)
    exact_image_groups = defaultdict(list)
    for i in source_idxs:
        rec = records[i]
        if rec.text_hash and rec.text_len >= 80:
            exact_text_groups[rec.text_hash].append(rec)
        if rec.image_hash:
            exact_image_groups[rec.image_hash].append(rec)
    exact_text_groups = [g for g in exact_text_groups.values() if len(g) > 1]
    exact_image_groups = [g for g in exact_image_groups.values() if len(g) > 1]

    text_cluster_local = cluster_from_neighbors(
        [records[i] for i in source_idxs], text_neighbors_local, "text", 0.985
    )
    image_cluster_local = cluster_from_neighbors(
        [records[i] for i in source_idxs], image_neighbors_local, "image", 0.992
    )

    payload = {
        "pdf_path": str(PDF_PATH),
        "device": device,
        "page_count": len(records),
        "source_page_count": len(source_idxs),
        "components": [asdict(c) for c in components],
        "pages": [asdict(r) for r in records],
        "exact_text_groups": [[asdict(r) for r in grp] for grp in exact_text_groups],
        "exact_image_groups": [[asdict(r) for r in grp] for grp in exact_image_groups],
        "near_text_groups": [[asdict(r) for r in grp] for grp in text_cluster_local],
        "near_image_groups": [[asdict(r) for r in grp] for grp in image_cluster_local],
    }
    PAGE_META_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Evidence Binder Page Embedding Analysis")
    lines.append("")
    lines.append(f"Binder: [{PDF_PATH.name}]({PDF_PATH})")
    lines.append("")
    lines.append(f"Device: `{device}`")
    lines.append(f"Total binder pages scanned: `{len(records)}`")
    lines.append(f"Source pages embedded: `{len(source_idxs)}`")
    lines.append("")
    lines.append("Method:")
    lines.append("")
    lines.append("1. scan the merged binder page-by-page;")
    lines.append("2. map each page back to exhibit/component using the build manifest;")
    lines.append("3. extract page text with PyMuPDF and OCR fallback with Tesseract;")
    lines.append("4. compute text embeddings with `all-MiniLM-L6-v2` on CUDA;")
    lines.append("5. compute image embeddings with `clip-ViT-B-32` on CUDA;")
    lines.append("6. cluster likely duplicates by cosine similarity.")
    lines.append("")

    def emit_groups(title, groups, kind):
        lines.append(f"## {title}")
        lines.append("")
        if not groups:
            lines.append("No groups found.")
            lines.append("")
            return
        for idx, grp in enumerate(sorted(groups, key=lambda g: (-len(g), g[0].binder_page)), start=1):
            lines.append(f"### {kind} cluster {idx}")
            lines.append("")
            for rec in grp:
                lines.append(
                    f"- binder page `{rec.binder_page}`: `{rec.exhibit_label}` / `{rec.component_type}` / `{rec.family}`"
                )
                lines.append(f"  source: `{Path(rec.component_path).name}` page `{rec.page_in_component}`")
                if rec.text_neighbor_score is not None and kind.startswith("near text"):
                    lines.append(f"  top text similarity: `{rec.text_neighbor_score}`")
                if rec.image_neighbor_score is not None and kind.startswith("near image"):
                    lines.append(f"  top image similarity: `{rec.image_neighbor_score}`")
            lines.append("")

    emit_groups("1. Exact Text Page Duplicates", exact_text_groups, "exact text")
    emit_groups("2. Exact Image Page Duplicates", exact_image_groups, "exact image")
    emit_groups("3. Likely Near-Text Page Duplicates", text_cluster_local, "near text")
    emit_groups("4. Likely Near-Image Page Duplicates", image_cluster_local, "near image")
    lines.append("## 5. Use")
    lines.append("")
    lines.append("Use exact groups first for safe deduplication.")
    lines.append("Use near groups as review targets before removing any page or source component.")
    lines.append("When collapsing a duplicate source, keep the tab cover page and exhibit cover page and incorporate the master source by reference.")
    lines.append("")
    PAGE_META_MD.write_text("\n".join(lines), encoding="utf-8")

    print(PAGE_META_MD)
    print(PAGE_META_JSON)


if __name__ == "__main__":
    main()
