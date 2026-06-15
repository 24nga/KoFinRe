"""Domain dictionary detector — 금융기관·업무·약어 사전 기반 (v2.1 골격).

논문 Stage 3: 'Domain Dictionary Detector — 금융기관, 업무, 데이터, 인터페이스, 약어 사전'
"""
import re
from typing import Dict, Any
from .base import BaseDetector, DetectorResult, Confidence


# 한국 금융 도메인 키워드 사전
FIN_INSTITUTIONS = {
    '한국은행','한국주택금융공사','한국자산관리공사','한국수출입은행',
    '한국거래소','한국예탁결제원','금융결제원','한국투자공사','예금보험공사',
    '주택도시보증공사','신용보증기금','기술보증기금','금융위원회','금융감독원',
    'KB','신한','우리','하나','농협','IBK','SC','씨티',
}

FIN_DOMAIN_TERMS = {
    # 업무
    '여신','수신','외환','지급결제','자금세탁방지','신용평가','담보','보증','채권','이자',
    '리스크','신용','시장','운영','유동성','자본',
    # 데이터·인터페이스
    'CB','신용정보','계좌','거래','이체','승인','정산','조회','연계',
}

DATA_TERMS = re.compile(r'(데이터|마스터|메타|로그|스키마|테이블|컬럼|키|인덱스|뷰)')
INTERFACE_TERMS = re.compile(r'(API|인터페이스|연계|채널|엔드포인트|메시지|전문|프로토콜)')
QUALITY_TERMS = re.compile(r'(가용성|확장성|성능|보안|장애|복구|이중화|백업|복원|모니터링)')


class DictionaryDetector(BaseDetector):
    name = "dictionary"

    def detect(self, sentence: str, doc_context: Dict[str, Any] = None) -> DetectorResult:
        s = sentence
        res = DetectorResult(sentence=s)

        # 도메인 신호 — 요구사항임을 시사하는 보조 신호 (smell 직접 검출 X)
        has_inst = any(i in s for i in FIN_INSTITUTIONS)
        has_dom = any(t in s for t in FIN_DOMAIN_TERMS)
        has_data = DATA_TERMS.search(s) is not None
        has_iface = INTERFACE_TERMS.search(s) is not None
        has_qual = QUALITY_TERMS.search(s) is not None

        # 품질 속성 관련 표현이 있지만 정량 부재 → S6 보조 신호
        if has_qual:
            from .regex_detector import NUMBER_RE
            if NUMBER_RE.search(s) is None:
                res.set("S6", True, Confidence.LOW, "품질속성 키워드 + 정량 부재")
            else:
                res.set("S6", False)
        else:
            res.set("S6", False)

        # 나머지는 직접 검출 안 함 (signal만 meta에 저장)
        for c in ["S1","S2","S3","S4","S5","S7","S8","S9","S10",
                  "S11","S12","S13","S14","S15",
                  "S16","S17","S18","S19"]:
            res.set(c, False)

        res.meta = {
            "has_institution": has_inst,
            "has_domain": has_dom,
            "has_data": has_data,
            "has_interface": has_iface,
            "has_quality": has_qual,
        }
        return res
