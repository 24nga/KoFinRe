"""Detector base class — 모든 분석기가 동일 인터페이스로 동작."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any


class Confidence(float, Enum):
    """탐지 confidence 표준 레벨 — voting 시 가중치로 사용."""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.9


@dataclass
class DetectorResult:
    """단일 문장에 대한 한 detector 결과.

    Attributes:
        sentence: 분석 대상 문장
        flags: smell code → (detected: bool, confidence: float, evidence: str)
        meta: detector 별 추가 정보
    """
    sentence: str
    flags: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def set(self, code: str, detected: bool, confidence: float = 0.0, evidence: str = ""):
        self.flags[code] = {"detected": int(detected), "confidence": float(confidence), "evidence": evidence}

    def any_smell(self) -> bool:
        return any(v["detected"] for v in self.flags.values())


class BaseDetector:
    """모든 detector의 부모. detect(sentence) → DetectorResult."""
    name = "base"

    def detect(self, sentence: str, doc_context: Dict[str, Any] = None) -> DetectorResult:
        raise NotImplementedError

    def detect_batch(self, sentences, doc_context: Dict[str, Any] = None):
        return [self.detect(s, doc_context) for s in sentences]
