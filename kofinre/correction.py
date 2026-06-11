"""Stage 5 LLM 교정 — 논문 6원칙 기반 교정 도구 (골격).

교정 원칙 (논문 6개):
1. 원문 의미 유지
2. 원문에 없는 기능·조건·정책·인터페이스·데이터 항목 추가 금지
3. 한 요구사항 = 하나의 기능/품질 (원자성)
4. 모호 표현 → 검증 가능 표현
5. 주체·조건·행위·대상·결과 명확화
6. 교정 전후 의미 차이·추가정보 기록
"""
from dataclasses import dataclass
from typing import Callable, List, Optional, Dict


CORRECTION_PROMPT = """당신은 한국어 RFP 요구사항 교정 전문가입니다.

아래 요구사항을 교정하세요. 다음 6개 원칙을 반드시 지키세요:

1. 원문 의미를 유지합니다.
2. 원문에 없는 기능, 조건, 정책, 인터페이스, 데이터 항목을 추가하지 않습니다.
3. 하나의 요구사항은 하나의 기능 또는 품질조건만 포함하도록 분리합니다.
4. 모호한 표현("적절히", "필요한", "실시간" 등)은 검증 가능한 표현으로 바꿉니다.
5. 주체, 조건, 행위, 대상, 결과를 명확히 드러냅니다.
6. 교정 전후의 의미 차이와 추가정보 여부를 기록합니다.

탐지된 smell: {smells}
원문: {original}

JSON으로만 반환:
{{
  "corrected": ["교정된 요구사항 1", "교정된 요구사항 2 (분리됐을 때만)"],
  "removed_smells": ["S1", "S3", ...],
  "semantic_preserved": true,
  "added_info": "(추가된 정보가 있으면 명시. 없으면 빈 문자열)",
  "rationale": "교정 사유 1문장"
}}
"""


@dataclass
class CorrectionResult:
    original: str
    detected_smells: List[str]
    corrected: List[str]
    removed_smells: List[str]
    semantic_preserved: bool
    added_info: str
    rationale: str
    error: Optional[str] = None

    def to_dict(self):
        return {
            "original": self.original,
            "detected_smells": self.detected_smells,
            "corrected": self.corrected,
            "removed_smells": self.removed_smells,
            "semantic_preserved": self.semantic_preserved,
            "added_info": self.added_info,
            "rationale": self.rationale,
            "error": self.error,
        }


class LLMCorrector:
    def __init__(self, llm_caller: Optional[Callable[[str], str]] = None,
                 cache_path: str = None):
        """
        Args:
            llm_caller: prompt(str) → response(str)
            cache_path: 결과 캐시 (재실행 비용 절감)
        """
        import json
        self.llm_caller = llm_caller
        self.cache_path = cache_path
        self._cache = {}
        if cache_path:
            try:
                self._cache = json.load(open(cache_path, encoding='utf-8'))
            except Exception:
                self._cache = {}

    def correct(self, sentence: str, detected_smells: List[str]) -> CorrectionResult:
        import json
        key = f"{sentence}||{','.join(sorted(detected_smells))}"
        if key in self._cache:
            d = self._cache[key]
            return CorrectionResult(**d)

        if self.llm_caller is None:
            return CorrectionResult(
                original=sentence,
                detected_smells=detected_smells,
                corrected=[sentence],
                removed_smells=[],
                semantic_preserved=True,
                added_info="",
                rationale="LLM 비활성 — 원문 반환",
                error="llm_disabled",
            )

        prompt = CORRECTION_PROMPT.format(
            smells=", ".join(detected_smells), original=sentence
        )
        try:
            response = self.llm_caller(prompt)
            data = json.loads(response.strip())
            result = CorrectionResult(
                original=sentence,
                detected_smells=detected_smells,
                corrected=data.get("corrected", [sentence]),
                removed_smells=data.get("removed_smells", []),
                semantic_preserved=data.get("semantic_preserved", True),
                added_info=data.get("added_info", ""),
                rationale=data.get("rationale", ""),
            )
            self._cache[key] = result.to_dict()
            if self.cache_path:
                json.dump(self._cache, open(self.cache_path, 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=2)
            return result
        except Exception as e:
            return CorrectionResult(
                original=sentence,
                detected_smells=detected_smells,
                corrected=[sentence],
                removed_smells=[],
                semantic_preserved=True,
                added_info="",
                rationale="",
                error=str(e),
            )

    def correct_batch(self, items: List[Dict]) -> List[CorrectionResult]:
        """items: [{'sentence': str, 'detected_smells': [str]}, ...]"""
        return [self.correct(it["sentence"], it["detected_smells"]) for it in items]
