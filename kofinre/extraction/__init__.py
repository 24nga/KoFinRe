"""Stage 1 — 텍스트 추출 + 문장 분리 + 요구사항 후보 필터."""
from .signatures import detect_kind, FileKind
from .document_extractor import (
    extract_html, extract_pdf, extract_hwp, extract_rtf, extract_docx,
    extract_by_signature,
)
from .sentence_splitter import split_sentences, is_meaningful
from .requirement_filter import is_requirement, FilterReason

__all__ = [
    "detect_kind", "FileKind",
    "extract_html", "extract_pdf", "extract_hwp", "extract_rtf", "extract_docx",
    "extract_by_signature",
    "split_sentences", "is_meaningful",
    "is_requirement", "FilterReason",
]
