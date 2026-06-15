"""LLM-assisted classifier — 규칙으로 판단 어려운 smell 보조 판정 (v2.1 골격).

논문 Stage 3: 'LLM-assisted Classifier — 규칙으로 판단하기 어려운 smell 후보의 보조 판정'

호출 인터페이스만 골격. v2.2에서 Anthropic/OpenAI/로컬 LLM 통합.
운영 비용·API 키 관리 위해 캐싱 권장.
"""
import json
from typing import Dict, Any, Callable, Optional
from .base import BaseDetector, DetectorResult, Confidence


PROMPT_TEMPLATE = """당신은 한국어 RFP 요구사항 품질 검토 전문가입니다.
아래 문장에 대해 10종 smell 검출을 수행하세요.

문장: "{sentence}"

각 smell에 대해 yes/no + confidence(0.0~1.0) + 근거 1문장을 JSON으로 반환:
{{
  "S1": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S2": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S3": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S4": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S5": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S6": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S7": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S8": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S9": {{"detected": false, "confidence": 0.0, "evidence": ""}},
  "S10": {{"detected": false, "confidence": 0.0, "evidence": ""}}
}}

smell 정의:
- S1 Non-atomic: 한 요구사항에 둘 이상 기능
- S2 Incomplete: 시스템 응답·행위·대상 불완전
- S3 Ambiguous: 적절히/필요한/실시간 등
- S4 Weak Obligation: 한다/된다 평서형
- S5 Missing Actor: 수행 주체 부재
- S6 Missing Quantification: 정량 기준 부재
- S7 Undefined Acronym: 정의 없는 약어
- S8 Coordination Ambiguity: 및/또는, 등, 포함
- S9 Passive: 처리되어야/관리되어야
- S10 Unverifiable: 검증 방법·판정 기준 불명

JSON만 반환하세요.
"""


class LLMDetector(BaseDetector):
    name = "llm"

    def __init__(self, llm_caller: Optional[Callable[[str], str]] = None, cache_path: str = None):
        """
        Args:
            llm_caller: prompt(str) → response(str) 함수. None이면 detect 시 비활성.
            cache_path: 결과 캐시 파일 (재실행 비용 절감)
        """
        self.llm_caller = llm_caller
        self.cache_path = cache_path
        self._cache = {}
        if cache_path:
            try:
                self._cache = json.load(open(cache_path, encoding='utf-8'))
            except Exception:
                self._cache = {}

    def detect(self, sentence: str, doc_context: Dict[str, Any] = None) -> DetectorResult:
        res = DetectorResult(sentence=sentence)
        # 캐시 hit
        if sentence in self._cache:
            for c, v in self._cache[sentence].items():
                res.set(c, v["detected"], v["confidence"], v.get("evidence", ""))
            res.meta["from_cache"] = True
            return res

        # LLM 비활성 시 모두 false
        if self.llm_caller is None:
            for c in ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10","S11","S12","S13","S14","S15"]:
                res.set(c, False)
            res.meta["llm_disabled"] = True
            return res

        prompt = PROMPT_TEMPLATE.format(sentence=sentence)
        try:
            response = self.llm_caller(prompt)
            data = json.loads(response.strip())
            for c, v in data.items():
                res.set(c, v.get("detected", False),
                        float(v.get("confidence", 0.0)),
                        v.get("evidence", ""))
            self._cache[sentence] = data
            if self.cache_path:
                json.dump(self._cache, open(self.cache_path, 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=2)
        except Exception as e:
            for c in ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10","S11","S12","S13","S14","S15"]:
                res.set(c, False)
            res.meta["error"] = str(e)

        return res
