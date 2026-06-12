"""휴리스틱 기반 자동 교정 — LLM 없이도 작동.

원칙은 LLM 교정과 동일:
1. 원문 의미 유지
2. 추가 정보 금지
3. 원자성 (1요구사항 = 1기능)
4. 모호 표현 → 검증가능 표현
5. 주체·조건·행위·대상·결과 명확화
6. 차이 기록

구현 한계: 정규식·치환만 가능. 의미 분석은 불가.
LLM 어댑터(`correction.py`)와 병행 가능.
"""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class HeuristicCorrection:
    original: str
    corrected: List[str]
    applied_rules: List[str]
    notes: str = ''


# ─── 변환 규칙 ───

VAGUE_REPLACEMENTS = {
    '실시간으로': '[명세 필요: 응답시간 임계값]',
    '신속히': '[명세 필요: 시간 기준]',
    '신속하게': '[명세 필요: 시간 기준]',
    '효율적으로': '[명세 필요: 측정 기준]',
    '효율적': '[명세 필요: 효율 측정 기준]',
    '효과적으로': '[명세 필요: 측정 기준]',
    '적절히': '[명세 필요: 적정 기준]',
    '적절한': '[명세 필요: 적정 기준]',
    '안정적으로': '[명세 필요: 가용성 SLO]',
    '안정적': '[명세 필요: 가용성 SLO]',
    '필요한 경우': '[명세 필요: 조건]',
    '충분한': '[명세 필요: 충분 기준]',
    '체계적으로': '[명세 필요: 측정 기준]',
    '원활하게': '[명세 필요: 측정 기준]',
    '원활히': '[명세 필요: 측정 기준]',
}


def fix_S3_vague(s: str) -> tuple:
    """모호어 → [명세 필요] 마커. 작성자가 직접 채워야 함."""
    applied = []
    out = s
    for term, replacement in VAGUE_REPLACEMENTS.items():
        if term in out:
            out = out.replace(term, replacement)
            applied.append(f'{term}→측정기준요청')
    return out, applied


def fix_S4_weak(s: str) -> tuple:
    """평서형 → 의무형. ~한다/된다 → ~해야 한다/되어야 한다."""
    applied = []
    out = s
    # 종결 패턴 변환
    end_replacements = [
        (r'(?<=[가-힣])한다([\.\s]*)$', r'해야 한다\1'),
        (r'(?<=[가-힣])된다([\.\s]*)$', r'되어야 한다\1'),
        (r'(?<=[가-힣])함([\.\s]*)$', r'하여야 함\1'),
        (r'(?<=[가-힣])됨([\.\s]*)$', r'되어야 함\1'),
    ]
    for pat, rep in end_replacements:
        new = re.sub(pat, rep, out)
        if new != out:
            applied.append('S4:평서형→의무형')
            out = new
            break
    return out, applied


def fix_S8_coordination(s: str) -> tuple:
    """범위 모호 — '등을' → [열거 명시] 마커."""
    applied = []
    out = re.sub(r'(\S+),\s*(\S+)\s*등을\s', r'\1, \2 [열거 명시 필요]을 ', s)
    if out != s:
        applied.append('S8:등을→[열거명시필요]')
    return out, applied


def fix_S1_nonatomic(s: str) -> tuple:
    """복합의무 — '및/그리고' 으로 결합된 의무 분리. 여러 요구사항으로 split."""
    parts = re.split(r'(?:해야 한다|하여야 한다|되어야 한다)\s*(?:고|며|,)\s*(?=[가-힣])', s)
    if len(parts) > 1:
        out = []
        for i, p in enumerate(parts[:-1]):
            out.append(p.strip() + '해야 한다.')
        out.append(parts[-1].strip())
        return out, ['S1:복합의무→분리']
    return [s], []


def heuristic_correct(sentence: str, detected_smells: List[str]) -> HeuristicCorrection:
    """smell 검출된 요구사항에 대해 휴리스틱 교정 적용."""
    out_sents = [sentence]
    rules = []

    # S1 — 분리 (여러 문장 결과)
    if 'S1' in detected_smells:
        new_sents = []
        for s in out_sents:
            parts, applied = fix_S1_nonatomic(s)
            new_sents.extend(parts)
            rules.extend(applied)
        out_sents = new_sents

    # 나머지는 각 문장에 적용
    final = []
    for s in out_sents:
        cur = s
        if 'S3' in detected_smells:
            cur, applied = fix_S3_vague(cur)
            rules.extend(applied)
        if 'S4' in detected_smells:
            cur, applied = fix_S4_weak(cur)
            rules.extend(applied)
        if 'S8' in detected_smells:
            cur, applied = fix_S8_coordination(cur)
            rules.extend(applied)
        final.append(cur)

    return HeuristicCorrection(
        original=sentence,
        corrected=final,
        applied_rules=rules,
        notes='heuristic — 의미 분석 없이 패턴 치환. 작성자 검토 필요'
    )
