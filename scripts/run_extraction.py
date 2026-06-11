"""Stage 1 entrypoint — raw_documents/ → sentence_candidates.csv + requirement_candidates.csv.

Usage:
    python scripts/run_extraction.py \
        --input data/raw_documents/ \
        --output results/stage1_extraction/
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.extraction import (
    extract_by_signature, normalize_text,
    split_sentences, is_meaningful, is_requirement,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, type=Path, help='폴더 또는 단일 파일')
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    extracted_dir = args.output / 'extracted_text'
    extracted_dir.mkdir(exist_ok=True)

    # 파일 수집
    if args.input.is_file():
        files = [args.input]
    else:
        files = []
        for ext in ['*.html', '*.htm', '*.hwp', '*.hwpx', '*.pdf', '*.docx', '*.doc', '*.rtf']:
            files.extend(args.input.rglob(ext))

    # HWP COM 1회 생성 (Windows + 한컴오피스)
    hwp_obj = None
    try:
        import win32com.client, pythoncom
        pythoncom.CoInitialize()
        hwp_obj = win32com.client.Dispatch('HWPFrame.HwpObject')
        try: hwp_obj.SetMessageBoxMode(0x10)
        except: pass
    except Exception as e:
        print(f'(HWP COM 비활성: {e})')

    extraction_log = []
    sentence_rows = []
    req_rows = []
    exclusion_rows = []

    for i, p in enumerate(files, 1):
        doc_id = p.stem[:60]
        try:
            text, kind = extract_by_signature(p, hwp_obj)
            text = normalize_text(text)
            (extracted_dir / f'{doc_id}.txt').write_text(text, encoding='utf-8')
            extract_ok = True
            failure = ''
        except Exception as e:
            text, kind = '', None
            extract_ok = False
            failure = f'{type(e).__name__}: {e}'

        sentences = split_sentences(text) if text else []
        meaningful = [s for s in sentences if is_meaningful(s)]
        req_count = 0
        for s in meaningful:
            sentence_rows.append({'doc_id': doc_id, 'sentence': s})
            ok, reason = is_requirement(s)
            if ok:
                req_rows.append({'doc_id': doc_id, 'sentence': s})
                req_count += 1
            else:
                exclusion_rows.append({'doc_id': doc_id, 'sentence': s[:200], 'reason': reason.value})

        extraction_log.append({
            'doc': doc_id, 'format': kind.value if kind else 'unknown',
            'extract_ok': extract_ok,
            'sentence_candidates': len(meaningful),
            'requirement_candidates': req_count,
            'failure_reason': failure,
        })
        print(f'[{i:02d}/{len(files)}] {doc_id[:50]:<50}  sent={len(meaningful):>4}  req={req_count:>3}')

    if hwp_obj:
        try: hwp_obj.Quit()
        except: pass

    # 산출물 (논문 명명)
    with open(args.output / 'sentence_candidates.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['doc_id', 'sentence'])
        w.writeheader()
        for r in sentence_rows: w.writerow(r)
    with open(args.output / 'requirement_candidates.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['doc_id', 'sentence'])
        w.writeheader()
        for r in req_rows: w.writerow(r)
    with open(args.output / 'exclusion_reason.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['doc_id', 'sentence', 'reason'])
        w.writeheader()
        for r in exclusion_rows: w.writerow(r)
    with open(args.output / 'extraction_log.json', 'w', encoding='utf-8') as f:
        json.dump(extraction_log, f, ensure_ascii=False, indent=2)

    print(f'\n총 문서: {len(files)}')
    print(f'문장 후보: {len(sentence_rows)}')
    print(f'요구사항 후보: {len(req_rows)}')
    print(f'산출물: {args.output}')


if __name__ == '__main__':
    main()
