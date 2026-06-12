"""LLM API 어댑터 — Anthropic / OpenAI / 로컬 모델 호환 인터페이스.

기본: Anthropic Claude (claude-opus-4-7 등). 환경 변수 ANTHROPIC_API_KEY 필수.

사용:
    from kofinre.llm_adapters import AnthropicCaller
    caller = AnthropicCaller(model='claude-opus-4-7')
    response = caller(prompt='Hello')
"""
from .anthropic_caller import AnthropicCaller, make_caller

__all__ = ['AnthropicCaller', 'make_caller']
