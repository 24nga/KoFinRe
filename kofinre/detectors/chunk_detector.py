"""Dependency / Chunk heuristic — 주체-행위-대상 구조 추정 (v2.1 골격).

논문 Stage 3: 'Dependency/Chunk Heuristic — 주체-행위-대상 구조 추정'

가벼운 명사구·동사구 휴리스틱. v2.1에서 KoNLPy 명사구 추출로 강화 예정.
"""
import re
from typing import Dict, Any
from .base import BaseDetector, DetectorResult, Confidence


# 주체 후보 (시스템·사용자 등)
ACTOR_CANDIDATES = re.compile(
    r'(시스템|모듈|서비스|애플리케이션|클라이언트|서버|사용자|관리자|운영자|개발자|이용자|고객|'
    r'본\s*사업|발주\s*기관|제안사|수행사|발주자)[가-힣]*\s*(?:가|이|은|는|에서)?'
)
ACTION_VERBS = re.compile(
    r'(처리|관리|지원|제공|수행|운영|구축|개발|연계|조회|등록|수정|삭제|출력|보고|분석|점검|모니터링|'
    r'생성|전송|수집|배포|반영|적용|구현|설계|구성|배치|보호|암호화|저장|기록|표시)'
)
TARGET_NOUN = re.compile(r'([가-힣A-Za-z0-9]+)(을|를)\s+')


class ChunkDetector(BaseDetector):
    name = "chunk"

    def detect(self, sentence: str, doc_context: Dict[str, Any] = None) -> DetectorResult:
        s = sentence
        res = DetectorResult(sentence=s)

        # Fix #1 (v2.2): short bullet (30자 미만)은 actor/target 검사 자체 스킵.
        # 양식 양상 "기능명" 키워드만 있는 fragment에서 자연스레 actor/target 부재 →
        # false positive 다수 발생. 의미 있는 의무 문장만 평가.
        if len(s.strip()) < 30:
            for c in ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]:
                res.set(c, False)
            res.meta = {"skip_reason": "short_bullet"}
            return res

        actor = ACTOR_CANDIDATES.search(s)
        action = ACTION_VERBS.search(s)
        target = TARGET_NOUN.search(s)

        # Fix #2 (v2.2): 목적 조사(`을/를`)가 본문 어느 곳에든 있으면 target 있음으로 인정.
        # TARGET_NOUN 정규식이 "X를 + 동사" 인접만 잡아서 부사·수식어가 끼면 놓치는 케이스 보완.
        if not target and __import__('re').search(r'(을|를)\s', s):
            target = True  # marker (실제 매칭 객체 아니어도 truthy)

        # S2 Incomplete — 주체/행위/대상 중 하나라도 부재
        missing = []
        if not actor: missing.append("주체")
        if not action: missing.append("행위")
        if not target: missing.append("대상")

        if missing and len(missing) >= 2:
            res.set("S2", True, Confidence.HIGH, f"{','.join(missing)} 누락")
        elif missing:
            res.set("S2", True, Confidence.MEDIUM, f"{','.join(missing)} 누락")
        else:
            res.set("S2", False)

        # S5 Missing Actor — 주체만 없을 때
        if not actor and (action or target):
            res.set("S5", True, Confidence.MEDIUM, "주체 후보 부재")
        else:
            res.set("S5", False)

        # 나머지는 chunk로는 검출 어려움
        for c in ["S1","S3","S4","S6","S7","S8","S9","S10","S11","S12","S13","S14","S15"]:
            res.set(c, False)

        res.meta = {
            "actor": actor.group() if actor else None,
            "action": action.group() if action else None,
            "target": (target.group(1) if hasattr(target, 'group') else 'particle-match')
                if target else None,
        }
        return res
