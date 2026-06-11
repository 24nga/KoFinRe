"""파일 시그니처(magic byte) 기반 포맷 판별.

공공기관 사이트 자동 수집 시 `page.html`로 저장된 파일이 실제로는
PDF/HWP/ZIP인 경우가 빈번 → 확장자 신뢰 불가, 시그니처로 재판별.
"""
from enum import Enum
from pathlib import Path


class FileKind(str, Enum):
    PDF = "pdf"
    OLE2 = "ole2"          # HWP 5.x / DOC 97-2003
    HWP_ALT = "hwp_alt"    # 한컴 변형 (E9 A5 89 11 등)
    ZIP = "zip"            # HWPX / DOCX / ODT 등 OOXML
    HTML = "html"
    RTF = "rtf"
    UNKNOWN = "unknown"


def detect_kind(path) -> FileKind:
    """확장자 무시하고 시그니처로 실제 포맷 판별."""
    path = Path(path)
    head = path.read_bytes()[:8]

    if head.startswith(b'%PDF'):
        return FileKind.PDF
    if head.startswith(b'PK\x03\x04'):
        return FileKind.ZIP
    if head.startswith(b'\xd0\xcf\x11\xe0'):
        return FileKind.OLE2
    if head.startswith(b'\xe9\xa5\x89\x11'):
        return FileKind.HWP_ALT
    if head.startswith(b'{\\rtf'):
        return FileKind.RTF
    if head[:1] in (b'<', b'\n', b'\r') or head[:3] == b'\xef\xbb\xbf':
        return FileKind.HTML

    sample = path.read_bytes()[:512]
    if b'<html' in sample.lower():
        return FileKind.HTML

    return FileKind.UNKNOWN
