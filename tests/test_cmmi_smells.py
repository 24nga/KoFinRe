"""v2.8 CMMI/NCS 기반 신규 smell S16~S19 단위 테스트."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.detectors import RegexDetector
from kofinre import korean_patterns as kp


class TestS16NecessityUnclear(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_preferred_font(self):
        s = "본 시스템은 개발팀이 선호하는 특정 폰트를 강제로 사용해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S16']['detected'])

    def test_arbitrary(self):
        s = "운영자가 임의로 정한 알림 주기를 적용해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S16']['detected'])

    def test_business_justified(self):
        s = "본 시스템은 사용자 인증 강화를 위해 MFA를 적용해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S16']['detected'])


class TestS17FeasibilityConcern(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_100_percent_availability(self):
        s = "본 시스템은 100% 가용성을 보장해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S17']['detected'])

    def test_zero_seconds(self):
        s = "응답시간은 0초 이내로 유지해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S17']['detected'])

    def test_perfect_security(self):
        s = "본 시스템은 완벽한 보안을 적용해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S17']['detected'])

    def test_five_nines_excessive(self):
        s = "본 시스템은 99.9999% 가용성을 유지해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S17']['detected'])

    def test_realistic(self):
        s = "본 시스템은 월 가용성 99.9% 이상을 유지해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S17']['detected'])


class TestS18MissingTraceabilityID(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_missing_id(self):
        s = "본 시스템은 사용자 인증 기능을 제공하여야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S18']['detected'])

    def test_with_id_pattern(self):
        s = "FUNC-AUTH-001 본 시스템은 사용자 인증 기능을 제공하여야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S18']['detected'])

    def test_with_source(self):
        s = "본 시스템은 보안정책에 따라 사용자 인증을 제공하여야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S18']['detected'])


class TestS19ConstraintCategory(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_unclear_constraint(self):
        s = "본 사업은 일부 제약을 준수하여야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S19']['detected'])

    def test_tech_classified(self):
        s = "본 시스템은 Linux 환경에서 운영되어야 한다는 제약을 준수한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S19']['detected'])  # TECH 카테고리 매칭


class TestKoreanPatternsHelpers(unittest.TestCase):
    def test_classify_constraint_tech(self):
        cats = kp.classify_constraint_category("RHEL 8 환경에서 운영")
        self.assertIn('TECH', cats)

    def test_classify_constraint_biz(self):
        cats = kp.classify_constraint_category("일정 마감일은 2026년 6월")
        self.assertIn('BIZ', cats)

    def test_classify_constraint_comp(self):
        cats = kp.classify_constraint_category("개인정보보호법을 준수")
        self.assertIn('COMP', cats)

    def test_classify_constraint_ops(self):
        cats = kp.classify_constraint_category("24시간 365일 무중단 운영")
        self.assertIn('OPS', cats)

    def test_classify_constraint_sec(self):
        cats = kp.classify_constraint_category("MFA 적용 및 AES-256 암호화")
        self.assertIn('SEC', cats)


if __name__ == '__main__':
    unittest.main()
