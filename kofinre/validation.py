"""Manual Validation — 논문 Stage 4·평가자 검증 (골격).

논문 요구사항:
- 최소 2명 평가자 독립 판정
- Cohen's kappa
- 불일치 항목 합의 → gold label
- 최소 200건 표본, 층화추출 (smell 있음/없음)
"""
import csv
import random
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


SMELL_CODES = ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]


def stratified_sample(rows: List[Dict[str, Any]],
                     n_target: int = 200,
                     smell_col: str = "has_smell",
                     positive_ratio: float = 0.6,
                     seed: int = 42) -> List[Dict[str, Any]]:
    """smell 있음/없음 층화 표본 추출.

    Args:
        rows: 분석 결과
        n_target: 목표 표본 크기 (200)
        positive_ratio: smell 있는 항목 비율 (0.6 = 6:4)
    """
    random.seed(seed)
    pos = [r for r in rows if int(r.get(smell_col, 0)) == 1]
    neg = [r for r in rows if int(r.get(smell_col, 0)) == 0]

    n_pos = min(int(n_target * positive_ratio), len(pos))
    n_neg = min(n_target - n_pos, len(neg))

    return random.sample(pos, n_pos) + random.sample(neg, n_neg)


def create_validation_template(sample: List[Dict[str, Any]], out_path: Path,
                                rater_id: str = "R1"):
    """평가자가 입력할 CSV 양식 생성.

    각 행: rater 가 smell label (0/1) 입력
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["sample_id", "sentence", "rater_id"] + SMELL_CODES + ["is_requirement", "notes"]
    with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for i, r in enumerate(sample, 1):
            row = {"sample_id": f"V{i:04d}",
                   "sentence": r.get("sentence", "")[:500],
                   "rater_id": rater_id,
                   **{c: "" for c in SMELL_CODES},
                   "is_requirement": "",
                   "notes": ""}
            w.writerow(row)


def load_rater_results(rater_csv: Path) -> Dict[str, Dict[str, int]]:
    """평가자가 채운 CSV 로드. sample_id → {smell_code: 0/1}"""
    rows = list(csv.DictReader(open(rater_csv, encoding='utf-8-sig')))
    out = {}
    for r in rows:
        sid = r["sample_id"]
        out[sid] = {c: int(r[c]) if r[c] else 0 for c in SMELL_CODES}
        out[sid]["is_requirement"] = int(r.get("is_requirement", 0) or 0)
    return out


def compute_inter_rater_agreement(r1: Dict[str, Dict[str, int]],
                                   r2: Dict[str, Dict[str, int]]) -> Dict[str, float]:
    """평가자 2명의 결과로 smell 코드별 Cohen's kappa."""
    from .metrics import cohens_kappa

    common = set(r1) & set(r2)
    out = {}
    for code in SMELL_CODES + ["is_requirement"]:
        l1 = [r1[s].get(code, 0) for s in common]
        l2 = [r2[s].get(code, 0) for s in common]
        out[code] = cohens_kappa(l1, l2)
    return out


def consolidate_gold(r1: Dict[str, Dict[str, int]],
                    r2: Dict[str, Dict[str, int]],
                    disagreement_resolution: Dict[str, Dict[str, int]] = None) -> Dict[str, Dict[str, int]]:
    """평가자 합의 → gold label.

    Args:
        r1, r2: 두 평가자 결과
        disagreement_resolution: 불일치 항목에 대한 합의 결과 (없으면 r1·r2 모두 1일 때만 1)
    """
    common = set(r1) & set(r2)
    gold = {}
    for sid in common:
        gold[sid] = {}
        for code in SMELL_CODES + ["is_requirement"]:
            v1 = r1[sid].get(code, 0)
            v2 = r2[sid].get(code, 0)
            if v1 == v2:
                gold[sid][code] = v1
            else:
                if disagreement_resolution and sid in disagreement_resolution:
                    gold[sid][code] = disagreement_resolution[sid].get(code, 0)
                else:
                    gold[sid][code] = 0  # 보수적
    return gold
