"""RFP 요구사항 추출 실험 — 층화 표본 생성.

과제: RFP 문장 세그먼트가 '구조화 가능한 요구사항'인지 식별(추출).
  - 규칙 라벨: 요구사항 후보 필터 통과 여부 (기존 방식)
  - LLM 라벨: GPT-4o / Claude (본 실험에서 생성)

표본: 규칙 통과 / 미통과 각 100건 층화 (seed=42), 노이즈성 단문 제외.
"""
import csv, random, sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(r'C:\Users\heen1\Desktop\assist\KoFinRe_repo\experiments\rfp_2013_sample\stage1')
OUT = Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)

passed = set()
with open(BASE/'requirement_candidates.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        passed.add(r['sentence'].strip())

rows = list(csv.DictReader(open(BASE/'sentence_candidates.csv', encoding='utf-8-sig')))
# 최소 길이 필터 (표·머리글 파편 배제) — 추출 대상이 될 만한 문장만
cand = [r for r in rows if 15 <= len(r['sentence'].strip()) <= 400]

pass_rows = [r for r in cand if r['sentence'].strip() in passed]
fail_rows = [r for r in cand if r['sentence'].strip() not in passed]
print(f'candidates: {len(cand)} | rule-pass: {len(pass_rows)} | rule-fail: {len(fail_rows)}')

rng = random.Random(42)
sample = rng.sample(pass_rows, 100) + rng.sample(fail_rows, 100)
rng.shuffle(sample)

with open(OUT/'extraction_sample.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['seg_id', 'doc_id', 'rule_label', 'sentence'])
    for i, r in enumerate(sample, 1):
        rl = 1 if r['sentence'].strip() in passed else 0
        w.writerow([f'S{i:03d}', r['doc_id'], rl, r['sentence'].strip()])
print(f'wrote {len(sample)} rows -> extraction_sample.csv (rule-pass 100 / fail 100)')
