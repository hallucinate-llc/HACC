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
        # If parsed output/meta already exists, skip work and return existing meta
        existing_meta_path = PARSED_DIR / f"{base}.json"
        existing_txt_path = PARSED_DIR / f"{base}.txt"
        if existing_meta_path.exists():
            try:
                with open(existing_meta_path, 'r', encoding='utf-8') as em:
                    meta = json.load(em)
                return {'meta': meta, 'skipped': True}
            except Exception:
                # Fall through and reprocess if meta is unreadable
                pass
        if existing_txt_path.exists() and existing_meta_path.exists() is False:
            # If text exists but no meta, synthesize a minimal meta entry
            try:
                with open(existing_txt_path, 'r', encoding='utf-8') as tf:
                    text = tf.read()
                meta = {
                    'pdf_path': str(pdf_path),
                    'parsed_text_path': str(existing_txt_path),
                    'parse_date': datetime.now().isoformat(),
                    'source': 'third_party:batch_parallel',
                    'url': f'file://{pdf_path}',
                    'text_length': len(text),
                    'checksum': hashlib.sha256(text.encode('utf-8')).hexdigest(),
                    'extraction_method': 'existing_parsed_text',
                    'ocr_available': False,
                    'ocr_attempted': False,
                    'ocr_used': False,
                    'needs_ocr': False
                }
                meta_path = existing_txt_path.with_suffix('.json')
                with open(meta_path, 'w', encoding='utf-8') as mf:
                    json.dump(meta, mf, indent=2)
                return {'meta': meta, 'skipped': True}
            except Exception:
                pass
        # Run ocrmypdf --force-ocr
        proc = subprocess.run([
            'ocrmypdf', '--force-ocr', '--skip-big', '0', str(pdf_path), str(temp_ocr)
        ], capture_output=True, text=True, timeout=timeout_ocr)
        if proc.returncode != 0:
            # ocrmypdf failed — attempt automatic fallback using pdftotext directly on the original PDF
            try:
                fproc = subprocess.run(['pdftotext', '-layout', str(pdf_path), '-'], capture_output=True, text=True, timeout=timeout_pdftotext)
                ftext = fproc.stdout if fproc.returncode == 0 else ''
            except subprocess.TimeoutExpired:
                return {'error': 'ocrmypdf failed and pdftotext timed out', 'pdf': str(pdf_path)}
            except FileNotFoundError as e:
                return {'error': f'missing binary during fallback: {e}', 'pdf': str(pdf_path)}
            except Exception as e:
                return {'error': f'fallback pdftotext error: {e}', 'pdf': str(pdf_path)}

            if ftext and len(ftext.strip()) >= 200:
                # write fallback text + meta
                text = ftext
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
                    'extraction_method': 'pdftotext_only_fallback',
                    'ocr_available': False,
                    'ocr_attempted': False,
                    'ocr_used': False,
                    'needs_ocr': False
                }
                meta_path = out_txt.with_suffix('.json')
                with open(meta_path, 'w', encoding='utf-8') as mf:
                    json.dump(meta, mf, indent=2)

                result_meta = meta
                return {'meta': result_meta}
            else:
                # fallback also failed — return original ocrmypdf stderr if available
                return {'error': f'ocrmypdf failed and pdftotext fallback produced insufficient text', 'pdf': str(pdf_path), 'stderr': proc.stderr[:1000]}

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

    # Load already-parsed metadata (so we don't re-run OCR for those PDFs)
    parsed_documents = []
    existing_meta_files = sorted(PARSED_DIR.glob('*.json'))
    for mfile in existing_meta_files:
        try:
            with open(mfile, 'r', encoding='utf-8') as mf:
                parsed_documents.append(json.load(mf))
        except Exception:
            # ignore unreadable meta files; they'll be reprocessed
            pass

    # Only process PDFs that do not already have a parsed .json
    all_pdfs = sorted(RAW_DIR.glob('*.pdf'))
    pdfs_to_process = [p for p in all_pdfs if not (PARSED_DIR / f"{p.stem}.json").exists()]
    print(f'Found {len(all_pdfs)} PDFs, {len(pdfs_to_process)} need processing; using {args.workers} workers')

    results = []
    if pdfs_to_process:
        with ProcessPoolExecutor(max_workers=args.workers) as exe:
            futures = {exe.submit(process_pdf, str(p), args.timeout_ocr, args.timeout_pdftotext): p for p in pdfs_to_process}
            for fut in as_completed(futures):
                p = futures[fut]
                try:
                    res = fut.result()
                except Exception as e:
                    res = {'error': str(e), 'pdf': str(p)}
                results.append(res)
                if 'meta' in res and res['meta']:
                    print(f"OK: {p.name} -> {res['meta'].get('text_length', 0)} chars")
                else:
                    print(f"FAIL: {p.name} -> {res.get('error')}")

    # Merge newly parsed metadata with existing parsed documents
    new_parsed = [r['meta'] for r in results if r.get('meta')]
    parsed_documents.extend(new_parsed)

    # Write manifest
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as mf:
        json.dump({'parsed_documents': parsed_documents}, mf, indent=2)

    # Report summary counts
    ok = len(parsed_documents)
    fail = sum(1 for r in results if not r.get('meta'))
    skipped = len(existing_meta_files)
    print(f'Done. Total parsed={ok} (skipped {skipped}), newly failed={fail}. Manifest saved to {MANIFEST_PATH}')


if __name__ == '__main__':
    main()
