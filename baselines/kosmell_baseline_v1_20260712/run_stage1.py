"""Stage 1 — Paska 변형 규칙 기반 1차 도출 (K1~K11).

기존 v2.8 detector 산출(S-코드)을 K-코드로 매핑하고, K8(비요구사항)은
전용 휴리스틱으로 판정한다. 전수 14,278건 대상.

입력 (로컬 전용, 커밋 금지):
    ../../data_d6_input.csv                      — segment_id/project/module/sentence
    ../../results_d6/ensemble_smell_labels.csv   — v2.8 앙상블 S1~S19

출력:
    stage1_labels.csv          — 행별 K1~K11 (로컬 전용: sentence 미포함이므로 커밋 가능)
    stage1_stats.json          — 전체·프로젝트별 통계 (커밋 대상)
    stage2_sample.csv          — LLM 평가용 층화 표본 (sentence 포함 → 로컬 전용)

Usage:
    python run_stage1.py [--sample-size 300] [--seed 42]
"""
from __future__ import annotations
import argparse
import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

S2K = {"S1": "K1", "S2": "K2", "S5": "K3", "S10": "K4", "S9": "K5",
       "S4": "K6", "S8": "K7", "S3": "K9", "S6": "K10", "S7": "K11"}
K_CODES = ["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9", "K10", "K11"]

# K8 비요구사항 휴리스틱: 의무·기능 서술이 전혀 없는 행
DUTY_RE = re.compile(r"(한다|된다|함|됨|해야|하여야|되어야|할 수 있|제공|지원|처리|관리|등록|조회|출력|생성|저장|연계|구축|개발)")
NOISE_RE = re.compile(r"^(목\s*차|개\s*요|참\s*고|비\s*고|주\s*의|안\s*내|별\s*첨|첨\s*부|배\s*경)")


def is_k8_not_requirement(sentence: str) -> int:
    s = sentence.strip()
    if NOISE_RE.match(s):
        return 1
    if not DUTY_RE.search(s):
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-size", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    inp = list(csv.DictReader(open(REPO / "data_d6_input.csv", encoding="utf-8-sig")))
    ens = list(csv.DictReader(open(REPO / "results_d6" / "ensemble_smell_labels.csv", encoding="utf-8-sig")))
    assert len(inp) == len(ens), (len(inp), len(ens))
    print(f"loaded {len(inp)} rows")

    rows = []
    for a, b in zip(inp, ens):
        r = {"segment_id": a["segment_id"], "project": a["project"], "module": a["module"]}
        for scode, kcode in S2K.items():
            r[kcode] = int(b[scode])
        r["K8"] = is_k8_not_requirement(a["sentence"])
        r["any_smell"] = int(any(r[k] for k in K_CODES))
        rows.append(r)

    # stage1_labels.csv — sentence 미포함 (커밋 가능)
    with open(HERE / "stage1_labels.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["segment_id", "project", "module"] + K_CODES + ["any_smell"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})

    # stats
    total = len(rows)
    by_k = {k: sum(r[k] for r in rows) for k in K_CODES}
    per_proj = defaultdict(Counter)
    for r in rows:
        c = per_proj[r["project"]]
        c["n"] += 1
        c["any"] += r["any_smell"]
        for k in K_CODES:
            c[k] += r[k]

    stats = {
        "design": "KoSmell Stage 1 — Paska-adapted rules (K1-K11)",
        "total": total,
        "any_smell": sum(r["any_smell"] for r in rows),
        "pct_any": round(100 * sum(r["any_smell"] for r in rows) / total, 1),
        "by_smell": by_k,
        "by_smell_pct": {k: round(100 * by_k[k] / total, 1) for k in K_CODES},
        "per_project": {
            p: {"n": per_proj[p]["n"], "pct_any": round(100 * per_proj[p]["any"] / per_proj[p]["n"], 1)}
            for p in sorted(per_proj)
        },
        "seed": args.seed,
    }
    json.dump(stats, open(HERE / "stage1_stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # Stage 2 stratified sample (sentence 포함 → 로컬 전용)
    rng = random.Random(args.seed)
    by_project = defaultdict(list)
    for a in inp:
        by_project[a["project"]].append(a)
    sample = []
    for p in sorted(by_project):
        pool = by_project[p]
        quota = max(10, round(args.sample_size * len(pool) / total))
        quota = min(quota, len(pool))
        sample.extend(rng.sample(pool, quota))
    # 초과분 절삭 (프로젝트 순서 편향 방지 셔플)
    rng.shuffle(sample)
    sample = sample[: args.sample_size]

    with open(HERE / "stage2_sample.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["segment_id", "project", "module", "sentence"])
        w.writeheader()
        w.writerows(sample)

    print(f"Stage1: any-smell {stats['pct_any']}%")
    for k in K_CODES:
        print(f"  {k}: {by_k[k]} ({stats['by_smell_pct'][k]}%)")
    print(f"Stage2 sample: {len(sample)} rows (seed={args.seed}) -> stage2_sample.csv [LOCAL ONLY]")


if __name__ == "__main__":
    main()
