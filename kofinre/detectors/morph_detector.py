"""Morphological analyzer detector — kiwipiepy (Kiwi C++) 기반 형태소 분석.

논문 Stage 3: 'Morphological Analyzer — 형태소, 품사, 종결어미, 조사, 명사구 후보 분석'

v2.3 (2026-06-12): kiwipiepy 통합. Java 불필요, pip install 만으로 설치.
kiwipiepy 미설치 환경에선 정규식 fallback 으로 동작.

POS 태그 (세종 태그셋):
- NNG: 일반명사
- NNP: 고유명사
- JKS: 주격조사 (이/가)
- JKO: 목적격조사 (을/를)
- JX:  보조사 (은/는/도/만)
- VV:  동사
- VA:  형용사
- XSV: 동사 접미사 (하-)
- EC:  연결어미 (어야, 며, 고)
- EF:  종결어미 (다, ㄴ다, 함)
- MM:  관형사 (본, 이)
"""
import re
from typing import Dict, Any, List, Tuple
from .base import BaseDetector, DetectorResult, Confidence


# ───────── kiwipiepy 가용성 체크 ─────────
try:
    from kiwipiepy import Kiwi
    _kiwi_singleton = None

    def _get_kiwi():
        global _kiwi_singleton
        if _kiwi_singleton is None:
            _kiwi_singleton = Kiwi()
        return _kiwi_singleton

    HAS_KIWI = True
except ImportError:
    HAS_KIWI = False


# ───────── Fallback 정규식 (kiwipiepy 부재 시) ─────────
DECLARATIVE_END = re.compile(r'(한다|된다|이다|있다|없다)\.?\s*$')
IMPERATIVE_END = re.compile(r'(해야 한다|하여야 한다|되어야 한다|할 수 있어야)')
NOM_PARTICLE = re.compile(r'[가-힣]+(이|가|은|는)\s')
OBJ_PARTICLE = re.compile(r'[가-힣]+(을|를)\s')


# ───────── kiwipiepy 기반 분석 ─────────
def analyze_with_kiwi(sentence: str) -> Dict[str, Any]:
    """문장 분석 결과 — 의무성·주체·대상·수동 여부."""
    kiwi = _get_kiwi()
    tokens = kiwi.tokenize(sentence)

    has_subject_particle = False     # JKS / JX 검출
    has_object_particle = False      # JKO 검출
    has_imperative_ending = False    # EF "어야 한다" 의무 종결
    has_declarative_ending = False   # EF 평서형 종결
    has_passive_marker = False       # "되" + EF/EC 수동 패턴
    has_noun_before_obj = False      # NNG + JKO 결합 (target 명확)
    has_noun_before_subj = False     # NNG + JKS/JX 결합 (actor 명확)

    prev_tag = None
    sentence_tail = ''.join(t.form for t in tokens[-6:])

    for i, t in enumerate(tokens):
        if t.tag == 'JKS' or (t.tag == 'JX' and t.form in ('은', '는')):
            has_subject_particle = True
            if prev_tag in ('NNG', 'NNP', 'NP'):
                has_noun_before_subj = True
        if t.tag == 'JKO':
            has_object_particle = True
            if prev_tag in ('NNG', 'NNP', 'NP'):
                has_noun_before_obj = True
        if t.tag == 'EF':
            if t.form in ('어야', '아야', '여야') or '어야' in t.form:
                has_imperative_ending = True
            elif t.form in ('다', 'ᆫ다', '는다', '함', '됨'):
                has_declarative_ending = True
        if t.tag == 'EC' and t.form in ('어야', '아야', '여야'):
            has_imperative_ending = True
        # 수동 — "되" + EF/EC
        if t.form in ('되', '돼') and t.tag in ('VV', 'VX'):
            has_passive_marker = True
        prev_tag = t.tag

    # "되어야 한다" / "되어야 함" 패턴 보완
    if '되어야' in sentence or '지원되어야' in sentence or '구현되어야' in sentence:
        has_passive_marker = True
    # "해야 한다 / 하여야 한다" 추가 확인
    if any(p in sentence for p in ('해야 한다', '하여야 한다', '해야 함', '하여야 함')):
        has_imperative_ending = True

    return {
        'has_subject': has_subject_particle or has_noun_before_subj,
        'has_object': has_object_particle or has_noun_before_obj,
        'has_imperative': has_imperative_ending,
        'has_declarative': has_declarative_ending,
        'has_passive': has_passive_marker,
        'has_noun_before_obj': has_noun_before_obj,
        'has_noun_before_subj': has_noun_before_subj,
        'token_count': len(tokens),
    }


class MorphDetector(BaseDetector):
    name = "morph"

    def __init__(self, use_kiwi: bool = True):
        self.use_kiwi = use_kiwi and HAS_KIWI

    def detect(self, sentence: str, doc_context: Dict[str, Any] = None) -> DetectorResult:
        s = sentence
        res = DetectorResult(sentence=s)

        # Fix #1 일관성 (v2.2): short fragment 는 평가 스킵
        if len(s.strip()) < 30:
            for c in ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]:
                res.set(c, False)
            res.meta = {"skip_reason": "short_bullet"}
            return res

        if self.use_kiwi:
            try:
                analysis = analyze_with_kiwi(s)
            except Exception as e:
                analysis = None
                res.meta['kiwi_error'] = str(e)
        else:
            analysis = None

        if analysis is None:
            # Fallback — 정규식 휴리스틱
            has_subject = NOM_PARTICLE.search(s) is not None
            has_object = OBJ_PARTICLE.search(s) is not None
            has_imperative = IMPERATIVE_END.search(s) is not None
            has_declarative = DECLARATIVE_END.search(s) is not None
            has_passive = '되어야' in s
            analysis = {
                'has_subject': has_subject,
                'has_object': has_object,
                'has_imperative': has_imperative,
                'has_declarative': has_declarative,
                'has_passive': has_passive,
                'has_noun_before_obj': has_object,
                'has_noun_before_subj': has_subject,
                'token_count': len(s.split()),
            }

        # ─────── Smell 판정 ───────

        # S2 Incomplete — 의무 표현 + 목적 부재 (target 없음)
        if analysis['has_imperative'] and not analysis['has_object']:
            res.set("S2", True, Confidence.HIGH, "kiwi: 의무+JKO부재")
        else:
            res.set("S2", False)

        # S5 Missing Actor — 의무 표현 + 주체 부재
        if analysis['has_imperative'] and not analysis['has_subject']:
            res.set("S5", True, Confidence.HIGH, "kiwi: 의무+주격조사부재")
        else:
            res.set("S5", False)

        # S4 Weak Obligation — 평서형 + 의무 부재 + 수동 부재
        if analysis['has_declarative'] and not analysis['has_imperative'] and not analysis['has_passive']:
            res.set("S4", True, Confidence.HIGH, "kiwi: 평서형 종결")
        else:
            res.set("S4", False)

        # S9 Passive — 수동 마커
        if analysis['has_passive']:
            res.set("S9", True, Confidence.HIGH, "kiwi: 수동 패턴")
        else:
            res.set("S9", False)

        # 나머지는 morph 단독 검출 어려움
        for c in ["S1","S3","S6","S7","S8","S10"]:
            res.set(c, False)

        res.meta.update(analysis)
        return res
