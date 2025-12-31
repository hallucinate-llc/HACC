#!/usr/bin/env python3
"""
batch_ocr_parallel.py
Force-OCR all PDFs in research_results/documents/raw using multiple processes,
extract text with pdftotext, write per-file metadata JSONs, and emit a
single parse_manifest.json summarizing results.

Usage: python3 research_data/scripts/batch_ocr_parallel.py [--workers N]
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import subprocess
import json
import hashlib
from datetime import datetime
import os
import tempfile

RAW_DIR = Path('research_results/documents/raw')
PARSED_DIR = Path('research_results/documents/parsed')
MANIFEST_PATH = Path('research_results/documents/parse_manifest.json')

PARSED_DIR.mkdir(parents=True, exist_ok=True)


def process_pdf(pdf_path_str, timeout_ocr=300, timeout_pdftotext=120):
    pdf_path = Path(pdf_path_str)
    base = pdf_path.stem
    temp_dir = tempfile.gettempdir()
    temp_ocr = Path(temp_dir) / f"{base}_ocr.pdf"
    result_meta = None
    try:
        # Run ocrmypdf --force-ocr
        proc = subprocess.run([
            'ocrmypdf', '--force-ocr', '--skip-big', '0', str(pdf_path), str(temp_ocr)
        ], capture_output=True, text=True, timeout=timeout_ocr)
        if proc.returncode != 0:
            return {'error': f'ocrmypdf failed', 'pdf': str(pdf_path), 'stderr': proc.stderr[:1000]}

        # Extract text from OCR'd PDF
        tproc = subprocess.run(['pdftotext', '-layout', str(temp_ocr), '-'], capture_output=True, text=True, timeout=timeout_pdftotext)
        if tproc.returncode != 0:
            return {'error': f'pdftotext failed', 'pdf': str(pdf_path), 'stderr': tproc.stderr[:1000]}

        text = tproc.stdout or ''
        out_txt = PARSED_DIR / f"{base}.txt"
        with open(out_txt, 'w', encoding='utf-8') as f:
            f.write(text)

        meta = {
            'pdf_path': str(pdf_path),
            'parsed_text_path': str(out_txt),
            'parse_date': datetime.now().isoformat(),
            'source': 'third_party:batch_parallel',
            'url': f'file://{pdf_path}',
            'text_length': len(text),
            'checksum': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'extraction_method': 'ocrmypdf_force+pdftotext',
            'ocr_available': True,
            'ocr_attempted': True,
            'ocr_used': True,
            'needs_ocr': False
        }
        meta_path = out_txt.with_suffix('.json')
        with open(meta_path, 'w') as mf:
            json.dump(meta, mf, indent=2)

        result_meta = meta
    except subprocess.TimeoutExpired:
        return {'error': 'timeout', 'pdf': str(pdf_path)}
    except FileNotFoundError as e:
        return {'error': f'missing binary: {e}', 'pdf': str(pdf_path)}
    except Exception as e:
        return {'error': str(e), 'pdf': str(pdf_path)}
    finally:
        try:
            if temp_ocr.exists():
                temp_ocr.unlink()
        except Exception:
            pass
    return {'meta': result_meta}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=os.cpu_count() or 1)
    parser.add_argument('--timeout-ocr', type=int, default=300)
    parser.add_argument('--timeout-pdftotext', type=int, default=120)
    args = parser.parse_args()

    pdfs = sorted(RAW_DIR.glob('*.pdf'))
    print(f'Found {len(pdfs)} PDFs; using {args.workers} workers')

    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as exe:
        futures = {exe.submit(process_pdf, str(p), args.timeout_ocr, args.timeout_pdftotext): p for p in pdfs}
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                res = {'error': str(e), 'pdf': str(p)}
            results.append(res)
            if 'meta' in res and res['meta']:
                print(f"OK: {p.name} -> {res['meta']['text_length']} chars")
            else:
                print(f"FAIL: {p.name} -> {res.get('error')}")

    # Aggregate metadata
    parsed_documents = [r['meta'] for r in results if r.get('meta')]
    with open(MANIFEST_PATH, 'w') as mf:
        json.dump({'parsed_documents': parsed_documents}, mf, indent=2)

    # Report summary counts
    ok = sum(1 for r in results if r.get('meta'))
    fail = sum(1 for r in results if not r.get('meta'))
    print(f'Done. OK={ok}, FAIL={fail}. Manifest saved to {MANIFEST_PATH}')


if __name__ == '__main__':
    main()
