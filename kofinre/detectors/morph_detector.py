"""Morphological analyzer detector — 형태소·품사·종결어미 (v2.1 골격).

논문: 형태소, 품사, 종결어미, 조사, 명사구 후보 분석

현재는 정규식·접미사 기반 가벼운 휴리스틱. v2.1에서 KoNLPy/Mecab 통합 예정.
"""
import re
from typing import Dict, Any
from .base import BaseDetector, DetectorResult, Confidence


# 종결어미 분류
DECLARATIVE_END = re.compile(r'(한다|된다|이다|있다|없다)\.?\s*$')
IMPERATIVE_END = re.compile(r'(해야 한다|하여야 한다|되어야 한다|할 수 있어야)')
INTERROGATIVE_END = re.compile(r'(인가|있는가|되는가)\?$')

# 조사 — 주어 마커
NOM_PARTICLE = re.compile(r'[가-힣]+(이|가|은|는)\s')
OBJ_PARTICLE = re.compile(r'[가-힣]+(을|를)\s')


class MorphDetector(BaseDetector):
    name = "morph"

    def detect(self, sentence: str, doc_context: Dict[str, Any] = None) -> DetectorResult:
        s = sentence
        res = DetectorResult(sentence=s)

        has_nom = NOM_PARTICLE.search(s) is not None
        has_obj = OBJ_PARTICLE.search(s) is not None
        has_imp = IMPERATIVE_END.search(s) is not None
        has_decl = DECLARATIVE_END.search(s) is not None

        # S5 보강 — 주격 조사 부재
        if has_imp and not has_nom:
            res.set("S5", True, Confidence.MEDIUM, "주격 조사 없음")
        else:
            res.set("S5", False)

        # S2 보강 — 목적 조사(`~을/를`) 없이 의무 표현
        if has_imp and not has_obj:
            res.set("S2", True, Confidence.MEDIUM, "목적 조사 없음")
        else:
            res.set("S2", False)

        # S4 보강 — 평서형 종결 + 의무 표현 부재
        if has_decl and not has_imp:
            res.set("S4", True, Confidence.MEDIUM, "평서형 종결")
        else:
            res.set("S4", False)

        # 나머지는 morph로는 검출 어려움
        for c in ["S1","S3","S6","S7","S8","S9","S10"]:
            res.set(c, False)

        res.meta = {"has_nom": has_nom, "has_obj": has_obj, "has_imp": has_imp}
        return res
