"""Ensemble voting — 복수 detector 결과 결합 (논문 Stage 3 마지막).

Voting 방식:
- majority: 과반 detector 동의
- rule_priority: Regex가 HIGH면 그대로, 아니면 다른 detector 보조
- confidence_weighted: confidence 가중 평균 ≥ 임계값
"""
from typing import List, Dict, Any, Literal
from .detectors.base import DetectorResult


SMELL_CODES = ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]


def vote_majority(results: List[DetectorResult], code: str) -> Dict[str, Any]:
    detected = [r.flags[code]["detected"] for r in results if code in r.flags]
    if not detected:
        return {"detected": 0, "confidence": 0.0, "votes": 0}
    pos = sum(detected)
    n = len(detected)
    return {
        "detected": int(pos > n / 2),
        "confidence": pos / n,
        "votes": pos,
        "total": n,
    }


def vote_rule_priority(results: List[DetectorResult], code: str,
                       regex_name: str = "regex") -> Dict[str, Any]:
    """규칙 기반 결과가 HIGH면 우선, 아니면 다른 detector 결합."""
    regex_res = next((r for r in results if r.flags.get(code) and getattr(r, 'name', '') == regex_name), None)
    # detector 이름은 클래스 속성, DetectorResult에는 없으므로 별도로 전달 필요
    # 단순화: results 순서 [regex, morph, chunk, dict, llm] 가정
    if len(results) == 0:
        return {"detected": 0, "confidence": 0.0}

    reg = results[0].flags.get(code, {"detected": 0, "confidence": 0.0})
    if reg["confidence"] >= 0.85:
        return {"detected": reg["detected"], "confidence": reg["confidence"],
                "decided_by": "regex_high"}

    # 나머지 detector 중 1+가 detected이면 결합
    other_pos = sum(r.flags.get(code, {}).get("detected", 0) for r in results[1:])
    other_avg_conf = (sum(r.flags.get(code, {}).get("confidence", 0) for r in results[1:])
                     / max(len(results) - 1, 1))

    if reg["detected"] or other_pos > 0:
        combined_conf = max(reg["confidence"], other_avg_conf)
        return {"detected": 1, "confidence": combined_conf,
                "decided_by": "regex+others" if reg["detected"] else "others"}
    return {"detected": 0, "confidence": 0.0, "decided_by": "all_negative"}


def vote_confidence_weighted(results: List[DetectorResult], code: str,
                             threshold: float = 0.5,
                             weights: Dict[str, float] = None) -> Dict[str, Any]:
    weights = weights or {}
    weighted_sum = 0.0
    weight_total = 0.0
    for i, r in enumerate(results):
        f = r.flags.get(code, {})
        w = weights.get(str(i), 1.0)
        weighted_sum += f.get("confidence", 0.0) * f.get("detected", 0) * w
        weight_total += w
    score = weighted_sum / max(weight_total, 1e-9)
    return {
        "detected": int(score >= threshold),
        "confidence": score,
    }


def ensemble(results: List[DetectorResult],
             method: Literal["majority","rule_priority","confidence_weighted"] = "rule_priority",
             **kwargs) -> Dict[str, Dict[str, Any]]:
    """입력: 한 문장에 대한 detector 결과 리스트. 출력: smell code → 최종 판정."""
    fn = {
        "majority": vote_majority,
        "rule_priority": vote_rule_priority,
        "confidence_weighted": vote_confidence_weighted,
    }[method]
    return {code: fn(results, code, **kwargs) if method != "rule_priority" else fn(results, code)
            for code in SMELL_CODES}
