#!/usr/bin/env python3
"""
download_manager.py — compatibility wrapper over complaint-generator's search adapter.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from integrations.ipfs_datasets.search import download_with_recovery


class DownloadManager:
    """Maintain the older manifest contract while delegating downloads upstream."""

    def __init__(
        self,
        raw_dir: str = "research_results/documents/raw",
        metadata_file: str = "research_results/documents/download_manifest.json",
    ):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = Path(metadata_file)
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as handle:
                return json.load(handle)
        return {"downloads": [], "dedupe_index": {}}

    def _save_manifest(self) -> None:
        with open(self.metadata_file, "w", encoding="utf-8") as handle:
            json.dump(self.manifest, handle, indent=2)

    def compute_hash(self, url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def is_downloaded(self, url: str) -> Optional[str]:
        return self.manifest["dedupe_index"].get(self.compute_hash(url))

    def download_pdf(self, url: str, source: str, timeout: int = 30) -> Optional[str]:
        existing = self.is_downloaded(url)
        if existing:
            logger.info("Already downloaded: %s -> %s", url, existing)
            return existing

        destination = self.raw_dir / f"{self.compute_hash(url)}.pdf"
        payload = download_with_recovery(url, output_path=destination, timeout=timeout)
        if payload.get("status") != "success":
            logger.error("Failed to download %s: %s", url, payload.get("error") or payload.get("status"))
            return None

        metadata = {
            "url": url,
            "source": source,
            "filepath": str(destination),
            "saved_path": str(destination),
            "download_date": datetime.now().isoformat(),
            "file_size": destination.stat().st_size if destination.exists() else 0,
            "content_type": payload.get("content_type", "unknown"),
            "recovery_strategy": payload.get("recovery_strategy", ""),
        }
        self.manifest["downloads"].append(metadata)
        self.manifest["dedupe_index"][self.compute_hash(url)] = str(destination)
        self._save_manifest()
        logger.info("Downloaded to: %s", destination)
        return str(destination)

    def batch_download(self, urls: List[Dict]) -> List[str]:
        filepaths: List[str] = []
        for item in urls:
            filepath = self.download_pdf(item["url"], item["source"])
            if filepath:
                filepaths.append(filepath)
        return filepaths


if __name__ == "__main__":
    logger.info("Download manager compatibility wrapper ready.")
