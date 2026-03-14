from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if COMPLAINT_GENERATOR_ROOT.exists():
    complaint_generator_path = str(COMPLAINT_GENERATOR_ROOT)
    if complaint_generator_path not in sys.path:
        sys.path.insert(0, complaint_generator_path)

try:
    from integrations.ipfs_datasets import scrape_web_content, search_brave_web, search_multi_engine_web
    from integrations.ipfs_datasets.graphs import extract_graph_from_text
except Exception as exc:  # pragma: no cover - exercised through fallback behavior
    scrape_web_content = None
    search_brave_web = None
    search_multi_engine_web = None
    extract_graph_from_text = None
    INTEGRATION_IMPORT_ERROR = str(exc)
else:
    INTEGRATION_IMPORT_ERROR = None


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _semantic_token(token: str) -> str:
    normalized = token.lower().strip()
    if not normalized:
        return ""

    canonical_map = {
        "complained": "complain",
        "complaint": "complain",
        "complaints": "complain",
        "engaged": "engage",
        "engaging": "engage",
        "files": "file",
        "filed": "file",
        "filing": "file",
        "policies": "policy",
        "rules": "rule",
    }
    if normalized in canonical_map:
        return canonical_map[normalized]

    for suffix in ("ing", "ed", "es", "s"):
        if normalized.endswith(suffix) and len(normalized) > len(suffix) + 2:
            return normalized[: -len(suffix)]
    return normalized


def _semantic_tokens(value: str) -> set[str]:
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "of",
        "on",
        "or",
        "that",
        "the",
        "to",
        "with",
    }
    return {
        normalized
        for normalized in (_semantic_token(token) for token in re.findall(r"[a-z0-9]+", value.lower()))
        if normalized and normalized not in stopwords
    }


def _sentence_split(text: str) -> List[str]:
    cleaned = _clean_text(text)
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+|\n+", cleaned)
    return [_clean_text(part) for part in parts if _clean_text(part)]


def _normalize_domain(value: str) -> str:
    parsed = urlparse(value or "")
    return (parsed.netloc or parsed.path or "").lower()


def _safe_json_load(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


@dataclass
class CorpusDocument:
    document_id: str
    title: str
    text: str
    source_type: str
    source_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    title_tokens: set[str] = field(init=False, repr=False)
    text_tokens: set[str] = field(init=False, repr=False)
    entity_tokens: set[str] = field(init=False, repr=False)
    rule_tokens: set[str] = field(init=False, repr=False)
    title_lower: str = field(init=False, repr=False)
    text_lower: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.title = _clean_text(self.title) or self.document_id
        self.text = str(self.text or "")
        self.source_type = str(self.source_type or "document")
        self.source_path = str(self.source_path or "")
        self.title_lower = self.title.lower()
        self.text_lower = self.text.lower()
        self.title_tokens = _semantic_tokens(self.title)
        self.text_tokens = _semantic_tokens(self.text)
        self.entity_tokens = _semantic_tokens(" ".join(str(entity.get("name") or "") for entity in self.entities))
        self.rule_tokens = _semantic_tokens(" ".join(str(rule.get("text") or "") for rule in self.rules))

    def summary(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "source_type": self.source_type,
            "source_path": self.source_path,
            "text_length": len(self.text),
            "rule_count": len(self.rules),
            "entity_count": len(self.entities),
            "relationship_count": len(self.relationships),
            "metadata": dict(self.metadata),
        }


class HACCResearchEngine:
    def __init__(
        self,
        *,
        repo_root: Optional[Path | str] = None,
        parsed_dir: Optional[Path | str] = None,
        parse_manifest_path: Optional[Path | str] = None,
        knowledge_graph_dir: Optional[Path | str] = None,
    ) -> None:
        self.repo_root = Path(repo_root or REPO_ROOT).resolve()
        self.parsed_dir = Path(parsed_dir or (self.repo_root / "research_results/documents/parsed")).resolve()
        self.parse_manifest_path = Path(
            parse_manifest_path or (self.repo_root / "research_results/documents/parse_manifest.json")
        ).resolve()
        self.knowledge_graph_dir = Path(
            knowledge_graph_dir or (self.repo_root / "hacc_website/knowledge_graph")
        ).resolve()
        self._documents: Optional[List[CorpusDocument]] = None

    def load_corpus(self, *, force_reload: bool = False) -> List[CorpusDocument]:
        if self._documents is not None and not force_reload:
            return list(self._documents)

        documents = []
        documents.extend(self._load_parsed_documents())
        documents.extend(self._load_knowledge_graph_documents())
        self._documents = documents
        return list(documents)

    def build_index(self, output_path: Optional[Path | str] = None) -> Dict[str, Any]:
        documents = self.load_corpus()
        payload = {
            "status": "success",
            "document_count": len(documents),
            "source_counts": self._source_counts(documents),
            "knowledge_graph_dir": str(self.knowledge_graph_dir),
            "parsed_dir": str(self.parsed_dir),
            "documents": [document.summary() for document in documents],
            "integration_status": self._integration_status(),
        }
        if output_path:
            output = Path(output_path).resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            payload["output_path"] = str(output)
        return payload

    def search_local(
        self,
        query: str,
        *,
        top_k: int = 10,
        source_types: Optional[Sequence[str]] = None,
        min_score: float = 0.0,
    ) -> Dict[str, Any]:
        query_text = _clean_text(query)
        query_tokens = _semantic_tokens(query_text)
        documents = self.load_corpus()
        allowed_types = {value.lower() for value in source_types or []}

        ranked_results = []
        for document in documents:
            if allowed_types and document.source_type.lower() not in allowed_types:
                continue
            score, matched_rules, matched_entities = self._score_document(
                query_text=query_text,
                query_tokens=query_tokens,
                document=document,
            )
            if score < min_score:
                continue
            ranked_results.append(
                {
                    "document_id": document.document_id,
                    "title": document.title,
                    "score": round(score, 4),
                    "source_type": document.source_type,
                    "source_path": document.source_path,
                    "snippet": self._extract_snippet(query_text, query_tokens, document, matched_rules),
                    "matched_rules": matched_rules[:3],
                    "matched_entities": matched_entities[:5],
                    "metadata": dict(document.metadata),
                }
            )

        ranked_results.sort(key=lambda item: (-float(item["score"]), item["title"]))
        return {
            "status": "success",
            "query": query_text,
            "document_count": len(documents),
            "returned_result_count": min(top_k, len(ranked_results)),
            "results": ranked_results[:top_k],
            "integration_status": self._integration_status(),
        }

    def discover(
        self,
        query: str,
        *,
        max_results: int = 10,
        engines: Optional[List[str]] = None,
        domain_filter: Optional[Sequence[str] | str] = None,
        scrape: bool = False,
    ) -> Dict[str, Any]:
        query_text = _clean_text(query)
        if search_multi_engine_web is None and search_brave_web is None:
            return {
                "status": "unavailable",
                "query": query_text,
                "results": [],
                "error": INTEGRATION_IMPORT_ERROR or "ipfs_datasets search adapter unavailable",
            }

        if search_multi_engine_web is not None:
            results = search_multi_engine_web(query_text, max_results=max_results, engines=engines)
        else:
            results = search_brave_web(query_text, max_results=max_results)

        normalized_filters = self._normalize_domain_filters(domain_filter)
        if normalized_filters:
            results = [item for item in results if self._matches_domain_filter(item, normalized_filters)]

        if scrape and scrape_web_content is not None:
            for item in results[: min(len(results), 5)]:
                scraped = scrape_web_content(str(item.get("url") or ""))
                item["scrape"] = {
                    "success": bool(scraped.get("success", False)),
                    "errors": list(scraped.get("errors", []) or []),
                    "content_preview": str(scraped.get("content", "") or "")[:500],
                }

        return {
            "status": "success",
            "query": query_text,
            "result_count": len(results),
            "results": results[:max_results],
            "integration_status": self._integration_status(),
        }

    def research(
        self,
        query: str,
        *,
        local_top_k: int = 10,
        web_max_results: int = 10,
        engines: Optional[List[str]] = None,
        domain_filter: Optional[Sequence[str] | str] = None,
        scrape: bool = False,
    ) -> Dict[str, Any]:
        return {
            "status": "success",
            "query": _clean_text(query),
            "local_search": self.search_local(query, top_k=local_top_k),
            "web_discovery": self.discover(
                query,
                max_results=web_max_results,
                engines=engines,
                domain_filter=domain_filter,
                scrape=scrape,
            ),
        }

    def _load_parsed_documents(self) -> List[CorpusDocument]:
        if not self.parse_manifest_path.exists():
            return []

        manifest = _safe_json_load(self.parse_manifest_path)
        entries = manifest.get("parsed_documents") or []
        documents: List[CorpusDocument] = []
        for entry in entries:
            raw_text_path = str(entry.get("parsed_text_path") or "").strip()
            if not raw_text_path:
                continue
            text_path = Path(raw_text_path).expanduser()
            if not text_path.is_absolute():
                text_path = (self.repo_root / text_path).resolve()
            if not text_path.exists() or not text_path.is_file():
                continue

            text = text_path.read_text(encoding="utf-8", errors="ignore")
            metadata_path = text_path.with_suffix(".json")
            sidecar = _safe_json_load(metadata_path) if metadata_path.exists() else {}
            title = self._infer_title(text, fallback=Path(str(entry.get("pdf_path") or text_path)).stem)
            source_id = text_path.stem
            graph_payload = self._extract_graph_payload(text=text, source_id=source_id, title=title, source_path=text_path)
            documents.append(
                CorpusDocument(
                    document_id=source_id,
                    title=title,
                    text=text,
                    source_type="parsed_document",
                    source_path=str(text_path),
                    metadata={
                        **entry,
                        **sidecar,
                        "graph_status": graph_payload.get("status", "unavailable"),
                    },
                    rules=[],
                    entities=list(graph_payload.get("entities", []) or []),
                    relationships=list(graph_payload.get("relationships", []) or []),
                )
            )
        return documents

    def _load_knowledge_graph_documents(self) -> List[CorpusDocument]:
        documents_dir = self.knowledge_graph_dir / "documents"
        if not documents_dir.exists():
            return []

        documents: List[CorpusDocument] = []
        for json_path in sorted(documents_dir.glob("*.json")):
            payload = _safe_json_load(json_path)
            text = str(payload.get("text") or "")
            document_metadata = payload.get("document") or {}
            title = str(document_metadata.get("title") or self._infer_title(text, fallback=json_path.stem))
            source_path = str(document_metadata.get("source_path") or json_path)
            documents.append(
                CorpusDocument(
                    document_id=str(payload.get("source_id") or json_path.stem),
                    title=title,
                    text=text,
                    source_type="knowledge_graph",
                    source_path=source_path,
                    metadata={
                        **(payload.get("metadata") or {}),
                        "provider": payload.get("provider", ""),
                        "status": payload.get("status", ""),
                    },
                    rules=list(payload.get("rules", []) or []),
                    entities=list(payload.get("entities", []) or []),
                    relationships=list(payload.get("relationships", []) or []),
                )
            )
        return documents

    def _extract_graph_payload(self, *, text: str, source_id: str, title: str, source_path: Path) -> Dict[str, Any]:
        if extract_graph_from_text is None:
            return {
                "status": "unavailable",
                "entities": [],
                "relationships": [],
                "error": INTEGRATION_IMPORT_ERROR or "graph extraction unavailable",
            }
        payload = extract_graph_from_text(
            text,
            source_id=source_id,
            metadata={
                "title": title,
                "source_path": str(source_path),
            },
        )
        return payload if isinstance(payload, dict) else {"status": "error", "entities": [], "relationships": []}

    def _infer_title(self, text: str, *, fallback: str) -> str:
        for line in str(text or "").splitlines():
            candidate = _clean_text(line)
            if 4 <= len(candidate) <= 180:
                return candidate
        return _clean_text(fallback) or "Untitled document"

    def _score_document(
        self,
        *,
        query_text: str,
        query_tokens: set[str],
        document: CorpusDocument,
    ) -> tuple[float, List[Dict[str, Any]], List[Dict[str, Any]]]:
        if not query_text:
            return 0.0, [], []

        score = 0.0
        matched_rules: List[Dict[str, Any]] = []
        matched_entities: List[Dict[str, Any]] = []

        if query_text.lower() in document.title_lower:
            score += 12.0
        if query_text.lower() in document.text_lower:
            score += 8.0

        if query_tokens:
            title_overlap = len(query_tokens & document.title_tokens)
            text_overlap = len(query_tokens & document.text_tokens)
            rule_overlap = len(query_tokens & document.rule_tokens)
            entity_overlap = len(query_tokens & document.entity_tokens)

            score += 7.0 * (title_overlap / max(len(query_tokens), 1))
            score += 5.0 * (text_overlap / max(len(query_tokens), 1))
            score += 6.0 * (rule_overlap / max(len(query_tokens), 1))
            score += 4.0 * (entity_overlap / max(len(query_tokens), 1))

        for rule in document.rules:
            rule_text = str(rule.get("text") or "")
            rule_tokens = _semantic_tokens(rule_text)
            overlap = len(query_tokens & rule_tokens) if query_tokens else 0
            if overlap == 0 and query_text.lower() not in rule_text.lower():
                continue
            matched_rules.append(
                {
                    "text": rule_text,
                    "section_title": rule.get("section_title", ""),
                    "rule_type": rule.get("rule_type", ""),
                    "modality": rule.get("modality", ""),
                    "overlap": overlap,
                }
            )
            score += 1.5 + overlap

        for entity in document.entities:
            entity_name = str(entity.get("name") or "")
            entity_tokens = _semantic_tokens(entity_name)
            overlap = len(query_tokens & entity_tokens) if query_tokens else 0
            if overlap == 0 and query_text.lower() not in entity_name.lower():
                continue
            matched_entities.append(
                {
                    "name": entity_name,
                    "type": entity.get("type", entity.get("entity_type", "")),
                    "overlap": overlap,
                }
            )
            score += 0.75 + overlap

        if matched_rules:
            score += min(6.0, float(len(matched_rules)))
        if matched_entities:
            score += min(4.0, float(len(matched_entities)))
        if document.source_type == "knowledge_graph":
            score += 0.5

        matched_rules.sort(key=lambda item: (-int(item.get("overlap", 0)), item.get("text", "")))
        matched_entities.sort(key=lambda item: (-int(item.get("overlap", 0)), item.get("name", "")))
        return score, matched_rules, matched_entities

    def _extract_snippet(
        self,
        query_text: str,
        query_tokens: set[str],
        document: CorpusDocument,
        matched_rules: Sequence[Dict[str, Any]],
    ) -> str:
        if matched_rules:
            return str(matched_rules[0].get("text") or "")[:500]

        sentences = _sentence_split(document.text[:12000])
        query_lower = query_text.lower()
        if query_lower:
            for sentence in sentences:
                if query_lower in sentence.lower():
                    return sentence[:500]

        best_sentence = ""
        best_overlap = -1
        for sentence in sentences[:80]:
            overlap = len(query_tokens & _semantic_tokens(sentence))
            if overlap > best_overlap:
                best_overlap = overlap
                best_sentence = sentence
        return best_sentence[:500]

    def _source_counts(self, documents: Iterable[CorpusDocument]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for document in documents:
            counts[document.source_type] = counts.get(document.source_type, 0) + 1
        return counts

    def _integration_status(self) -> Dict[str, Any]:
        return {
            "complaint_generator_root": str(COMPLAINT_GENERATOR_ROOT),
            "adapter_available": INTEGRATION_IMPORT_ERROR is None,
            "degraded_reason": INTEGRATION_IMPORT_ERROR,
        }

    def _normalize_domain_filters(self, domain_filter: Optional[Sequence[str] | str]) -> set[str]:
        if domain_filter is None:
            return set()
        if isinstance(domain_filter, str):
            values = [domain_filter]
        else:
            values = list(domain_filter)
        return {value.lower().strip() for value in values if value and value.strip()}

    def _matches_domain_filter(self, item: Dict[str, Any], normalized_filters: set[str]) -> bool:
        if not normalized_filters:
            return True
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        domain = str(metadata.get("domain") or _normalize_domain(str(item.get("url") or ""))).lower()
        return any(candidate in domain for candidate in normalized_filters)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HACC research and search engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_index = subparsers.add_parser("build-index", help="Build a searchable HACC corpus summary index")
    build_index.add_argument(
        "--output",
        default=str(REPO_ROOT / "research_results/hacc_search_index.json"),
        help="Path to write the index summary JSON",
    )

    search = subparsers.add_parser("search", help="Search the local HACC corpus")
    search.add_argument("query", help="Search query")
    search.add_argument("--top-k", type=int, default=10, help="Maximum number of local results")
    search.add_argument(
        "--source-type",
        action="append",
        default=[],
        help="Optional source type filter (repeatable): parsed_document or knowledge_graph",
    )

    discover = subparsers.add_parser("discover", help="Run web discovery through the ipfs_datasets adapter")
    discover.add_argument("query", help="Discovery query")
    discover.add_argument("--max-results", type=int, default=10, help="Maximum number of results")
    discover.add_argument("--engine", action="append", default=[], help="Preferred search engine (repeatable)")
    discover.add_argument("--domain", action="append", default=[], help="Domain substring filter (repeatable)")
    discover.add_argument("--scrape", action="store_true", help="Scrape the top few discovered URLs")

    research = subparsers.add_parser("research", help="Run local search plus web discovery")
    research.add_argument("query", help="Research query")
    research.add_argument("--top-k", type=int, default=10, help="Maximum number of local results")
    research.add_argument("--max-results", type=int, default=10, help="Maximum number of web results")
    research.add_argument("--engine", action="append", default=[], help="Preferred search engine (repeatable)")
    research.add_argument("--domain", action="append", default=[], help="Domain substring filter (repeatable)")
    research.add_argument("--scrape", action="store_true", help="Scrape the top few discovered URLs")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    engine = HACCResearchEngine()

    if args.command == "build-index":
        payload = engine.build_index(output_path=args.output)
    elif args.command == "search":
        payload = engine.search_local(
            args.query,
            top_k=args.top_k,
            source_types=args.source_type or None,
        )
    elif args.command == "discover":
        payload = engine.discover(
            args.query,
            max_results=args.max_results,
            engines=args.engine or None,
            domain_filter=args.domain or None,
            scrape=args.scrape,
        )
    else:
        payload = engine.research(
            args.query,
            local_top_k=args.top_k,
            web_max_results=args.max_results,
            engines=args.engine or None,
            domain_filter=args.domain or None,
            scrape=args.scrape,
        )

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
