#!/usr/bin/env python3
"""Build searchable artifacts for evidence/history using ipfs_datasets_py adapters.

Outputs:
- chunks.jsonl: chunk-level records for keyword and metadata search
- graph.jsonld: JSON-LD graph payload (GraphRAG-ready entity/relationship structure)
- vector/: local vector index artifacts when embedding backend is available
- manifest.json: run summary and artifact pointers
"""

from __future__ import annotations

import argparse
import concurrent.futures
import duckdb
import json
import os
import sys
import re
import shutil
import tempfile
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from hacc_complaint_manager import COMPLAINT_GENERATOR_ROOT, ensure_complaint_generator_on_path

try:
    import numpy as np
except Exception:
    np = None


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT_DIRS = [
    REPO_ROOT / "evidence" / "history",
    REPO_ROOT / "evidence" / "email_imports",
]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "research_results" / "history_index"

# ── PDF text extraction helpers ───────────────────────────────────────────────

def _printable_ratio(text: str) -> float:
    if not text:
        return 0.0
    return sum(1 for c in text if c.isprintable()) / len(text)


def _extract_pdf_text_native(path: Path) -> str:
    """Try native-text extraction with pymupdf; returns '' on failure."""
    try:
        import pymupdf as fitz  # type: ignore
        pages = []
        doc = fitz.open(str(path))
        for page in doc:
            pages.append(page.get_text() or "")
        doc.close()
        return "\n".join(pages)
    except Exception:
        return ""


def _extract_pdf_text_ocr(path: Path) -> str:
    """Render each PDF page to an image and OCR with pytesseract."""
    try:
        import pymupdf as fitz  # type: ignore
        from pytesseract import pytesseract as tess  # type: ignore
        from PIL import Image  # type: ignore
        import io
        pages = []
        doc = fitz.open(str(path))
        for page in doc:
            mat = fitz.Matrix(2.0, 2.0)   # 2× zoom ≈ 144 dpi
            pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
            pages.append(tess.image_to_string(img))
        doc.close()
        return "\n".join(pages)
    except Exception:
        return ""


def _extract_image_text_ocr(path: Path) -> str:
    """OCR a raster image file (JPEG, PNG, TIFF, etc.) with pytesseract."""
    try:
        from pytesseract import pytesseract as tess  # type: ignore
        from PIL import Image  # type: ignore
        img = Image.open(str(path)).convert("RGB")
        return tess.image_to_string(img)
    except Exception:
        return ""


_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif", ".webp"}
_TEXT_SUFFIXES  = {".txt", ".md", ".rst", ".csv", ".json", ".xml", ".html", ".htm",
                   ".log", ".py", ".js", ".ts", ".yaml", ".yml", ".toml"}


def _extract_clean_text(path: Path) -> str:
    """
    Return the best human-readable text for *path*.
    - PDF: try pymupdf native text, fall back to pytesseract OCR.
    - Image (JPEG/PNG/…): pytesseract OCR directly.
    - Text formats: read as UTF-8, gate on printable ratio.
    Returns '' if no usable text is found.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = _extract_pdf_text_native(path)
        if _printable_ratio(text) >= 0.80 and len(text.strip()) >= 50:
            return text
        # Fall back to OCR
        text = _extract_pdf_text_ocr(path)
        if _printable_ratio(text) >= 0.70 and len(text.strip()) >= 20:
            return text
        return ""
    elif suffix in _IMAGE_SUFFIXES:
        text = _extract_image_text_ocr(path)
        if _printable_ratio(text) >= 0.70 and len(text.strip()) >= 20:
            return text
        return ""
    elif suffix in _TEXT_SUFFIXES or not suffix:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            if _printable_ratio(text) >= 0.80:
                return text
        except Exception:
            pass
        return ""
    else:
        # Unknown binary format — skip
        return ""


def _simple_chunk(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split *text* into overlapping chunks of roughly *chunk_size* characters."""
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += max(1, chunk_size - overlap)
    return chunks


def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    if hasattr(value, "as_dict") and callable(getattr(value, "as_dict")):
        return _to_jsonable(value.as_dict())
    if hasattr(value, "dict") and callable(getattr(value, "dict")):
        return _to_jsonable(value.dict())
    if hasattr(value, "__dict__"):
        return _to_jsonable(vars(value))
    return str(value)


def _iter_files(roots: Iterable[Path], max_bytes: int) -> Iterable[Path]:
    seen: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            try:
                if path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            seen.add(resolved)
            yield resolved


def _resolve_source_root(file_path: Path, source_roots: Iterable[Path]) -> Path:
    resolved_file = file_path.resolve()
    for root in source_roots:
        try:
            resolved_file.relative_to(root.resolve())
            return root.resolve()
        except ValueError:
            continue
    return resolved_file.parent


def _common_source_root(paths: Iterable[Path]) -> Path:
    resolved = [str(path.resolve()) for path in paths]
    if not resolved:
        return Path(".").resolve()
    return Path(os.path.commonpath(resolved)).resolve()


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", (text or "").lower())


def _build_local_hash_vector_index(
    *,
    documents: List[Dict[str, Any]],
    output_dir: Path,
    index_name: str,
    dim: int = 128,
) -> Dict[str, Any]:
    if np is None:
        return {
            "status": "unavailable",
            "index_name": index_name,
            "error": "numpy unavailable for local fallback vector index",
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    vectors_path = output_dir / f"{index_name}.vectors.npy"
    records_path = output_dir / f"{index_name}.records.jsonl"
    manifest_path = output_dir / f"{index_name}.manifest.json"

    vectors = np.zeros((len(documents), dim), dtype=np.float32)
    with records_path.open("w", encoding="utf-8") as records_fp:
        for idx, row in enumerate(documents):
            text = str(row.get("text") or "")
            for token in _tokenize(text):
                bucket = hash(token) % dim
                vectors[idx, bucket] += 1.0

            norm = float(np.linalg.norm(vectors[idx]))
            if norm > 0.0:
                vectors[idx] /= norm

            records_fp.write(json.dumps(row, ensure_ascii=False) + "\n")

    np.save(vectors_path, vectors)
    payload = {
        "index_name": index_name,
        "document_count": len(documents),
        "dimension": dim,
        "provider": "local_hashing_fallback",
        "vectors_path": str(vectors_path),
        "records_path": str(records_path),
    }
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["manifest_path"] = str(manifest_path)
    return {
        "status": "success",
        "index_name": index_name,
        "document_count": len(documents),
        "dimension": dim,
        "provider": "local_hashing_fallback",
        "files": {
            "vectors_path": str(vectors_path),
            "records_path": str(records_path),
            "manifest_path": str(manifest_path),
        },
    }


def _graph_jsonld_payload(
    *,
    dataset_id: str,
    generated_at: str,
    source_root: Path,
    entities: List[Dict[str, Any]],
    relationships: List[Dict[str, Any]],
    documents: List[Dict[str, Any]],
) -> Dict[str, Any]:
    node_map = []
    for entity in entities:
        entity_id = str(entity.get("entity_id") or entity.get("id") or "")
        if not entity_id:
            continue
        entity_type = str(entity.get("entity_type") or "Entity")
        node_map.append(
            {
                "@id": entity_id,
                "@type": entity_type,
                "name": entity.get("name") or "",
                "confidence": entity.get("confidence"),
                "attributes": entity.get("attributes") or {},
            }
        )

    edge_map = []
    for rel in relationships:
        rel_id = str(rel.get("relationship_id") or rel.get("id") or "")
        source_id = str(rel.get("source_id") or "")
        target_id = str(rel.get("target_id") or "")
        if not rel_id or not source_id or not target_id:
            continue
        edge_map.append(
            {
                "@id": rel_id,
                "@type": str(rel.get("relation_type") or "related_to"),
                "source": source_id,
                "target": target_id,
                "confidence": rel.get("confidence"),
                "attributes": rel.get("attributes") or {},
            }
        )

    return {
        "@context": {
            "@vocab": "https://schema.org/",
            "source": "https://schema.org/isBasedOn",
            "target": "https://schema.org/about",
            "confidence": "https://schema.org/confidence",
            "attributes": "https://schema.org/additionalProperty",
            "documents": "https://schema.org/hasPart",
            "nodes": "https://schema.org/Thing",
            "edges": "https://schema.org/Action",
        },
        "@id": dataset_id,
        "@type": "Dataset",
        "name": "HACC evidence/history GraphRAG index",
        "dateModified": generated_at,
        "sourceRoot": str(source_root),
        "documents": documents,
        "nodes": node_map,
        "edges": edge_map,
    }


def _write_duckdb_index(
    *,
    output_root: Path,
    document_rows: list[dict[str, Any]],
    chunk_rows: list[dict[str, Any]],
    entity_rows: list[dict[str, Any]],
    relationship_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    db_path = output_root / "evidence_index.duckdb"
    con = duckdb.connect(str(db_path))
    try:
        con.execute("DROP TABLE IF EXISTS documents")
        con.execute("DROP TABLE IF EXISTS chunks")
        con.execute("DROP TABLE IF EXISTS entities")
        con.execute("DROP TABLE IF EXISTS relationships")

        con.execute(
            """
            CREATE TABLE documents (
                doc_id VARCHAR,
                relative_path VARCHAR,
                absolute_path VARCHAR,
                status VARCHAR,
                text_length BIGINT,
                chunk_count BIGINT,
                metadata_json VARCHAR
            )
            """
        )
        if document_rows:
            con.executemany(
                "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        str(row.get("doc_id") or ""),
                        str(row.get("relative_path") or ""),
                        str(row.get("absolute_path") or ""),
                        str(row.get("status") or ""),
                        int(row.get("text_length") or 0),
                        int(row.get("chunk_count") or 0),
                        json.dumps(row.get("metadata") or {}, ensure_ascii=False),
                    )
                    for row in document_rows
                ],
            )

        con.execute(
            """
            CREATE TABLE chunks (
                chunk_id VARCHAR,
                doc_id VARCHAR,
                chunk_index BIGINT,
                text VARCHAR,
                metadata_json VARCHAR
            )
            """
        )
        if chunk_rows:
            con.executemany(
                "INSERT INTO chunks VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        str(row.get("id") or ""),
                        str(row.get("doc_id") or ""),
                        int(row.get("chunk_index") or 0),
                        str(row.get("text") or ""),
                        json.dumps(row.get("metadata") or {}, ensure_ascii=False),
                    )
                    for row in chunk_rows
                ],
            )

        con.execute(
            """
            CREATE TABLE entities (
                entity_id VARCHAR,
                entity_type VARCHAR,
                name VARCHAR,
                confidence DOUBLE,
                attributes_json VARCHAR,
                raw_json VARCHAR
            )
            """
        )
        if entity_rows:
            con.executemany(
                "INSERT INTO entities VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        str(row.get("entity_id") or row.get("id") or ""),
                        str(row.get("entity_type") or ""),
                        str(row.get("name") or ""),
                        float(row.get("confidence") or 0.0),
                        json.dumps(row.get("attributes") or {}, ensure_ascii=False),
                        json.dumps(row, ensure_ascii=False),
                    )
                    for row in entity_rows
                ],
            )

        con.execute(
            """
            CREATE TABLE relationships (
                relationship_id VARCHAR,
                source_id VARCHAR,
                target_id VARCHAR,
                relation_type VARCHAR,
                confidence DOUBLE,
                attributes_json VARCHAR,
                raw_json VARCHAR
            )
            """
        )
        if relationship_rows:
            con.executemany(
                "INSERT INTO relationships VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        str(row.get("relationship_id") or row.get("id") or ""),
                        str(row.get("source_id") or ""),
                        str(row.get("target_id") or ""),
                        str(row.get("relation_type") or ""),
                        float(row.get("confidence") or 0.0),
                        json.dumps(row.get("attributes") or {}, ensure_ascii=False),
                        json.dumps(row, ensure_ascii=False),
                    )
                    for row in relationship_rows
                ],
            )

        con.execute("CREATE INDEX IF NOT EXISTS idx_documents_doc_id ON documents(doc_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_entities_entity_id ON entities(entity_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_relationships_relationship_id ON relationships(relationship_id)")
    finally:
        con.close()

    return {
        "duckdb_path": str(db_path),
        "document_count": len(document_rows),
        "chunk_count": len(chunk_rows),
        "entity_count": len(entity_rows),
        "relationship_count": len(relationship_rows),
    }


def _run_vector_preflight(
    *,
    create_vector_index: Any,
    embeddings_backend_status: Any,
    vector_index_backend_status: Any,
    batch_size: int,
    vector_provider: str,
    vector_model: str,
    vector_device: str,
    embedding_batch_size: int,
    embedding_num_workers: int,
    run_smoke_test: bool,
) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "status": "unknown",
        "checks": {},
    }

    emb_status = _to_jsonable(embeddings_backend_status(perform_probe=True))
    vec_status = _to_jsonable(vector_index_backend_status(require_local_persistence=True))

    report["checks"]["embeddings_backend_status"] = emb_status
    report["checks"]["vector_index_backend_status"] = vec_status

    smoke_status: Dict[str, Any] = {
        "status": "skipped" if not run_smoke_test else "pending"
    }
    smoke_ok = True
    if run_smoke_test:
        tmp_dir = Path(tempfile.mkdtemp(prefix="history_vector_preflight_"))
        try:
            smoke_docs = [
                {
                    "id": "preflight-1",
                    "text": "Tenant complaint evidence timeline and lease-related correspondence.",
                    "metadata": {"source": "preflight"},
                },
                {
                    "id": "preflight-2",
                    "text": "Housing policy violation allegations and supporting document summary.",
                    "metadata": {"source": "preflight"},
                },
            ]
            smoke_result = _to_jsonable(
                create_vector_index(
                    smoke_docs,
                    index_name="vector_preflight",
                    output_dir=str(tmp_dir),
                    batch_size=max(1, int(batch_size)),
                    provider=(vector_provider or None),
                    model_name=(vector_model or None),
                    device=(None if vector_device == "auto" else vector_device),
                    embedding_batch_size=max(1, int(embedding_batch_size)),
                    embedding_num_workers=max(0, int(embedding_num_workers)),
                )
            )
            smoke_status = {
                "status": str(smoke_result.get("status") or "unknown"),
                "error": smoke_result.get("error") or "",
                "provider": smoke_result.get("provider") or "",
                "dimension": smoke_result.get("dimension") or 0,
                "metadata": smoke_result.get("metadata") or {},
            }
            smoke_ok = smoke_status["status"] == "success"
        except Exception as exc:
            smoke_status = {"status": "error", "error": str(exc)}
            smoke_ok = False
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    report["checks"]["smoke_test_vector_index"] = smoke_status

    emb_ok = str(emb_status.get("status") or "").lower() in {"available", "degraded"}
    vec_ok = str(vec_status.get("status") or "").lower() == "available"
    healthy = emb_ok and vec_ok and smoke_ok
    report["status"] = "healthy" if healthy else "unhealthy"
    return report


def _process_single_file(
    *,
    source_root: Path,
    output_root: Path,
    file_path: Path,
    file_index: int,
    chunk_size: int,
    overlap: int,
) -> Dict[str, Any]:
    from integrations.ipfs_datasets.documents import ingest_local_document
    from integrations.ipfs_datasets.graphs import extract_graph_from_text

    rel_path = str(file_path.relative_to(source_root))
    doc_id = f"doc:{file_index}:{rel_path}"
    parsed_dir = output_root / "parsed" / f"doc_{file_index:06d}"

    try:
        parsed = ingest_local_document(
            file_path,
            metadata={"source_path": str(file_path), "relative_path": rel_path},
            output_dir=str(parsed_dir),
            chunk_size=chunk_size,
            overlap=overlap,
        )
    except Exception as exc:
        return {
            "file_index": file_index,
            "failure": {"path": rel_path, "error": str(exc)},
            "document_row": None,
            "chunks": [],
            "entities": [],
            "relationships": [],
        }

    parsed = _to_jsonable(parsed)
    parse_status = str(parsed.get("status") or "")
    parse_payload = parsed.get("parse") if isinstance(parsed.get("parse"), dict) else {}
    text = str(parsed.get("text") or parse_payload.get("text") or "").strip()
    chunks = parse_payload.get("chunks") if isinstance(parse_payload.get("chunks"), list) else []

    # ── OCR fallback: if text is binary/empty, extract clean text ourselves ──
    using_clean_text = False
    if _printable_ratio(text) < 0.80 or len(text.strip()) < 50:
        clean = _extract_clean_text(file_path)
        if len(clean.strip()) >= 50:
            text = clean
            using_clean_text = True
            chunks = []  # will rebuild below

    document_row = {
        "doc_id": doc_id,
        "relative_path": rel_path,
        "absolute_path": str(file_path),
        "status": parse_status,
        "text_length": len(text),
        "chunk_count": len(chunks),
        "metadata": parsed.get("metadata") or {},
    }

    chunk_records: List[Dict[str, Any]] = []
    if text:
        # When using clean text extraction (OCR/pdfplumber), build chunks ourselves.
        if using_clean_text or not chunks:
            raw_chunks = _simple_chunk(text, chunk_size=chunk_size, overlap=overlap)
            for chunk_index, chunk_text in enumerate(raw_chunks):
                chunk_text = chunk_text.strip()
                if not chunk_text:
                    continue
                chunk_id = f"{doc_id}:chunk:{chunk_index}"
                chunk_records.append(
                    {
                        "id": chunk_id,
                        "doc_id": doc_id,
                        "chunk_index": chunk_index,
                        "text": chunk_text,
                        "metadata": {
                            "relative_path": rel_path,
                            "absolute_path": str(file_path),
                            "start_pos": None,
                            "end_pos": None,
                            "length": len(chunk_text),
                            "ocr_extracted": using_clean_text,
                        },
                    }
                )
        elif isinstance(chunks, list):
            for chunk_index, chunk in enumerate(chunks):
                chunk = _to_jsonable(chunk)
                chunk_text = str(chunk.get("text") or "").strip()
                if not chunk_text:
                    continue
                chunk_id = f"{doc_id}:chunk:{chunk_index}"
                chunk_records.append(
                    {
                        "id": chunk_id,
                        "doc_id": doc_id,
                        "chunk_index": chunk_index,
                        "text": chunk_text,
                        "metadata": {
                            "relative_path": rel_path,
                            "absolute_path": str(file_path),
                            "start_pos": chunk.get("start_pos"),
                            "end_pos": chunk.get("end_pos"),
                            "length": chunk.get("length") or len(chunk_text),
                            "ocr_extracted": False,
                        },
                    }
                )

    entities: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []
    if text:
        graph_payload = _to_jsonable(
            extract_graph_from_text(
                text,
                source_id=doc_id,
                metadata={
                    "artifact_id": doc_id,
                    "relative_path": rel_path,
                    "absolute_path": str(file_path),
                },
            )
        )
        for entity in graph_payload.get("entities") or []:
            entities.append(_to_jsonable(entity))
        for relationship in graph_payload.get("relationships") or []:
            relationships.append(_to_jsonable(relationship))

    return {
        "file_index": file_index,
        "failure": None,
        "document_row": document_row,
        "chunks": chunk_records,
        "entities": entities,
        "relationships": relationships,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Index evidence/history into JSONL, JSON-LD, and vector artifacts using ipfs_datasets_py"
    )
    parser.add_argument(
        "--input-dir",
        action="append",
        default=None,
        help="Directory to index. Repeat to include multiple roots. Defaults to evidence/history and evidence/email_imports.",
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Artifact output directory")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Text chunk size")
    parser.add_argument("--overlap", type=int, default=120, help="Chunk overlap")
    parser.add_argument("--max-bytes", type=int, default=25_000_000, help="Skip files larger than this")
    parser.add_argument("--index-name", default="evidence_history", help="Vector index name")
    parser.add_argument("--batch-size", type=int, default=32, help="Embedding batch size")
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, min(8, (os.cpu_count() or 1))),
        help="Parallel workers for document ingest/graph extraction",
    )
    parser.add_argument(
        "--cpu-worker-backend",
        choices=["thread", "process"],
        default="process",
        help="Execution backend for CPU workers",
    )
    parser.add_argument(
        "--vector-provider",
        default="",
        help="Embedding provider override (e.g. adapter, openrouter, hf_inference)",
    )
    parser.add_argument(
        "--vector-model",
        default="",
        help="Embedding model override",
    )
    parser.add_argument(
        "--vector-device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Embedding device preference",
    )
    parser.add_argument(
        "--embedding-batch-size",
        type=int,
        default=32,
        help="Provider-level embedding micro-batch size",
    )
    parser.add_argument(
        "--embedding-num-workers",
        type=int,
        default=0,
        help="Tokenizer worker hint for HF backend",
    )
    parser.add_argument(
        "--skip-vector-preflight",
        action="store_true",
        help="Skip vector backend preflight checks before indexing",
    )
    parser.add_argument(
        "--skip-vector-preflight-smoke-test",
        action="store_true",
        help="Skip the smoke-test vector generation in preflight",
    )
    parser.add_argument(
        "--preflight-report-path",
        default="",
        help="Optional path to write vector preflight JSON report",
    )
    args = parser.parse_args()

    input_dir_values = list(args.input_dir or [str(path) for path in DEFAULT_INPUT_DIRS])
    source_roots = [Path(value).expanduser().resolve() for value in input_dir_values]
    output_root = Path(args.output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    existing_source_roots = [path for path in source_roots if path.exists()]
    if not existing_source_roots:
        print(
            f"No input directories exist: {', '.join(str(path) for path in source_roots)}",
            file=sys.stderr,
        )
        return 2

    if COMPLAINT_GENERATOR_ROOT.exists():
        ensure_complaint_generator_on_path()
    else:
        print(f"complaint-generator root not found: {COMPLAINT_GENERATOR_ROOT}", file=sys.stderr)
        return 2

    from integrations.ipfs_datasets.vector_store import (
        create_vector_index,
        embeddings_backend_status,
        vector_index_backend_status,
    )

    graph_source_root = _common_source_root(existing_source_roots)

    generated_at = datetime.now(timezone.utc).isoformat()
    chunks_path = output_root / "chunks.jsonl"
    graph_path = output_root / "graph.jsonld"
    vector_status_path = output_root / "vector_status.json"
    preflight_path = output_root / "vector_preflight.json"
    duckdb_status_path = output_root / "duckdb_status.json"
    manifest_path = output_root / "manifest.json"

    preflight_result: Dict[str, Any] = {"status": "skipped"}
    if not args.skip_vector_preflight:
        preflight_result = _run_vector_preflight(
            create_vector_index=create_vector_index,
            embeddings_backend_status=embeddings_backend_status,
            vector_index_backend_status=vector_index_backend_status,
            batch_size=args.batch_size,
            vector_provider=args.vector_provider,
            vector_model=args.vector_model,
            vector_device=args.vector_device,
            embedding_batch_size=args.embedding_batch_size,
            embedding_num_workers=args.embedding_num_workers,
            run_smoke_test=not args.skip_vector_preflight_smoke_test,
        )

        report_path = (
            Path(args.preflight_report_path).expanduser().resolve()
            if args.preflight_report_path
            else preflight_path
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(preflight_result, indent=2, ensure_ascii=False), encoding="utf-8")

        if preflight_result.get("status") != "healthy":
            print(
                json.dumps(
                    {
                        "status": "error",
                        "reason": "vector_preflight_failed",
                        "preflight_report": str(report_path),
                        "preflight": preflight_result,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 3

    vector_docs: List[Dict[str, Any]] = []
    document_rows: List[Dict[str, Any]] = []
    entities_by_id: Dict[str, Dict[str, Any]] = {}
    relationships_by_id: Dict[str, Dict[str, Any]] = {}
    failures: List[Dict[str, Any]] = []

    file_paths = list(_iter_files(existing_source_roots, args.max_bytes))

    cpu_workers = max(1, int(args.workers))
    results_by_index: Dict[int, Dict[str, Any]] = {}

    if cpu_workers == 1:
        for file_index, file_path in enumerate(file_paths):
            results_by_index[file_index] = _process_single_file(
                source_root=_resolve_source_root(file_path, existing_source_roots),
                output_root=output_root,
                file_path=file_path,
                file_index=file_index,
                chunk_size=args.chunk_size,
                overlap=args.overlap,
            )
    else:
        executor_cls = (
            concurrent.futures.ProcessPoolExecutor
            if args.cpu_worker_backend == "process"
            else concurrent.futures.ThreadPoolExecutor
        )
        with executor_cls(max_workers=cpu_workers) as executor:
            future_map = {
                executor.submit(
                    _process_single_file,
                    source_root=_resolve_source_root(file_path, existing_source_roots),
                    output_root=output_root,
                    file_path=file_path,
                    file_index=file_index,
                    chunk_size=args.chunk_size,
                    overlap=args.overlap,
                ): file_index
                for file_index, file_path in enumerate(file_paths)
            }
            for future in concurrent.futures.as_completed(future_map):
                file_index = future_map[future]
                try:
                    results_by_index[file_index] = future.result()
                except Exception as exc:
                    source_root = _resolve_source_root(file_paths[file_index], existing_source_roots)
                    rel_path = str(file_paths[file_index].relative_to(source_root))
                    results_by_index[file_index] = {
                        "file_index": file_index,
                        "failure": {"path": rel_path, "error": str(exc)},
                        "document_row": None,
                        "chunks": [],
                        "entities": [],
                        "relationships": [],
                    }

    with chunks_path.open("w", encoding="utf-8") as chunks_fp:
        for file_index in range(len(file_paths)):
            result = results_by_index.get(file_index)
            if not result:
                continue

            failure = result.get("failure")
            if isinstance(failure, dict):
                failures.append(failure)
                continue

            document_row = result.get("document_row")
            if isinstance(document_row, dict):
                document_rows.append(document_row)

            for record in result.get("chunks") or []:
                chunks_fp.write(json.dumps(record, ensure_ascii=False) + "\n")
                vector_docs.append(record)

            for entity in result.get("entities") or []:
                entity_obj = _to_jsonable(entity)
                entity_id = str(entity_obj.get("entity_id") or entity_obj.get("id") or "")
                if entity_id and entity_id not in entities_by_id:
                    entities_by_id[entity_id] = entity_obj

            for relationship in result.get("relationships") or []:
                rel_obj = _to_jsonable(relationship)
                rel_id = str(rel_obj.get("relationship_id") or rel_obj.get("id") or "")
                if rel_id and rel_id not in relationships_by_id:
                    relationships_by_id[rel_id] = rel_obj

    graph_payload = _graph_jsonld_payload(
        dataset_id="urn:hacc:evidence-history:index",
        generated_at=generated_at,
        source_root=graph_source_root,
        entities=list(entities_by_id.values()),
        relationships=list(relationships_by_id.values()),
        documents=document_rows,
    )
    graph_path.write_text(json.dumps(graph_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    duckdb_result = _write_duckdb_index(
        output_root=output_root / "duckdb",
        document_rows=document_rows,
        chunk_rows=vector_docs,
        entity_rows=list(entities_by_id.values()),
        relationship_rows=list(relationships_by_id.values()),
    )
    duckdb_status_path.write_text(json.dumps(duckdb_result, indent=2, ensure_ascii=False), encoding="utf-8")

    vector_result = _to_jsonable(
        create_vector_index(
            vector_docs,
            index_name=args.index_name,
            output_dir=str(output_root / "vector"),
            batch_size=args.batch_size,
            provider=(args.vector_provider or None),
            model_name=(args.vector_model or None),
            device=(None if args.vector_device == "auto" else args.vector_device),
            embedding_batch_size=max(1, int(args.embedding_batch_size)),
            embedding_num_workers=max(0, int(args.embedding_num_workers)),
        )
    )
    if str(vector_result.get("status") or "") != "success":
        fallback_result = _build_local_hash_vector_index(
            documents=vector_docs,
            output_dir=output_root / "vector",
            index_name=f"{args.index_name}_fallback",
            dim=128,
        )
        vector_result = {
            "status": "fallback_success" if fallback_result.get("status") == "success" else "error",
            "primary": vector_result,
            "fallback": fallback_result,
        }
    vector_status_path.write_text(json.dumps(vector_result, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest = {
        "status": "success",
        "generated_at": generated_at,
        "input_dirs": [str(path) for path in existing_source_roots],
        "output_dir": str(output_root),
        "files_scanned": len(file_paths),
        "documents_indexed": len(document_rows),
        "chunk_records": len(vector_docs),
        "entities": len(entities_by_id),
        "relationships": len(relationships_by_id),
        "failures": failures,
        "artifacts": {
            "chunks_jsonl": str(chunks_path),
            "graph_jsonld": str(graph_path),
            "duckdb_status": str(duckdb_status_path),
            "vector_status": str(vector_status_path),
            "vector_preflight": str(preflight_path),
            "manifest": str(manifest_path),
        },
        "duckdb_index": duckdb_result,
        "vector_preflight": preflight_result,
        "vector_index": vector_result,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": "success",
        "manifest": str(manifest_path),
        "chunk_records": len(vector_docs),
        "documents_indexed": len(document_rows),
        "entities": len(entities_by_id),
        "relationships": len(relationships_by_id),
        "duckdb_path": duckdb_result.get("duckdb_path"),
        "vector_status": vector_result.get("status"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
