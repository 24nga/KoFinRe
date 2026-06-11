"""KoFinRe detectors — 5 analyzers for ensemble voting (논문 Stage 3)."""
from .base import BaseDetector, DetectorResult, Confidence
from .regex_detector import RegexDetector

# 골격 — v2.1에서 본격 구현
__all__ = ["BaseDetector", "DetectorResult", "Confidence", "RegexDetector"]
