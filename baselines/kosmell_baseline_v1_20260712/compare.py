"""Stage 3 — 규칙(Stage 1) vs LLM(Stage 2) 비교.

표본에 대해 K1~K11 스멜별로:
  % agreement, Cohen's kappa, McNemar (b vs c), Rule-only/LLM-only/Both/Neither 4분할

Usage:
    python compare.py --llm stage2_labels__claude-sonnet-4-6.csv
    python compare.py --llm stage2_labels__gemma4_12b.csv --out comparison__gemma.json
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
K_CODES = ["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9", "K10", "K11"]


def cohen_kappa(a: list[int], b: list[int]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa1 = sum(a) / n
    pb1 = sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if pe == 1.0:
        return float("nan")
    return (po - pe) / (1 - pe)


def mcnemar_p(b: int, c: int) -> float:
    """Exact binomial McNemar p-value (two-sided)."""
    n = b + c
    if n == 0:
        return float("nan")
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n) * 2
    return min(1.0, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", type=Path, default=HERE / "stage1_labels.csv")
    ap.add_argument("--llm", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    rule_rows = {r["segment_id"]: r for r in csv.DictReader(open(args.rule, encoding="utf-8-sig"))}
    llm_rows = list(csv.DictReader(open(args.llm, encoding="utf-8-sig")))
    paired = [(rule_rows[r["segment_id"]], r) for r in llm_rows if r["segment_id"] in rule_rows]
    print(f"paired: {len(paired)} (LLM rows: {len(llm_rows)})")

    result = {"n_paired": len(paired), "llm_file": args.llm.name, "per_smell": {}}
    print(f"{'K':<5}{'agree%':>8}{'kappa':>8}{'both':>6}{'rule':>6}{'llm':>6}{'none':>7}{'McNemar_p':>11}")
    for k in K_CODES:
        rule = [int(a[k]) for a, _ in paired]
        llm = [int(b[k]) for _, b in paired]
        both = sum(1 for x, y in zip(rule, llm) if x == 1 and y == 1)
        r_only = sum(1 for x, y in zip(rule, llm) if x == 1 and y == 0)
        l_only = sum(1 for x, y in zip(rule, llm) if x == 0 and y == 1)
        neither = len(paired) - both - r_only - l_only
        agree = (both + neither) / len(paired) * 100 if paired else float("nan")
        kap = cohen_kappa(rule, llm)
        p = mcnemar_p(r_only, l_only)
        result["per_smell"][k] = {
            "agreement_pct": round(agree, 1), "kappa": round(kap, 3),
            "both": both, "rule_only": r_only, "llm_only": l_only, "neither": neither,
            "mcnemar_p": round(p, 4) if not math.isnan(p) else None,
        }
        print(f"{k:<5}{agree:>7.1f}%{kap:>8.3f}{both:>6}{r_only:>6}{l_only:>6}{neither:>7}{p:>11.4f}")

    # any-smell level
    rule_any = [int(any(int(a[k]) for k in K_CODES)) for a, _ in paired]
    llm_any = [int(any(int(b[k]) for k in K_CODES)) for _, b in paired]
    result["any_smell"] = {
        "rule_pct": round(100 * sum(rule_any) / len(paired), 1),
        "llm_pct": round(100 * sum(llm_any) / len(paired), 1),
        "kappa": round(cohen_kappa(rule_any, llm_any), 3),
    }
    print(f"\nany-smell: rule {result['any_smell']['rule_pct']}% vs llm {result['any_smell']['llm_pct']}% (kappa {result['any_smell']['kappa']})")

    out = args.out or HERE / f"comparison__{args.llm.stem.replace('stage2_labels__', '')}.json"
    json.dump(result, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"saved: {out.name}")


if __name__ == "__main__":
    main()
