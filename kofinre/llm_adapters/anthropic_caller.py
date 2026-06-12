"""Anthropic Claude API 어댑터.

요구사항:
- pip install anthropic
- 환경변수 ANTHROPIC_API_KEY 또는 인스턴스 생성 시 api_key 전달
- 기본 모델: claude-opus-4-7 (2026.01 시점 최신 Opus)
"""
import os
import json
from typing import Optional, Callable


class AnthropicCaller:
    """LLMDetector·LLMCorrector에 전달하기 위한 caller 객체.

    호출:
        caller(prompt: str) -> str
    """

    DEFAULT_MODEL = 'claude-opus-4-7'

    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = DEFAULT_MODEL,
                 max_tokens: int = 2048,
                 system: Optional[str] = None,
                 dry_run: bool = False):
        """
        Args:
            api_key: ANTHROPIC_API_KEY (None이면 환경변수에서 자동)
            model: claude-opus-4-7 / claude-sonnet-4-6 / claude-haiku-4-5-20251001
            max_tokens: 응답 최대 토큰
            system: 시스템 프롬프트
            dry_run: True면 실제 호출 안 하고 mock 응답 반환 (개발·CI 용)
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.model = model
        self.max_tokens = max_tokens
        self.system = system or "You are a Korean RFP requirements quality reviewer. Respond in valid JSON."
        self.dry_run = dry_run or not self.api_key
        self._client = None
        if not self.dry_run:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                # 패키지 부재 시 자동 dry_run
                self.dry_run = True

    def __call__(self, prompt: str) -> str:
        """프롬프트 → 응답 텍스트."""
        if self.dry_run:
            return self._mock_response(prompt)

        msg = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system,
            messages=[{"role": "user", "content": prompt}],
        )
        # content는 보통 [TextBlock(text=...)]
        return msg.content[0].text if msg.content else ""

    def _mock_response(self, prompt: str) -> str:
        """API 키 없을 때 dummy 응답 (smell 모두 false / 교정은 원문 반환)."""
        if '교정' in prompt or 'correct' in prompt.lower():
            return json.dumps({
                "corrected": ["(dry-run: 실제 교정 안 됨 — ANTHROPIC_API_KEY 설정 필요)"],
                "removed_smells": [],
                "semantic_preserved": True,
                "added_info": "",
                "rationale": "dry-run mode",
            }, ensure_ascii=False)
        # smell 검출 응답 dummy
        smells = {f"S{i}": {"detected": False, "confidence": 0.0,
                            "evidence": "dry-run"} for i in range(1, 11)}
        return json.dumps(smells, ensure_ascii=False)


def make_caller(provider: str = 'anthropic', **kwargs) -> Callable[[str], str]:
    """프로바이더별 caller 팩토리.

    Args:
        provider: 'anthropic' (현재 지원). 추후 openai 추가 예정.
    """
    if provider == 'anthropic':
        return AnthropicCaller(**kwargs)
    raise ValueError(f'unsupported provider: {provider}')
