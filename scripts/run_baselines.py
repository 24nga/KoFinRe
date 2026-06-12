"""4 방식 baseline 비교 — Rule / NLP / LLM / Ensemble.

논문 IV.3 Baseline and Comparison:
- Rule-only: 정규식·키워드 기반 탐지
- NLP-only:  한국어 NLP 전처리(kiwipiepy 형태소) 기반 탐지
- LLM-assisted: LLM 보조 판정 기반 탐지
- Ensemble: 위 셋 결합 + rule-priority voting

Usage:
    python scripts/run_baselines.py \
        --predictions data/gold_labels/D4_R1_sim.csv \
        --output results/baseline_comparison/
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.detectors import RegexDetector
from kofinre.detectors.morph_detector import MorphDetector
from kofinre.detectors.llm_detector import LLMDetector
from kofinre.detectors.chunk_detector import ChunkDetector
from kofinre.detectors.dictionary_detector import DictionaryDetector
from kofinre.detectors.regex_detector import collect_undefined_acronyms
from kofinre.ensemble import ensemble, SMELL_CODES
from kofinre.metrics import precision_recall_f1, macro_f1, micro_f1


def predict_all_methods(sentences, ctx, llm_caller=None):
    """4 방식 각각 prediction 산출."""
    regex = RegexDetector()
    morph = MorphDetector()
    chunk = ChunkDetector()
    diction = DictionaryDetector()
    llm = LLMDetector(llm_caller=llm_caller)

    results = {'rule_only': [], 'nlp_only': [], 'llm_assisted': [], 'ensemble': []}
    for s in sentences:
        r_regex = regex.detect(s, ctx)
        r_morph = morph.detect(s, ctx)
        r_chunk = chunk.detect(s, ctx)
        r_dict = diction.detect(s, ctx)
        r_llm = llm.detect(s, ctx)

        # Rule-only — RegexDetector 만
        results['rule_only'].append({c: r_regex.flags.get(c, {}).get('detected', 0)
                                    for c in SMELL_CODES})
        # NLP-only — Morph + Chunk
        results['nlp_only'].append({c: int(any(r.flags.get(c, {}).get('detected', 0)
                                                for r in [r_morph, r_chunk]))
                                    for c in SMELL_CODES})
        # LLM-assisted — Regex + LLM (LLM이 dry-run이면 사실상 Regex)
        results['llm_assisted'].append({c: int(any(r.flags.get(c, {}).get('detected', 0)
                                                    for r in [r_regex, r_llm]))
                                        for c in SMELL_CODES})
        # Ensemble — 5 detector + voting
        ens = ensemble([r_regex, r_morph, r_chunk, r_dict, r_llm],
                       method='rule_priority')
        results['ensemble'].append({c: ens[c]['detected'] for c in SMELL_CODES})

    return results


def compute_metrics(predictions, gold_per_smell):
    """P/R/F1 per smell + Macro-F1 + Micro-F1."""
    pred_per_smell = {c: [p[c] for p in predictions] for c in SMELL_CODES}
    per_smell = {}
    for c in SMELL_CODES:
        if not gold_per_smell[c]: continue
        per_smell[c] = precision_recall_f1(gold_per_smell[c], pred_per_smell[c])
    macro = macro_f1(gold_per_smell, pred_per_smell)
    micro = micro_f1(gold_per_smell, pred_per_smell)
    return per_smell, macro['macro_f1'], micro


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--predictions', required=True, type=Path,
                   help='R1_sim CSV (gold label) — sample_id, sentence, S1..S10')
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # 1. 입력 로드 (R1_sim = gold label)
    rows = list(csv.DictReader(open(args.predictions, encoding='utf-8-sig')))
    print(f'Gold label: {len(rows)}건')

    sentences = [r['sentence'] for r in rows]
    gold_per_smell = {c: [int(r.get(c, 0)) for r in rows] for c in SMELL_CODES}

    # 2. 약어 context
    ctx = {'undefined_acronyms': collect_undefined_acronyms('\n'.join(sentences))}

    # 3. 4 방식 prediction
    print('\n=== 4 방식 prediction 산출 중 ===')
    preds = predict_all_methods(sentences, ctx, llm_caller=None)
    for method, vals in preds.items():
        smelly = sum(1 for p in vals if any(p[c] for c in SMELL_CODES))
        print(f'  {method:<15} {smelly}/{len(sentences)} smelly')

    # 4. 지표 산출
    print('\n=== 4 방식 성능 (gold vs prediction) ===')
    print(f"{'Method':<15} {'Macro-F1':>10} {'Micro-F1':>10}  Per-smell F1")
    print('-' * 70)
    all_metrics = {}
    for method in ['rule_only', 'nlp_only', 'llm_assisted', 'ensemble']:
        per_smell, macro, micro = compute_metrics(preds[method], gold_per_smell)
        all_metrics[method] = {'per_smell': per_smell, 'macro_f1': macro, 'micro_f1': micro}
        per_smell_str = '  '.join(f'{c}:{per_smell[c]["f1"]:.2f}'
                                 for c in SMELL_CODES if c in per_smell)
        print(f'{method:<15} {macro:>10.3f} {micro:>10.3f}  {per_smell_str}')

    # 5. CSV 저장
    out_csv = args.output / 'baseline_comparison.csv'
    with open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['method', 'macro_f1', 'micro_f1'] + [f'{c}_P' for c in SMELL_CODES]
                  + [f'{c}_R' for c in SMELL_CODES] + [f'{c}_F1' for c in SMELL_CODES])
        for method, m in all_metrics.items():
            row = [method, round(m['macro_f1'], 3), round(m['micro_f1'], 3)]
            for c in SMELL_CODES:
                ps = m['per_smell'].get(c, {})
                row.append(round(ps.get('precision', 0), 3))
            for c in SMELL_CODES:
                ps = m['per_smell'].get(c, {})
                row.append(round(ps.get('recall', 0), 3))
            for c in SMELL_CODES:
                ps = m['per_smell'].get(c, {})
                row.append(round(ps.get('f1', 0), 3))
            w.writerow(row)

    # 6. 리포트
    lines = [
        '# Baseline Comparison Report',
        '',
        f'_Gold label: {args.predictions.name} ({len(rows)}건)_',
        '',
        '## 전체 성능',
        '',
        '| 방식 | Macro-F1 | Micro-F1 |',
        '|---|---:|---:|',
    ]
    for method, m in all_metrics.items():
        lines.append(f'| {method} | {m["macro_f1"]:.3f} | {m["micro_f1"]:.3f} |')

    lines += ['', '## Smell 유형별 F1 비교', '',
              '| Smell | ' + ' | '.join(all_metrics.keys()) + ' |',
              '|---|' + '|'.join(['---:'] * len(all_metrics)) + '|']
    for c in SMELL_CODES:
        cells = [c]
        for method in all_metrics:
            f1 = all_metrics[method]['per_smell'].get(c, {}).get('f1', 0)
            cells.append(f'{f1:.3f}')
        lines.append('| ' + ' | '.join(cells) + ' |')

    lines += ['', '## 분석',
              '',
              '- **Rule-only**: RegexDetector 단독 — 가장 단순, 빠른 baseline',
              '- **NLP-only**: MorphDetector (kiwipiepy) + ChunkDetector — 형태소 분석 기반',
              '- **LLM-assisted**: RegexDetector + LLMDetector OR — LLM 누락 보완',
              '- **Ensemble**: 5 detector + rule-priority voting — 종합 결정',
              '',
              '※ LLM dry-run 환경에선 LLM-assisted ≈ Rule-only.',
              '   ANTHROPIC_API_KEY 설정 후 재실행 시 LLM 효과 확인 가능.']
    (args.output / 'baseline_report.md').write_text('\n'.join(lines), encoding='utf-8')

    print(f'\n저장: {out_csv}')
    print(f'리포트: {args.output / "baseline_report.md"}')


if __name__ == '__main__':
    main()
