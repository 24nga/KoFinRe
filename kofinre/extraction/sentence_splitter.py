"""문장 분리 + 1차 품질 필터.

분리자:
- 마침표/물음표/느낌표 + 공백 + 한글/대문자/괄호/숫자 시작
- 세미콜론(`;`) — REQ_abstract sub-requirement 패턴
- 하이픈 줄바꿈(`-\n`) → 결합
"""
import re
from typing import List


# 노이즈 라인 (목차, 번호만, 글머리표만)
NOISE_RE = re.compile(
    r'^(목\s*차|목차|작\s*성|개정\s*이력|개정이력|개\s*요|문\s*서\s*정\s*보|'
    r'^\d+\s*$|^[-·•▶▪○◇□■●◐－–—\s]+$|^\s*\d+(\.\d+)*\s*$|페\s*이\s*지|Page \d+|'
    r'^[가-힣A-Za-z]\.\s|^\s*[-－–—]\s|첨부)'
)


def split_sentences(text: str) -> List[str]:
    """한국어 + 영문 + 세미콜론 기준 분리."""
    text = re.sub(r'-\s*\n\s*', '', text)              # 하이픈 줄바꿈 결합
    text = re.sub(r'\s+', ' ', text)
    # 마침표·물음표·느낌표 + 한국어 종결
    parts = re.split(r'(?<=[\.!?。])\s+(?=[가-힣A-Z○●▶■◇\(\d])', text)
    # 세미콜론 분리 (REQ_abstract sub-req 패턴)
    out = []
    for p in parts:
        for sub in re.split(r'[;；]', p):
            sub = sub.strip()
            if sub:
                out.append(sub)
    return out


def is_meaningful(s: str, min_len: int = 10, max_len: int = 400,
                  min_hangul_ratio: float = 0.25) -> bool:
    """길이·한글 비율·노이즈 패턴 필터."""
    if not (min_len <= len(s) <= max_len):
        return False
    if NOISE_RE.search(s):
        return False
    hangul = sum(1 for ch in s if '가' <= ch <= '힣')
    if hangul / max(len(s), 1) < min_hangul_ratio:
        return False
    return True
