"""평가 지표 — 논문 Stage 4.

3 카테고리:
- Detection Performance (gold label 필요): Precision, Recall, F1, FPR, FNR, Cohen's Kappa, Macro-F1, Micro-F1
- Requirement Quality: Smell Density, Coverage, Average, Severe Ratio, Yield, Validity Rate
- Correction Effect (Stage 5): Smell Reduction, Quality Score Gain, Semantic Preservation, Over-correction, Atomicity Improvement, Testability Improvement
"""
from typing import List, Dict, Any
from collections import Counter


SMELL_CODES = ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]
SEVERE_SMELLS = ["S2","S6","S10"]  # 불완전·정량부재·검증불가


# ───────── Detection Performance (gold label vs prediction) ─────────

def confusion_matrix(gold: List[int], pred: List[int]) -> Dict[str, int]:
    tp = sum(1 for g, p in zip(gold, pred) if g == 1 and p == 1)
    fp = sum(1 for g, p in zip(gold, pred) if g == 0 and p == 1)
    fn = sum(1 for g, p in zip(gold, pred) if g == 1 and p == 0)
    tn = sum(1 for g, p in zip(gold, pred) if g == 0 and p == 0)
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn}


def precision_recall_f1(gold: List[int], pred: List[int]) -> Dict[str, float]:
    cm = confusion_matrix(gold, pred)
    tp, fp, fn, tn = cm["TP"], cm["FP"], cm["FN"], cm["TN"]
    p = tp / max(tp + fp, 1)
    r = tp / max(tp + fn, 1)
    f1 = 2 * p * r / max(p + r, 1e-9)
    fpr = fp / max(fp + tn, 1)
    fnr = fn / max(fn + tp, 1)
    return {"precision": p, "recall": r, "f1": f1, "fpr": fpr, "fnr": fnr, **cm}


def macro_f1(gold_per_smell: Dict[str, List[int]], pred_per_smell: Dict[str, List[int]]) -> Dict[str, Any]:
    per_smell = {}
    f1s = []
    for code in SMELL_CODES:
        g = gold_per_smell.get(code, [])
        p = pred_per_smell.get(code, [])
        if not g: continue
        m = precision_recall_f1(g, p)
        per_smell[code] = m
        f1s.append(m["f1"])
    return {"per_smell": per_smell, "macro_f1": sum(f1s) / max(len(f1s), 1)}


def micro_f1(gold_per_smell: Dict[str, List[int]], pred_per_smell: Dict[str, List[int]]) -> float:
    g_all, p_all = [], []
    for code in SMELL_CODES:
        g_all.extend(gold_per_smell.get(code, []))
        p_all.extend(pred_per_smell.get(code, []))
    return precision_recall_f1(g_all, p_all)["f1"]


def cohens_kappa(rater1: List[Any], rater2: List[Any]) -> float:
    """평가자 간 일치도. Cohen's kappa."""
    assert len(rater1) == len(rater2)
    n = len(rater1)
    if n == 0: return 0.0
    agree = sum(1 for a, b in zip(rater1, rater2) if a == b)
    po = agree / n
    # 우연 일치 기댓값
    counts1 = Counter(rater1); counts2 = Counter(rater2)
    pe = sum((counts1[k] / n) * (counts2[k] / n) for k in set(counts1) | set(counts2))
    if abs(1 - pe) < 1e-9: return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


# ───────── Requirement Quality Metrics ─────────

def quality_metrics(req_smells: List[Dict[str, int]],
                    total_sentences: int = None,
                    total_validated: int = None,
                    actual_requirements: int = None) -> Dict[str, float]:
    """
    Args:
        req_smells: 요구사항 리스트, 각 항목은 smell code → 0/1
        total_sentences: 추출 후보 문장 수 (Yield 산출용)
        total_validated: 수작업 검증한 문장 수
        actual_requirements: 검증 결과 실제 요구사항 수 (Validity 산출용)
    """
    n_req = len(req_smells)
    if n_req == 0:
        return {"smell_density": 0, "smell_coverage": 0, "avg_smell_per_req": 0,
                "severe_smell_ratio": 0}
    total_smells = sum(sum(r.get(c, 0) for c in SMELL_CODES) for r in req_smells)
    reqs_with_smell = sum(1 for r in req_smells if any(r.get(c, 0) for c in SMELL_CODES))
    severe_count = sum(sum(r.get(c, 0) for c in SEVERE_SMELLS) for r in req_smells)

    out = {
        "smell_density": total_smells / n_req,
        "smell_coverage": reqs_with_smell / n_req,
        "avg_smell_per_req": total_smells / n_req,
        "severe_smell_ratio": severe_count / max(total_smells, 1),
        "total_smells": total_smells,
        "total_requirements": n_req,
        "reqs_with_smell": reqs_with_smell,
    }
    if total_sentences:
        out["extraction_yield"] = n_req / total_sentences
    if total_validated and actual_requirements is not None:
        out["dataset_validity_rate"] = actual_requirements / total_validated
    return out


# ───────── Correction Effect (Stage 5) ─────────

def correction_metrics(before: List[Dict[str, int]],
                       after: List[Dict[str, int]],
                       semantic_preserved: List[bool] = None,
                       over_corrected: List[bool] = None) -> Dict[str, float]:
    """교정 전후 비교.

    Args:
        before: 교정 전 smell 플래그 리스트 (per requirement)
        after:  교정 후 동일
        semantic_preserved: 평가자가 의미 보존 OK 표시
        over_corrected: 원문에 없는 정보가 추가됨 표시
    """
    assert len(before) == len(after)
    n = len(before)
    smells_before = sum(sum(b.get(c, 0) for c in SMELL_CODES) for b in before)
    smells_after = sum(sum(a.get(c, 0) for c in SMELL_CODES) for a in after)
    quality_before = -smells_before  # 단순 정의: 음의 smell 수
    quality_after = -smells_after

    # 원자성 개선: S1 (Non-atomic)이 1 → 0
    atomicity_improved = sum(1 for b, a in zip(before, after)
                             if b.get("S1", 0) == 1 and a.get("S1", 0) == 0)
    # 검증가능성 개선: S6 또는 S10이 1 → 0
    testability_improved = sum(1 for b, a in zip(before, after)
                               if (b.get("S6", 0) == 1 and a.get("S6", 0) == 0)
                                  or (b.get("S10", 0) == 1 and a.get("S10", 0) == 0))

    out = {
        "smell_reduction_rate": (smells_before - smells_after) / max(smells_before, 1),
        "quality_score_gain": quality_after - quality_before,
        "atomicity_improvement_rate": atomicity_improved / max(sum(1 for b in before if b.get("S1", 0)), 1),
        "testability_improvement_rate": testability_improved / max(
            sum(1 for b in before if b.get("S6", 0) or b.get("S10", 0)), 1
        ),
        "smells_before": smells_before,
        "smells_after": smells_after,
        "total_corrected": n,
    }
    if semantic_preserved is not None:
        out["semantic_preservation_rate"] = sum(semantic_preserved) / max(len(semantic_preserved), 1)
    if over_corrected is not None:
        out["over_correction_rate"] = sum(over_corrected) / max(len(over_corrected), 1)
    return out
