"""Gold Label 데이터셋 빌드 (논문 Stage 4·Manual Validation).

워크플로우:
1. Stage 3 ensemble 결과에서 층화 표본 200건 추출
2. 평가자 2명(R1, R2)용 양식 CSV 생성
   - prediction 컬럼(모델 예측)을 보여줘서 빠른 동의/비동의 판단 가능
3. 채워진 R1.csv, R2.csv 로 Cohen's kappa 계산
4. 불일치 항목 추출 → 합의 양식 생성
5. 합의 결과 + R1·R2 결과 → gold_labels.csv 확정
6. 모델 예측 vs gold → precision/recall/F1/kappa 산정

Usage:
    # 1. 표본 추출
    python scripts/build_gold_dataset.py sample \
        --predictions results/stage3_detection/ensemble_smell_labels.csv \
        --output data/gold_labels/

    # 2. R1, R2 가 양식 채운 후 일치도 평가
    python scripts/build_gold_dataset.py evaluate \
        --r1 data/gold_labels/R1.csv \
        --r2 data/gold_labels/R2.csv \
        --predictions results/stage3_detection/ensemble_smell_labels.csv \
        --output results/stage4_evaluation/
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.validation import (
    stratified_sample, create_validation_template,
    load_rater_results, compute_inter_rater_agreement, consolidate_gold,
)
from kofinre.metrics import precision_recall_f1, macro_f1, micro_f1
from kofinre.ensemble import SMELL_CODES


def cmd_sample(args):
    """200건 층화 표본 + 평가자 양식 생성."""
    rows = list(csv.DictReader(open(args.predictions, encoding='utf-8-sig')))
    print(f'입력 예측: {len(rows)}건')

    sample = stratified_sample(rows, n_target=args.n_target,
                               smell_col='has_smell',
                               positive_ratio=args.positive_ratio)
    print(f'층화 표본: {len(sample)}건 '
          f'(positive {sum(1 for r in sample if int(r["has_smell"]))} / '
          f'negative {sum(1 for r in sample if not int(r["has_smell"]))})')

    args.output.mkdir(parents=True, exist_ok=True)

    # 평가자별 양식 — 예측을 함께 보여줘서 빠른 검토 가능
    for rater_id in ['R1', 'R2']:
        out_path = args.output / f'{rater_id}.csv'
        fieldnames = (['sample_id', 'project_id', 'sentence', 'is_requirement']
                      + SMELL_CODES + ['notes', 'rater_id']
                      + [f'pred_{c}' for c in SMELL_CODES])
        with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for i, r in enumerate(sample, 1):
                row = {
                    'sample_id': f'V{i:04d}',
                    'project_id': r.get('project_id', ''),
                    'sentence': r.get('sentence', '')[:500],
                    'is_requirement': '',
                    **{c: '' for c in SMELL_CODES},
                    'notes': '',
                    'rater_id': rater_id,
                    **{f'pred_{c}': int(r.get(c, 0)) for c in SMELL_CODES},
                }
                w.writerow(row)
        print(f'  생성: {out_path}')

    # 가이드 작성
    guide = args.output / 'README.md'
    guide.write_text(f"""# Gold Label 작성 가이드

## 개요
- 표본 크기: {len(sample)}건
- 평가자 2명 (R1, R2) 독립 판정 필수
- Smell 코드 10종: S1~S10

## 작성 순서

1. `R1.csv`, `R2.csv` 각각 다른 평가자가 채움
2. 각 행마다:
   - `is_requirement`: 이게 진짜 요구사항인가? (1=네, 0=아니오)
   - `S1`~`S10`: 각 smell에 해당하는가? (1/0)
   - `notes`: 특이사항/근거 (선택)
3. `pred_S1`~`pred_S10`은 **모델 예측** — 참고만, 절대 따라 적지 말 것
4. 다 채운 후 `evaluate` 명령으로 일치도 산출

## Smell 정의 (참고)
| 코드 | 의미 | 예시 |
|---|---|---|
| S1 | 복합의무 | 한 문장에 2+ 의무 |
| S2 | 불완전 | 시스템 응답·행위·대상 누락 |
| S3 | 모호어 | "적절히, 필요한, 실시간" |
| S4 | 약한의무 | "~한다 / ~된다" |
| S5 | 주체누락 | 수행 주체 미명시 |
| S6 | 정량부재 | 성능 키워드 + 숫자 부재 |
| S7 | 미정의약어 | 정의 없는 약어 |
| S8 | 범위모호 | "및/또는, 등, 포함" |
| S9 | 수동표현 | "되어야 한다" |
| S10 | 검증불가 | 검증 방법·판정 기준 부재 |
""", encoding='utf-8')
    print(f'  가이드: {guide}')


def cmd_evaluate(args):
    """R1, R2 채워진 결과로 Cohen's kappa + gold label 합의 + 모델 평가."""
    r1 = load_rater_results(args.r1)
    r2 = load_rater_results(args.r2)
    print(f'R1: {len(r1)}건, R2: {len(r2)}건, 공통: {len(set(r1) & set(r2))}건')

    # 1. 평가자 간 일치도
    agreement = compute_inter_rater_agreement(r1, r2)
    print('\n=== Cohen\'s Kappa ===')
    for code, k in agreement.items():
        label = '상' if k > 0.8 else '중상' if k > 0.6 else '중' if k > 0.4 else '하'
        print(f'  {code:<16} {k:>6.3f}  [{label}]')

    # 2. Gold label 합의
    gold = consolidate_gold(r1, r2)

    # 3. 모델 예측 로드
    preds = {}
    for r in csv.DictReader(open(args.predictions, encoding='utf-8-sig')):
        preds[r['sentence']] = {c: int(r.get(c, 0)) for c in SMELL_CODES}

    args.output.mkdir(parents=True, exist_ok=True)

    # gold_labels.csv 저장
    with open(args.output / 'gold_labels.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['sample_id'] + SMELL_CODES + ['is_requirement'])
        for sid in sorted(gold):
            w.writerow([sid] + [gold[sid].get(c, 0) for c in SMELL_CODES] +
                      [gold[sid].get('is_requirement', 0)])

    # 4. 모델 vs gold → Detection Performance
    # NOTE: 모델 예측을 sentence 기준으로 매핑하려면 sample 양식에 sentence가 있어야.
    # 여기서는 단순화: R1.csv 의 sentence 컬럼 사용
    rows1 = list(csv.DictReader(open(args.r1, encoding='utf-8-sig')))
    sentence_by_sid = {r['sample_id']: r['sentence'] for r in rows1}

    gold_per_smell = {c: [] for c in SMELL_CODES}
    pred_per_smell = {c: [] for c in SMELL_CODES}
    for sid in sorted(gold):
        sent = sentence_by_sid.get(sid, '')
        pred = preds.get(sent, {c: 0 for c in SMELL_CODES})
        for c in SMELL_CODES:
            gold_per_smell[c].append(gold[sid].get(c, 0))
            pred_per_smell[c].append(pred[c])

    print('\n=== Detection Performance vs Gold ===')
    per_smell_metrics = {}
    for c in SMELL_CODES:
        m = precision_recall_f1(gold_per_smell[c], pred_per_smell[c])
        per_smell_metrics[c] = m
        print(f'  {c}  P={m["precision"]:.3f}  R={m["recall"]:.3f}  F1={m["f1"]:.3f}')

    macro = macro_f1(gold_per_smell, pred_per_smell)
    micro = micro_f1(gold_per_smell, pred_per_smell)
    print(f'\n  Macro-F1: {macro["macro_f1"]:.3f}')
    print(f'  Micro-F1: {micro:.3f}')

    # 리포트
    from kofinre.reporting import render_evaluation_report
    render_evaluation_report(
        args.output / 'evaluation_report.md',
        per_smell_metrics,
        macro_f1=macro['macro_f1'],
        micro_f1=micro,
        kappa=sum(agreement.values()) / len(agreement),
    )
    print(f'\n리포트: {args.output / "evaluation_report.md"}')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='command', required=True)

    s = sub.add_parser('sample', help='200건 표본 + 평가자 양식 생성')
    s.add_argument('--predictions', required=True, type=Path)
    s.add_argument('--output', required=True, type=Path)
    s.add_argument('--n-target', type=int, default=200)
    s.add_argument('--positive-ratio', type=float, default=0.6)

    e = sub.add_parser('evaluate', help='R1, R2 채워진 결과로 평가')
    e.add_argument('--r1', required=True, type=Path)
    e.add_argument('--r2', required=True, type=Path)
    e.add_argument('--predictions', required=True, type=Path)
    e.add_argument('--output', required=True, type=Path)

    args = ap.parse_args()
    if args.command == 'sample':
        cmd_sample(args)
    elif args.command == 'evaluate':
        cmd_evaluate(args)


if __name__ == '__main__':
    main()
