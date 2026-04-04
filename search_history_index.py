#!/usr/bin/env python3
"""
Semantic search over the HACC evidence history vector index.

Usage:
    python search_history_index.py "housing discrimination" [--top-k 10] [--index-dir PATH]

The script embeds the query with the same model used to build the index
(sentence-transformers/all-MiniLM-L6-v2 via the ipfs_datasets_py adapter),
then returns the top-k most similar chunks by cosine similarity.
"""
import sys
import os
import json
import argparse
import textwrap

# ── resolve venv before importing heavy deps ─────────────────────────────────
_VENV = os.path.join(os.path.dirname(__file__), ".venv")
if os.path.isdir(_VENV):
    _site = os.path.join(_VENV, "lib")
    for _d in os.listdir(_site):
        _sp = os.path.join(_site, _d, "site-packages")
        if os.path.isdir(_sp) and _sp not in sys.path:
            sys.path.insert(0, _sp)

import numpy as np

_DEFAULT_INDEX = os.path.join(
    os.path.dirname(__file__),
    "research_results", "history_index_v8",
)


def _load_embed_fn():
    """Import embed_text from the local ipfs_datasets_py installation."""
    _pkg_root = os.path.join(os.path.dirname(__file__), "complaint-generator",
                             "ipfs_datasets_py")
    if _pkg_root not in sys.path:
        sys.path.insert(0, _pkg_root)
    from ipfs_datasets_py.embeddings_router import embed_text  # type: ignore
    return embed_text


def embed_query(text: str) -> np.ndarray:
    """Return a unit-normalised 384-dim embedding for *text*."""
    embed_text = _load_embed_fn()
    vec = embed_text(text)
    arr = np.asarray(vec, dtype=np.float32)
    norm = np.linalg.norm(arr)
    if norm > 0:
        arr = arr / norm
    return arr


def load_index(index_dir: str):
    """Load the vector matrix and records from *index_dir*."""
    vdir = os.path.join(index_dir, "vector")
    vectors_path = os.path.join(vdir, "evidence_history.vectors.npy")
    records_path = os.path.join(vdir, "evidence_history.records.jsonl")

    if not os.path.isfile(vectors_path):
        sys.exit(f"[error] Vector file not found: {vectors_path}")
    if not os.path.isfile(records_path):
        sys.exit(f"[error] Records file not found: {records_path}")

    print(f"Loading vectors from {vectors_path} …", file=sys.stderr, flush=True)
    vectors = np.load(vectors_path)  # shape [N, 384]

    # Unit-normalise each row so dot product == cosine similarity
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    vectors = vectors / norms

    print(f"Loading {vectors.shape[0]:,} records …", file=sys.stderr, flush=True)
    records = []
    with open(records_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    assert len(records) == vectors.shape[0], (
        f"Mismatch: {len(records)} records vs {vectors.shape[0]} vectors"
    )
    return vectors, records


def search(query: str, vectors: np.ndarray, records: list, top_k: int = 10):
    """Return top_k (score, record) pairs for *query*."""
    q = embed_query(query)  # [384]
    scores = vectors @ q    # [N]  cosine similarity
    idx = np.argpartition(scores, -top_k)[-top_k:]
    idx = idx[np.argsort(scores[idx])[::-1]]
    return [(float(scores[i]), records[i]) for i in idx]


def _truncate(text: str, width: int = 300) -> str:
    text = " ".join(text.split())   # collapse whitespace
    if len(text) > width:
        text = text[:width] + " …"
    return text


def _is_printable(text: str) -> bool:
    printable = sum(1 for c in text if c.isprintable())
    return printable / max(len(text), 1) > 0.7


def print_results(results: list, query: str, show_text: bool = True):
    print(f"\nQuery: {query!r}\n{'─'*70}")
    for rank, (score, rec) in enumerate(results, 1):
        meta = rec.get("metadata", {})
        path = meta.get("relative_path", rec.get("id", "?"))
        text = rec.get("text", "")
        print(f"\n#{rank}  score={score:.4f}  {path}")
        if show_text:
            if _is_printable(text):
                print(textwrap.fill(_truncate(text), width=90, initial_indent="    ",
                                    subsequent_indent="    "))
            else:
                print("    [binary/non-printable content]")


def main():
    parser = argparse.ArgumentParser(
        description="Semantic search over the HACC evidence history index",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(__doc__),
    )
    parser.add_argument("query", nargs="+", help="Search query (free text)")
    parser.add_argument("--top-k", type=int, default=10, metavar="N",
                        help="Number of results to return (default: 10)")
    parser.add_argument("--index-dir", default=_DEFAULT_INDEX, metavar="PATH",
                        help=f"Path to index directory (default: {_DEFAULT_INDEX})")
    parser.add_argument("--no-text", action="store_true",
                        help="Suppress chunk text in output")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON array")
    args = parser.parse_args()

    query = " ".join(args.query)
    vectors, records = load_index(args.index_dir)
    results = search(query, vectors, records, top_k=args.top_k)

    if args.json:
        out = [{"rank": i+1, "score": s, "id": r["id"],
                "path": r.get("metadata", {}).get("relative_path", ""),
                "text": r.get("text", "") if _is_printable(r.get("text","")) else "[binary]"}
               for i, (s, r) in enumerate(results)]
        print(json.dumps(out, indent=2))
    else:
        print_results(results, query, show_text=not args.no_text)


if __name__ == "__main__":
    main()
