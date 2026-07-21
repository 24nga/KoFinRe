"""Detector 단위 테스트 — 정답 라벨이 있는 짧은 예제 기반."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.detectors import RegexDetector
from kofinre.detectors.regex_detector import collect_undefined_acronyms


class TestRegexDetector(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_s3_ambiguous(self):
        s = "시스템은 적절한 응답시간을 보장한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S3']['detected'], 'S3 모호어 검출 실패')

    def test_s4_weak_obligation(self):
        s = "이력 정보를 저장한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S4']['detected'], 'S4 약한의무 검출 실패')

    def test_s8_coordination_ambiguity(self):
        s = "인증, 권한관리 등을 지원해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S8']['detected'], 'S8 범위모호 검출 실패')

    def test_s9_passive(self):
        s = "보고서는 자동으로 생성되어야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S9']['detected'], 'S9 수동표현 검출 실패')

    def test_s10_unverifiable(self):
        s = "시스템은 효율적으로 운영되어야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S10']['detected'], 'S10 검증불가 검출 실패')

    def test_clean_requirement(self):
        s = "신용점수 조회는 NICE를 통해 수행하여야 하며, 응답시간은 200ms 이하여야 한다."
        # 화이트리스트에 NICE 포함 + 정량값 명시 → S6/S10/S3 false
        r = self.det.detect(s, self.ctx)
        # 적어도 S6 정량부재는 false 이어야 함
        self.assertFalse(r.flags['S6']['detected'], 'S6 false positive')


class TestS1CategoryConditional(unittest.TestCase):
    """S1 카테고리 조건부 적용 (v2.9.3)."""
    def setUp(self):
        self.det = RegexDetector()

    def test_intra_clause_compound_flags_s1(self):
        # 묶음 마커 없는 단일 절 내 복합 의무(종결형 2회) → RFP에서도 S1
        s = "시스템은 사용자를 인증해야 한다 그리고 접근 권한을 부여해야 한다"
        r = self.det.detect(s, {'category': 'rfp'})
        self.assertTrue(r.flags['S1']['detected'], 'RFP 절내 복합 의무 S1 검출 실패')

    def test_bundled_sub_items_not_s1_in_rfp(self):
        # 파이프 묶음으로 세부 나열 → RFP에서는 S1 제외
        s = "사용자 관리 | 사용자를 등록하여야 한다 | 사용자를 삭제하여야 한다"
        r = self.det.detect(s, {'category': 'rfp'})
        self.assertFalse(r.flags['S1']['detected'], 'RFP 묶음 구조가 S1으로 오검출됨')

    def test_bundled_sub_items_still_s1_in_spec(self):
        # 정의서(spec) 카테고리에서는 기존 로직 유지 (의무 2회 → S1)
        s = "사용자 관리 | 사용자를 등록하여야 한다 | 사용자를 삭제하여야 한다"
        r = self.det.detect(s, {'category': 'spec'})
        self.assertTrue(r.flags['S1']['detected'], 'spec 카테고리 S1 기존 로직 미유지')

    def test_bundled_no_id_attributed_to_s18(self):
        # RFP 묶음 + 파생 ID 부재 → S18 귀속
        s = "사용자 관리 | 사용자를 등록하여야 한다 | 사용자를 삭제하여야 한다"
        r = self.det.detect(s, {'category': 'rfp'})
        self.assertTrue(r.flags['S18']['detected'], '묶음+ID부재 S18 귀속 실패')


class TestUndefinedAcronyms(unittest.TestCase):
    def test_whitelist(self):
        text = "API와 JSON은 표준이다. XYZW는 정의 없이 등장한다."
        und = collect_undefined_acronyms(text)
        self.assertNotIn('API', und)
        self.assertNotIn('JSON', und)
        self.assertIn('XYZW', und)


if __name__ == '__main__':
    unittest.main()
