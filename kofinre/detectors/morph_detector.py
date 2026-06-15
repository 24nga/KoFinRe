"""Morphological analyzer detector — kiwipiepy 형태소 정밀 분석.

v2.6 (2026-06-12) 한국어 고도화:
- 종결어미 5단계 분류 (강한 의무 / 약한 의무 / 평서 / 명령 / 의문)
- 격조사 정밀 분류 (NOM/ACC/LOC/GEN/TOPIC)
- 부정·이중부정 검출 (S2 정밀화)
- 번역체 흔적 (RFP 품질 신호)
- 한국 RFP 도메인 어휘 활용 (korean_patterns 모듈 위임)

POS 태그 (세종):
- NNG/NNP: 명사
- JKS/JKO/JKB/JKG: 격조사
- JX: 보조사 (은/는/도/만)
- VV/VA/VX: 동사·형용사·보조용언
- EC/EF: 어미
- XSV: 동사 접미사
"""
import re
from typing import Dict, Any
from .base import BaseDetector, DetectorResult, Confidence
from .. import korean_patterns as kp


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


def analyze_with_kiwi(sentence: str) -> Dict[str, Any]:
    """kiwipiepy 형태소 분석 → 5 카테고리 신호 추출."""
    kiwi = _get_kiwi()
    tokens = kiwi.tokenize(sentence)

    # 카테고리별 카운트
    counts = {
        'nom_particle': 0,      # JKS — 이/가
        'acc_particle': 0,      # JKO — 을/를
        'topic_particle': 0,    # JX(은/는) — 보조사
        'loc_particle': 0,      # JKB — 에/에서
        'noun_count': 0,        # NNG/NNP
        'verb_count': 0,        # VV/VX
        'ending_imperative': 0, # EC 의무 어미
        'ending_declarative': 0, # EF 평서 어미
        'passive_marker': 0,    # 되 + 어미
    }

    prev_token = None
    for t in tokens:
        if t.tag in ('JKS',):
            counts['nom_particle'] += 1
        elif t.tag == 'JKO':
            counts['acc_particle'] += 1
        elif t.tag == 'JX' and t.form in ('은', '는'):
            counts['topic_particle'] += 1
        elif t.tag == 'JKB':
            counts['loc_particle'] += 1
        elif t.tag in ('NNG', 'NNP', 'NP'):
            counts['noun_count'] += 1
        elif t.tag in ('VV', 'VX', 'VA'):
            counts['verb_count'] += 1
            if t.form in ('되', '돼'):
                counts['passive_marker'] += 1
        elif t.tag == 'EC':
            if t.form in ('어야', '아야', '여야'):
                counts['ending_imperative'] += 1
        elif t.tag == 'EF':
            if any(p in t.form for p in ('어야', '아야', '여야')):
                counts['ending_imperative'] += 1
            elif t.form in ('다', 'ᆫ다', '는다', '함', '됨', '음'):
                counts['ending_declarative'] += 1
        prev_token = t

    # 패턴 모듈 호출 — 명사 직후 격조사 결합 확인
    has_noun_with_nom = (counts['noun_count'] >= 1
                         and (counts['nom_particle'] + counts['topic_particle']) >= 1)
    has_noun_with_acc = counts['noun_count'] >= 1 and counts['acc_particle'] >= 1

    # 의무 강도 분류 (korean_patterns 위임)
    obligation = kp.classify_obligation_strength(sentence)

    return {
        # 격조사·주체
        'has_subject_marker': has_noun_with_nom,
        'has_object_marker': has_noun_with_acc,
        'subject_marker_count': counts['nom_particle'] + counts['topic_particle'],
        'object_marker_count': counts['acc_particle'],
        # 의무 강도
        'obligation': obligation,
        'is_strong_obligation': obligation == 'strong',
        'is_declarative': obligation == 'declarative',
        # 수동
        'has_passive': counts['passive_marker'] > 0 or kp.has_passive_marker(sentence),
        # 도메인 신호
        'has_actor_keyword': kp.has_actor_keyword(sentence),
        # 보조 분석
        'has_negation_double': kp.has_double_negation(sentence),
        'has_translationese': kp.has_translationese(sentence),
        'noun_count': counts['noun_count'],
        'verb_count': counts['verb_count'],
        'token_count': len(tokens),
    }


class MorphDetector(BaseDetector):
    name = "morph"

    def __init__(self, use_kiwi: bool = True):
        self.use_kiwi = use_kiwi and HAS_KIWI

    def detect(self, sentence: str, doc_context: Dict[str, Any] = None) -> DetectorResult:
        s = sentence.strip()
        res = DetectorResult(sentence=s)

        # short bullet 스킵 (v2.2 일관성)
        if len(s) < 30:
            for c in ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]:
                res.set(c, False)
            res.meta = {"skip_reason": "short_bullet"}
            return res

        if not self.use_kiwi:
            for c in ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]:
                res.set(c, False)
            res.meta = {"skip_reason": "kiwi_unavailable"}
            return res

        try:
            a = analyze_with_kiwi(s)
        except Exception as e:
            for c in ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]:
                res.set(c, False)
            res.meta = {"error": str(e)}
            return res

        # ─── S2 Incomplete — 강한 의무 + 목적 부재 + 행위 동사 부재 ───
        # 명사 1+ 와 동사 1+ 모두 있어야 완전
        if a['is_strong_obligation']:
            target_missing = not a['has_object_marker']
            verb_missing = a['verb_count'] == 0
            if target_missing and verb_missing:
                res.set("S2", True, Confidence.HIGH, "kiwi:대상·행위 모두 부재")
            elif target_missing and a['noun_count'] < 2:
                res.set("S2", True, Confidence.MEDIUM, "kiwi:대상 명사구 부족")
            else:
                res.set("S2", False)
        else:
            res.set("S2", False)

        # ─── S4 Weak Obligation ───
        # 평서형 종결 + 강한 의무 없음 + 수동도 없음 + 이중부정도 없음
        if (a['is_declarative']
                and not a['is_strong_obligation']
                and not a['has_passive']
                and not a['has_negation_double']):
            res.set("S4", True, Confidence.HIGH, "kiwi:평서형 종결")
        else:
            res.set("S4", False)

        # ─── S5 Missing Actor ───
        # 강한 의무 + 주격·보조사 부재 + 주체 키워드도 부재
        if a['is_strong_obligation']:
            if not a['has_subject_marker'] and not a['has_actor_keyword']:
                res.set("S5", True, Confidence.HIGH, "kiwi:주체 조사·키워드 부재")
            else:
                res.set("S5", False)
        else:
            res.set("S5", False)

        # ─── S9 Passive ───
        if a['has_passive']:
            res.set("S9", True, Confidence.HIGH, "kiwi:수동 마커")
        else:
            res.set("S9", False)

        # ─── 나머지는 morph 단독 검출 어려움 ───
        for c in ["S1","S3","S6","S7","S8","S10",
                  "S11","S12","S13","S14","S15",
                  "S16","S17","S18","S19"]:
            res.set(c, False)

        # 메타 — 번역체·이중부정 등 추가 신호
        res.meta.update(a)
        if a['has_translationese']:
            res.meta['quality_signal'] = 'translationese_detected'
        if a['has_negation_double']:
            res.meta['quality_signal'] = (res.meta.get('quality_signal', '') + ' double_negation').strip()

        return res
