"""REQ_abstract.csv 형식 입력 → 19종 smell 평가 + Excel 리포트 (v2.8).

Usage:
    python examples/req_abstract_demo.py \
        --input "C:/path/to/REQ_abstract.csv" \
        --output results/req_abstract_demo/
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.io import load_req_abstract, save_csv, write_xlsx_report
from kofinre.io.csv_loader import split_sub_requirements
from kofinre.detectors import RegexDetector
from kofinre.detectors.regex_detector import collect_undefined_acronyms
from kofinre.ensemble import SMELL_CODES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    rows = load_req_abstract(args.input)
    print(f'요구사항 행: {len(rows)}')

    # 도메인 약어 컨텍스트 (전체 문서 단위)
    all_text = '\n'.join(f"{r.get('req_title','')} {r.get('req_details','')}" for r in rows)
    ctx = {'undefined_acronyms': collect_undefined_acronyms(all_text)}

    regex = RegexDetector()

    req_results = []
    proj_agg = defaultdict(lambda: dict({'reqs': 0, 'with_smell': 0}, **{c: 0 for c in SMELL_CODES}))

    for r in rows:
        subs = split_sub_requirements(r['req_details'])
        req_flags = {c: 0 for c in SMELL_CODES}
        for sub in subs:
            res = regex.detect(sub, ctx)
            for c in SMELL_CODES:
                if res.flags[c]['detected']:
                    req_flags[c] = 1

        has_smell = int(any(req_flags.values()))
        req_results.append({
            'project_id': r['project_id'],
            'project_name': r['project_name'],
            'system_name': r['system_name'],
            'req_id': r['req_id'],
            'req_title': r['req_title'],
            'sentence': r['req_details'][:300],
            'has_smell': has_smell,
            **req_flags,
        })

        pid = r['project_id']
        proj_agg[pid]['reqs'] += 1
        proj_agg[pid]['with_smell'] += has_smell
        for c in SMELL_CODES:
            proj_agg[pid][c] += req_flags[c]

    save_csv(args.output / 'requirements.csv', req_results)
    per_proj_rows = [{'project_id': k, **v} for k, v in sorted(proj_agg.items())]
    save_csv(args.output / 'per_project.csv', per_proj_rows)

    # 요약
    total = len(req_results)
    smelly = sum(r['has_smell'] for r in req_results)
    summary = {
        '총 요구사항': total,
        'Smell 검출': f'{smelly} ({100*smelly/max(total,1):.1f}%)',
        **{c: sum(r[c] for r in req_results) for c in SMELL_CODES},
    }
    print('=== 요약 ===')
    for k, v in summary.items():
        print(f'  {k:<14} {v}')

    # Excel 리포트
    write_xlsx_report(
        args.output / 'report.xlsx',
        summary=summary,
        requirements=req_results,
        per_project=per_proj_rows,
    )
    print(f'\n결과: {args.output}')


if __name__ == '__main__':
    main()
