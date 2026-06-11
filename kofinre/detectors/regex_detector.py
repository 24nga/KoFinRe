"""Regex-based detector — S1~S10 모두 (정규식·키워드 기반).

논문 Stage 3 의 'Regex-based Detector' 역할:
- 의무 표현, 모호어, 정량부재, 약어 등 명시적 패턴 탐지
- HIGH confidence: 명확한 패턴 매칭
- MEDIUM confidence: 휴리스틱 매칭
- LOW confidence: 약한 신호
"""
import re
from collections import Counter
from typing import Dict, Any, Set
from .base import BaseDetector, DetectorResult, Confidence


# ───────────────── S3 Ambiguous Term — 어휘 모호 ─────────────────
VAGUE_TERMS = {
    '필요한','적절한','적정한','신속한','신속히','신속하게','효율적','효과적','충분한','충분히',
    '원활','원활히','원활한','다양한','다수의','양호한','우수한','적합한','가능한 한',
    '적시','적시에','안정적','안정적인','안정적으로','편리한','편리하게','용이한','용이하게',
    '간편한','간편하게','최적','최적의','최적화','체계적','체계적으로','신뢰성','신뢰성 있는',
    '유연한','유연하게','광범위','광범위한','폭넓은','폭넓게','포괄적','포괄적으로',
    '대규모','대량','대용량','소규모','약간','대체로','추후','향후',
    '주기적','주기적으로','정기적','정기적으로','실시간',
}

# ───────────────── S8 Coordination Ambiguity — 범위 모호 ─────────────────
COORD_RE = re.compile(
    r'(및\s*\/\s*또는|등을|등의|등에|등 ?\(|포함\s+(?!한다)|관련(?:한|된)\s+(?!기관))'
)

# ───────────────── S9 Passive voice ─────────────────
PASSIVE_RE = re.compile(
    r'(되어야\s*한다|되어야\s*함|지원되어야|구현되어야|제공되어야|보장되어야|적용되어야|'
    r'관리되어야|구축되어야|반영되어야|표시되어야|저장되어야|처리되어야|확보되어야|'
    r'수행되어야|배포되어야|기록되어야|연계되어야|되도록)'
)

# ───────────────── S1 Non-atomic / S4 Weak Obligation 종결 ─────────────────
STRONG_DUTY_RE = re.compile(
    r'(?:하|되|이|있)여야\s*(?:한다|함|됨)'
    r'|해야\s*(?:한다|함)'
    r'|할\s*수\s*있어야\s*(?:한다|함)'
    r'|반드시\s+[가-힣]+'
    r'|필수\s*(?:이다|로|적|항목)'
    r'|의무\s*(?:이다|적|로)'
    r'|[가-힣]+토록\s*한다'
)
WEAK_DUTY_END = re.compile(r'(한다|된다|함|됨)[\s\.]*$')

# ───────────────── S5 Missing Actor ─────────────────
SUBJECT_RE = re.compile(r'^[가-힣A-Za-z0-9\s\(\)\[\]\-_]+(가|이|은|는|에서|이며)\s')

# 의무 표현 앞쪽 N 글자에 시스템 명사가 있으면 주체 있음으로 판정
SYSTEM_ACTOR_NOUN = re.compile(
    r'(?:^|[\s\(])'
    r'(본\s*시스템|본\s*사업|본\s*모듈|본\s*서비스|시스템|모듈|서비스|애플리케이션|'
    r'클라이언트|서버|사용자|관리자|운영자|개발자|이용자|고객|'
    r'발주\s*기관|제안사|수행사|발주자|발주처|관리\s*화면|화면)'
    r'[가-힣]*\s*(?:은|는|이|가|에서|이며|에서는)?'
)

# 동사 명사형 (의무 표현 직전에 와야 함). 더 단순·확장 패턴.
ACTION_NOUN_BEFORE_DUTY = re.compile(
    r'(개발|구축|운영|관리|처리|지원|제공|수행|반영|연계|적용|분석|점검|모니터링|'
    r'배포|등록|수정|삭제|조회|저장|기록|표시|보고|보호|암호화|전송|수집|구성|설계|'
    r'구현|작성|준수|보장|확보|보유|갖춤|제출|기술|제시|포함|마련|확인)'
    r'\s*(?:하|되|이|있)여야'
)

# ───────────────── S6 Missing Quantification ─────────────────
PERF_KEYS = re.compile(r'(성능|속도|처리량|응답시간|동시접속|건수|TPS|처리율|용량|대수|초당|분당|시간당|정확도|가용성)')
NUMBER_RE = re.compile(r'\d+\s*(개|건|초|분|시간|일|년|GB|MB|TB|만|억|명|건/초|TPS|%|밀리초|ms)')

# ───────────────── S7 Undefined Acronym ─────────────────
ACRONYM_RE = re.compile(r'\b[A-Z]{2,6}\b')
DEFINED_RE = re.compile(r'([A-Z]{2,6})\s*[:：]\s*[^,;\n]+|[\(（]\s*([A-Z]{2,6})\s*[\)）]|([A-Z]{2,6})\s*[\(（]')
WHITELIST = {
    # 일반 ICT
    'RFP','ICT','IT','OS','PC','DB','API','UI','UX','AI','ML','ETL','DR','OK','URL','HTTP','HTTPS',
    'JSON','XML','HTML','CSS','JS','SQL','PDF','HWP','SMS','SSO','VPN','LDAP','WAS','WAF','PMO','SI',
    'SW','HW','LAN','WAN','GUI','CLI','CPU','RAM','SSD','HDD','USB','LTS','RPA','NLP','EAI','ESB','MQ',
    'MSA','MOU','SLA','KPI','EOL','EOS','EOD','SoC','GPS','TCP','UDP','IP','RFC','SDK','IDE','BMT','POC',
    # 한국 금융기관
    'NHN','SK','KT','LG','MS','IBM','HP','AWS','GCP','HF','BOK','HUG','KRX','KIC','KIBO','KDIC','KODIT',
    'KAMCO','KFTC','KSD','VOC','ECOS','CBDC','ARS','SIEM','MES','LLM','GPU','CPU',
    # 금융 도메인
    'NPL','EVR','SRA','SRS','BSC','BCP','MFA','PKI','OAUTH','OAUTH2','JWT','REST','SOAP','GRPC','CRUD',
    'HCS','MDM','EDI','HRMS','ERP','SCM','CRM','CMS','PMS','ITSM','ITIL','DEVOPS',
    'CB','NICE','KCB','DSR','DTI','VIN','CMS','PEP','EDD','KYC','STR','CTR','FATF','KOFIU','AML','PB','RM',
    'AUC','KS','ROC','AES','AES256','ETF','ELS','MLOPS',
    # 노이즈 빈출
    'META','PROJECT','CD','CI','CO','KR','KO','DO','OR','OF','BY','NO','ID','VS','PM','AM','PL',
    'TV','UP','PER','HEX','MIN','MAX','SUM','AVG',
}

# ───────────────── S10 Unverifiable — 정성 표현 ─────────────────
QUALITATIVE_RE = re.compile(r'(효율적|효과적|안정적|신뢰성|편리|용이|간편|최적|체계적|원활|유연)')


def collect_undefined_acronyms(text: str) -> Set[str]:
    """문서 단위 — 등장 약어 중 정의되지 않은 것."""
    all_a = set(ACRONYM_RE.findall(text))
    defined = set()
    for m in DEFINED_RE.finditer(text):
        for g in m.groups():
            if g: defined.add(g)
    return all_a - defined - WHITELIST


class RegexDetector(BaseDetector):
    name = "regex"

    def detect(self, sentence: str, doc_context: Dict[str, Any] = None) -> DetectorResult:
        s = sentence
        res = DetectorResult(sentence=s)
        ctx = doc_context or {}
        undef_acrs = ctx.get('undefined_acronyms', set())

        # S1 Non-atomic — 의무 표현 2회 이상
        duty_count = len(STRONG_DUTY_RE.findall(s))
        res.set("S1", duty_count >= 2, Confidence.HIGH if duty_count >= 2 else 0.0,
                f"의무표현 {duty_count}회")

        # S2 Incomplete — 정밀화: 의무 표현 + 목적 조사 부재 + 동사 명사형도 부재
        has_duty = STRONG_DUTY_RE.search(s) is not None
        # 부사·복합어 사이에 끼는 경우 허용
        has_object = re.search(r'(을|를)\s+(?:[가-힣\s]+?)(?:해야|하여야|할\s*수\s*있어야)', s) is not None
        has_action_noun = ACTION_NOUN_BEFORE_DUTY.search(s) is not None
        # 조건절(~경우)만 있고 결과 부재 케이스
        only_condition = re.search(r'\s*경우$|할\s*때\s*$|발생\s*시\s*$', s) is not None and not has_duty
        # 의무 표현은 있는데 대상도, 동사 명사형도 없을 때만 검출
        incomplete = (has_duty and not has_object and not has_action_noun) or only_condition
        res.set("S2", incomplete, Confidence.MEDIUM if incomplete else 0.0,
                "대상·행위 부재" if has_duty and not has_object and not has_action_noun
                else "조건만" if only_condition else "")

        # S3 Ambiguous term — 어휘 모호
        vague_hits = [t for t in VAGUE_TERMS if t in s]
        res.set("S3", bool(vague_hits), Confidence.HIGH if vague_hits else 0.0,
                "|".join(vague_hits))

        # S4 Weak Obligation — 평서형 종결 + 강한 의무 없음 + 수동태 없음
        weak = (WEAK_DUTY_END.search(s) is not None
                and STRONG_DUTY_RE.search(s) is None
                and PASSIVE_RE.search(s) is None)
        res.set("S4", weak, Confidence.HIGH if weak else 0.0, "평서형 종결")

        # S5 Missing Actor — 정밀화: 의무 표현 직전 30자 내 시스템 명사 있으면 false
        has_duty_match = STRONG_DUTY_RE.search(s)
        if has_duty_match:
            duty_start = has_duty_match.start()
            preceding = s[:duty_start]
            # 조사 포함 시스템 주체 후보 검사
            has_system_actor = SYSTEM_ACTOR_NOUN.search(preceding) is not None
            # 일반 명사구 주어 (SUBJECT_RE)
            has_general_subject = SUBJECT_RE.match(s) is not None
            missing_actor = not has_system_actor and not has_general_subject
        else:
            missing_actor = False
        res.set("S5", missing_actor, Confidence.MEDIUM if missing_actor else 0.0,
                "주체 후보 부재")

        # S6 Missing Quantification — 성능 키워드 + 숫자 없음
        missing_quant = PERF_KEYS.search(s) is not None and NUMBER_RE.search(s) is None
        res.set("S6", missing_quant, Confidence.HIGH if missing_quant else 0.0,
                "성능 키워드 + 정량 부재")

        # S7 Undefined Acronym — 문서 단위 약어 컨텍스트 사용
        in_sent = [a for a in undef_acrs if a in s]
        res.set("S7", bool(in_sent), Confidence.HIGH if in_sent else 0.0, "|".join(in_sent))

        # S8 Coordination Ambiguity — 범위 모호
        coord = COORD_RE.search(s) is not None
        res.set("S8", coord, Confidence.MEDIUM if coord else 0.0,
                COORD_RE.search(s).group() if coord else "")

        # S9 Passive — 수동/주체 흐림
        passive = PASSIVE_RE.search(s) is not None
        res.set("S9", passive, Confidence.HIGH if passive else 0.0,
                PASSIVE_RE.search(s).group() if passive else "")

        # S10 Unverifiable — 정성 표현 + 측정 기준 부재
        has_qualitative = QUALITATIVE_RE.search(s) is not None
        has_measure = NUMBER_RE.search(s) is not None
        unverifiable = has_qualitative and not has_measure
        res.set("S10", unverifiable, Confidence.MEDIUM if unverifiable else 0.0,
                QUALITATIVE_RE.search(s).group() if unverifiable else "")

        return res
