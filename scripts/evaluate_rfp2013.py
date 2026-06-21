"""RFP 2013 데이터셋 v2.8 19종 smell 평가 + 통계 리포트.

입력: results/rfp_2013/stage1/ (sentence_candidates.csv + xlsx_requirements.csv)
출력: results/rfp_2013/stage3/
  - all_detection.csv       — 전체 문장별 19종 검출
  - smell_summary.csv        — 문서별 통계
  - smell_summary_by_sheet.csv — XLSX 시트별 통계
  - report.md                — 요약 리포트
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.detectors.regex_detector import RegexDetector, collect_undefined_acronyms
from kofinre import korean_patterns as kp


SMELL_NAMES = {
    'S1': '복합의무', 'S2': '불완전', 'S3': '모호어', 'S4': '약한의무',
    'S5': '주체누락', 'S6': '정량부재', 'S7': '미정의약어', 'S8': '범위모호',
    'S9': '수동표현', 'S10': '검증불가',
    'S11': '구현편향', 'S12': '부정문', 'S13': '추측표현',
    'S14': '수혜자불명', 'S15': '지시어모호',
    'S16': '필요성불명확', 'S17': '실현불가', 'S18': '추적ID부재',
    'S19': '제약카테고리불명',
}
SMELL_CODES = list(SMELL_NAMES.keys())


def main():
    stage1 = Path('results/rfp_2013/stage1')
    out_dir = Path('results/rfp_2013/stage3')
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 입력 통합
    rows = []
    sources = {
        'HWP 요구사항후보': stage1 / 'requirement_candidates.csv',
        'HWP 전체문장': stage1 / 'sentence_candidates.csv',
        'XLSX 요구사항': stage1 / 'xlsx_requirements.csv',
    }
    for label, p in sources.items():
        if not p.exists():
            print(f'(없음) {p}')
            continue
        n = 0
        with open(p, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                r['source'] = label
                rows.append(r)
                n += 1
        print(f'  + {label}: {n} rows')

    # XLSX 요구사항만 detection 대상 (HWP 전체문장은 컨텍스트로만 약어 추출에 사용)
    eval_rows = [r for r in rows if r['source'] in ('XLSX 요구사항', 'HWP 요구사항후보')]
    all_text = '\n'.join(r['sentence'] for r in rows)
    ctx = {'undefined_acronyms': collect_undefined_acronyms(all_text)}
    print(f'\n  평가 대상: {len(eval_rows)} 문장')
    print(f'  미정의 약어: {len(ctx["undefined_acronyms"])}')

    # 2. RegexDetector v2.8 적용
    det = RegexDetector()
    detections = []
    for r in eval_rows:
        s = r['sentence']
        result = det.detect(s, ctx)
        flags = {c: int(result.flags.get(c, {}).get('detected', 0)) for c in SMELL_CODES}
        has_smell = int(any(flags.values()))
        smell_list = [c for c in SMELL_CODES if flags[c]]
        detections.append({
            'doc_id': r['doc_id'], 'source': r['source'], 'sentence': s,
            'has_smell': has_smell, 'smell_codes': ', '.join(smell_list),
            **flags,
        })

    # 3. CSV 출력
    out_csv = out_dir / 'all_detection.csv'
    with open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
        cols = ['doc_id', 'source', 'sentence', 'has_smell', 'smell_codes'] + SMELL_CODES
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for d in detections:
            w.writerow(d)
    print(f'\n  → {out_csv}')

    # 4. 문서별 통계
    by_doc = defaultdict(lambda: {'total': 0, 'smelly': 0, **{c: 0 for c in SMELL_CODES}})
    for d in detections:
        b = by_doc[d['doc_id']]
        b['total'] += 1
        b['smelly'] += d['has_smell']
        for c in SMELL_CODES:
            b[c] += d[c]
    doc_summary = out_dir / 'smell_summary_by_doc.csv'
    with open(doc_summary, 'w', encoding='utf-8-sig', newline='') as f:
        cols = ['doc_id', 'total', 'smelly', 'smell_ratio'] + SMELL_CODES
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for doc, b in sorted(by_doc.items(), key=lambda x: -x[1]['smelly']):
            row = {'doc_id': doc, 'total': b['total'], 'smelly': b['smelly'],
                   'smell_ratio': round(100 * b['smelly'] / max(b['total'], 1), 1)}
            for c in SMELL_CODES:
                row[c] = b[c]
            w.writerow(row)
    print(f'  → {doc_summary}')

    # 5. 전체 통계 + Markdown 리포트
    total = len(detections)
    smelly = sum(d['has_smell'] for d in detections)
    counts = Counter()
    for d in detections:
        for c in SMELL_CODES:
            if d[c]:
                counts[c] += 1

    report = out_dir / 'report.md'
    with open(report, 'w', encoding='utf-8') as f:
        f.write(f'# RFP 2013 사례 평가 리포트 (KoFinRe v2.8)\n\n')
        f.write(f'> 데이터: `2013년 요구사항상세화 적용 발주 RFP사례.zip` — 14건 (HWP 13 + XLSX 1)\n')
        f.write(f'> Smell taxonomy: **19종** (Paska + IEEE 830 + ISO 29148 + INCOSE + EARS + CMMI + NCS)\n')
        f.write(f'> 평가 detector: RegexDetector v2.8 (단일, Rule-only baseline)\n\n')
        f.write(f'---\n\n## 개요\n\n')
        f.write(f'| 지표 | 값 |\n|---|---:|\n')
        f.write(f'| 평가 문장 (요구사항 후보) | {total} |\n')
        f.write(f'| Smell 1+ 검출 | {smelly} |\n')
        f.write(f'| Smell 검출률 | {round(100*smelly/max(total,1),1)}% |\n')
        f.write(f'| 깨끗한 문장 | {total - smelly} |\n')
        f.write(f'| 미정의 약어 (전체 문서) | {len(ctx["undefined_acronyms"])} |\n\n')

        f.write(f'## Smell 유형별 검출량 (19종)\n\n')
        f.write(f'| Code | 한국어 | 검출 건수 | 비율 |\n|---|---|---:|---:|\n')
        for c in SMELL_CODES:
            cnt = counts[c]
            f.write(f'| {c} | {SMELL_NAMES[c]} | {cnt} | {round(100*cnt/max(total,1),1)}% |\n')

        f.write(f'\n## 문서별 Smell 비율 (Top 10)\n\n')
        f.write(f'| 문서 | 총 | Smell | 비율 |\n|---|---:|---:|---:|\n')
        for doc, b in sorted(by_doc.items(), key=lambda x: -x[1]['smelly'])[:10]:
            ratio = round(100 * b['smelly'] / max(b['total'], 1), 1)
            f.write(f'| {doc[:60]} | {b["total"]} | {b["smelly"]} | {ratio}% |\n')

        # Smell 그룹별 합계 (3 그룹)
        g1 = ['S1','S2','S3','S4','S5','S6','S7','S8','S9','S10']
        g2 = ['S11','S12','S13','S14','S15']
        g3 = ['S16','S17','S18','S19']
        f.write(f'\n## 표준 그룹별 분포\n\n')
        f.write(f'| 그룹 | Smell | 총 검출 | 평균 비율 |\n|---|---|---:|---:|\n')
        for label, gs in [('핵심 10종 (Paska + 한국 특화)', g1),
                          ('확장 5종 (ISO/INCOSE/EARS)', g2),
                          ('CMMI/NCS 4종 (v2.8 신규)', g3)]:
            grp_sum = sum(counts[c] for c in gs)
            grp_avg = round(grp_sum / len(gs), 1)
            grp_codes = ', '.join(gs)
            f.write(f'| {label} | {grp_codes} | {grp_sum} | {grp_avg} |\n')

        f.write(f'\n## 가장 자주 나타난 Smell Top 5\n\n')
        top5 = sorted(counts.items(), key=lambda x: -x[1])[:5]
        f.write(f'| 순위 | Code | 한국어 | 건수 |\n|---|---|---|---:|\n')
        for i, (c, n) in enumerate(top5, 1):
            f.write(f'| {i} | {c} | {SMELL_NAMES[c]} | {n} |\n')

        # Smell 동시 발생 (조합)
        combo = Counter()
        for d in detections:
            codes = tuple(c for c in SMELL_CODES if d[c])
            if len(codes) >= 2:
                combo[codes] += 1
        f.write(f'\n## Smell 동시 발생 패턴 Top 5\n\n')
        f.write(f'| 조합 | 건수 |\n|---|---:|\n')
        for codes, n in combo.most_common(5):
            f.write(f'| {", ".join(codes)} | {n} |\n')

        # 미정의 약어
        if ctx['undefined_acronyms']:
            f.write(f'\n## 미정의 영문 약어 (상위 30)\n\n')
            f.write(', '.join(sorted(list(ctx['undefined_acronyms']))[:30]) + '\n')

        f.write(f'\n---\n\n## 표준 매핑\n\n')
        f.write(f'본 평가는 **KoFinRe v2.8 — 19종 smell taxonomy**를 적용했으며,\n')
        f.write(f'6대 요구공학 표준과 정렬되어 있습니다:\n\n')
        f.write(f'- **IEEE 830-1998**: S3·S5·S9·S14 (좋은 SRS 8 특성)\n')
        f.write(f'- **ISO 29148:2018**: S1·S6·S11·S16·S17 (요구사항 품질 9 특성)\n')
        f.write(f'- **INCOSE Guide**: S3·S11·S12·S13·S15 (11 작성 결함)\n')
        f.write(f'- **EARS (Mavin 2009)**: S14 (5 패턴 분석)\n')
        f.write(f'- **CMMI V2.0 REQM/RD**: S1·S16·S17·S18 (9 원칙)\n')
        f.write(f'- **NCS 5 제약 카테고리**: S19 — TECH/BIZ/COMP/OPS/SEC 분류 보조\n')

        f.write(f'\n## 데이터셋 의의\n\n')
        f.write(f'본 데이터셋(`2013년 요구사항상세화 적용 발주 RFP사례`)은 \n')
        f.write(f'**요구사항 상세화 관행 시범 사례 (양식 우수 포함)** 로 공개된 자료입니다.\n')
        f.write(f'본 평가는 v2.8 19종 기준으로 우수 양식 사례에서도 어떤 작성 패턴이\n')
        f.write(f'표준 관점에서 미달인지를 정량 확인하는 데 의의가 있습니다.\n')

    print(f'  → {report}')
    print(f'\n=== 핵심 요약 ===')
    print(f'  평가: {total} 문장 / Smell: {smelly} ({round(100*smelly/max(total,1),1)}%)')
    print(f'  Top 5: {[c for c, _ in sorted(counts.items(), key=lambda x:-x[1])[:5]]}')


if __name__ == '__main__':
    main()
