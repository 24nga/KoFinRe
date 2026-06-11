"""요구사항 정밀 필터 — 포함·제외·약관 6 카테고리.

논문 Stage 1 의 'sentence_candidates.csv → requirement_candidates.csv' 단계.

`exclusion_reason.csv` 추적용으로 컷 사유를 반환.
"""
import re
from enum import Enum
from typing import Tuple


class FilterReason(str, Enum):
    PASS = "pass"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    HARD_NOISE = "hard_noise"             # 사이트 푸터·약관·VAT 등
    BID_NOISE = "bid_noise"               # 조달·입찰 표준 문구
    META_START = "meta_start"             # 사업명·연락처 등 메타 시작
    LEADING_BULLET = "leading_bullet"     # 글머리표 단편
    EVAL_CRITERIA = "eval_criteria"       # ~을 평가한다
    LEGAL_DOMAIN = "legal_domain"         # 임차인·보증금 + 시스템명사 없음
    NO_REQ_ENDING = "no_req_ending"       # 의무 종결어 부재


# ────────────── 필수 종결어 (논문 표준) ──────────────
REQ_END = re.compile(
    r'(?:하|되|이|있)여야\s*(?:한다|함|됨)'
    r'|해야\s*(?:한다|함)'
    r'|할\s*수\s*있어야\s*(?:한다|함)'
    r'|반드시\s+[가-힣]+'
    r'|필수\s*(?:이다|로|적|항목)'
    r'|의무\s*(?:이다|적|로)'
    r'|[가-힣]+토록\s*한다'
)

EVAL_RE = re.compile(r'(?:을|를)\s*평가한다|점검한다(?:\s*\.|\s*$)|배점')

HARD_NOISE = re.compile(
    r'(패밀리사이트|COPYRIGHT|All Rights Reserved|사이트맵|'
    r'페이지로 이동|이전 페이지|다음 페이지|마지막 페이지|처음 페이지|'
    r'용어사전|약관|개인정보처리방침|이용약관|'
    r'부가가치세|부가세 포함|부가세|VAT|'
    r'대표전화|대표\s*FAX|대표\s*Tel|'
    r'사업자등록번호|사업자번호|'
    r'홈페이지\s*주소|이메일\s*주소)',
    re.IGNORECASE
)

BID_NOISE = re.compile(
    r'(입찰자|공동수급체|입찰서|낙찰|청렴계약|'
    r'입찰\s*보증금|하자보수\s*보증금|이행보증|계약보증금|'
    r'조달청|나라장터|수요기관|발주처|공고번호|예가범위|투찰|'
    r'사업자등록증|법인등기부등본|대리인|임직원|이의\s*제기|'
    r'국가계약법|지방계약법|조의\s*2|특수조건|기초금액|예정\s*금액|추정\s*금액|'
    r'적격심사|제안서평가|입찰\s*등록|입찰\s*참여|입찰\s*참가|입찰\s*공고|'
    r'전자입찰|구매결의|입찰\s*설명서|공고서|과업내용서|입찰\s*안내|'
    r'적격심사기준|평가관련|연락처는|휴대폰\s*번호|'
    r'재직증명서|참석자\s*전원|주민등록증|운전면허증|여권|신분증|'
    r'재무현황|당기순이익|자기자본순이익률|순\s*현금흐름|'
    r'법\s*제\s*\d+조|미래창조과학부고시|소프트웨어사업의\s*하도급)'
)

LEADING_NOISE = re.compile(
    r'^(\s*[▶○●◇□■◐·\-•▪－–—]\s*|'
    r'\s*[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]\s*\.?\s|'
    r'\s*[ㅇㅁ]\s+|'
    r'\s*\d+\s*[\.\)]\s*$|'
    r'\s*\d+\s*-\s*\d+\s*$|'
    r'\s*\[\s*양식|\s*\(\s*양식)'
)

META_START = re.compile(
    r'^\s*(사업명|사업\s*기간|사업\s*예산|사업\s*목적|사업\s*개요|사업\s*범위|사업\s*요약|'
    r'추진\s*일정|주요\s*일정|입찰\s*일정|계약\s*방식|선정\s*방식|'
    r'발주\s*기관|발주처|문의처|담당자|연락처|연락\s*처|전화\s*번호|팩스|이메일|주소|'
    r'첨부|별첨|붙임|참고|참조|주\s*[\:\)]|※|'
    r'양식\s*\d|별표\s*\d|기타\s*사항|재무현황|재무\s*상태|구\s*분\s*M|'
    r'I+\s|II+\s|III+\s|IV\s|V\s|VI\s|VII\s|VIII\s|IX\s|X\s)'
)

SYSTEM_NOUN = re.compile(
    r'(시스템|기능|서비스|모듈|화면|메뉴|데이터|보고서|성능|보안|장애|장비|인프라|'
    r'사용자|관리자|운영자|개발자|이용자|고객|업무\s*담당|발주자|수행사|'
    r'인터페이스|API|UI|UX|DB|네트워크|서버|클라이언트|소프트웨어|하드웨어|'
    r'요구사항|기준|조건|규격|항목|품질|운영|구축|개발|연계|이중화|백업|'
    r'제안사|제안서|용역|사업|구성|배포|아키텍처|클라우드|온프레미스)'
)

LEGAL_DOMAIN = re.compile(
    r'(임차인|임대인|보증금|채권|법원|배당|이자|손해배상|채무|보증보험|'
    r'상속|배우자|증여|이행청구|반환|소송|제소|민법|약관|규정|시행령)'
)


def is_requirement(s: str,
                   min_len: int = 20,
                   max_len: int = 350) -> Tuple[bool, FilterReason]:
    """판정 + 컷 사유 반환 (exclusion_reason.csv 추적용)."""
    s = s.strip()
    if len(s) < min_len:
        return False, FilterReason.TOO_SHORT
    if len(s) > max_len:
        return False, FilterReason.TOO_LONG
    if HARD_NOISE.search(s):
        return False, FilterReason.HARD_NOISE
    if BID_NOISE.search(s):
        return False, FilterReason.BID_NOISE
    if LEADING_NOISE.match(s):
        return False, FilterReason.LEADING_BULLET
    if META_START.match(s):
        return False, FilterReason.META_START
    if EVAL_RE.search(s):
        return False, FilterReason.EVAL_CRITERIA
    if not REQ_END.search(s):
        return False, FilterReason.NO_REQ_ENDING
    # 약관 도메인 + 시스템 명사 없음
    if LEGAL_DOMAIN.search(s) and not SYSTEM_NOUN.search(s):
        return False, FilterReason.LEGAL_DOMAIN
    return True, FilterReason.PASS
