"""korean_patterns 모듈 단위 테스트."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre import korean_patterns as kp


class TestObligationClassification(unittest.TestCase):
    def test_strong(self):
        for s in ['시스템은 처리해야 한다.', '관리자는 등록하여야 함.', '반드시 검증한다.']:
            self.assertEqual(kp.classify_obligation_strength(s), 'strong', s)

    def test_weak(self):
        for s in ['제안서는 권장한다.', '권고된다.', '바람직하다.']:
            self.assertEqual(kp.classify_obligation_strength(s), 'weak', s)

    def test_declarative(self):
        for s in ['보고서는 생성한다.', '결과는 저장된다.']:
            self.assertEqual(kp.classify_obligation_strength(s), 'declarative', s)

    def test_imperative(self):
        for s in ['자료를 제출하라.', '확인하시오.']:
            self.assertEqual(kp.classify_obligation_strength(s), 'imperative', s)


class TestVagueTerms(unittest.TestCase):
    def test_lexical(self):
        hits = kp.find_vague_terms('시스템은 적절한 응답을 제공한다.')
        cats = set(c for c, _ in hits)
        self.assertIn('lexical', cats)

    def test_time(self):
        hits = kp.find_vague_terms('시스템은 실시간으로 처리한다.')
        cats = set(c for c, _ in hits)
        self.assertIn('time', cats)

    def test_quantifier(self):
        hits = kp.find_vague_terms('대부분의 요구를 충족한다.')
        cats = set(c for c, _ in hits)
        self.assertIn('quantifier', cats)


class TestQuantitativeUnit(unittest.TestCase):
    def test_with_unit(self):
        self.assertTrue(kp.has_quantitative_unit('응답시간은 200ms 이내여야 한다.'))
        self.assertTrue(kp.has_quantitative_unit('처리량은 1,000 TPS 이상이다.'))
        self.assertTrue(kp.has_quantitative_unit('100건/초 처리'))

    def test_without_unit(self):
        self.assertFalse(kp.has_quantitative_unit('빠른 응답을 제공한다.'))


class TestQualitativeUnverifiable(unittest.TestCase):
    def test_unverifiable(self):
        self.assertTrue(kp.is_qualitative_without_metric('시스템은 효율적으로 운영된다.'))

    def test_verifiable(self):
        self.assertFalse(kp.is_qualitative_without_metric('시스템은 99.9% 가용성을 유지한다.'))


class TestTranslationese(unittest.TestCase):
    def test_detect(self):
        # "기능을 가지다" — 영문 "have a function" 직역체
        self.assertTrue(kp.has_translationese('시스템은 기능을 가진다.'))

    def test_natural_korean(self):
        self.assertFalse(kp.has_translationese('시스템은 자료를 처리한다.'))


class TestActorKeyword(unittest.TestCase):
    def test_system_actors(self):
        for s in ['본 시스템은 처리한다.', '관리자는 승인한다.', '제안사는 제출한다.']:
            self.assertTrue(kp.has_actor_keyword(s), s)

    def test_no_actor(self):
        self.assertFalse(kp.has_actor_keyword('처리한다.'))


if __name__ == '__main__':
    unittest.main()
