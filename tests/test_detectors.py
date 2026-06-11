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


class TestUndefinedAcronyms(unittest.TestCase):
    def test_whitelist(self):
        text = "API와 JSON은 표준이다. XYZW는 정의 없이 등장한다."
        und = collect_undefined_acronyms(text)
        self.assertNotIn('API', und)
        self.assertNotIn('JSON', und)
        self.assertIn('XYZW', und)


if __name__ == '__main__':
    unittest.main()
