"""Metrics 단위 테스트."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.metrics import (
    precision_recall_f1, cohens_kappa,
    quality_metrics, correction_metrics,
)


class TestDetectionMetrics(unittest.TestCase):
    def test_perfect(self):
        m = precision_recall_f1([1,0,1,0], [1,0,1,0])
        self.assertEqual(m['precision'], 1.0)
        self.assertEqual(m['recall'], 1.0)
        self.assertEqual(m['f1'], 1.0)

    def test_mixed(self):
        m = precision_recall_f1([1,1,0,0], [1,0,1,0])
        # TP=1, FP=1, FN=1, TN=1
        self.assertAlmostEqual(m['precision'], 0.5)
        self.assertAlmostEqual(m['recall'], 0.5)

    def test_kappa(self):
        # 두 평가자 완전 일치
        self.assertEqual(cohens_kappa([1,0,1,0], [1,0,1,0]), 1.0)
        # 우연 수준 일치 → 0
        k = cohens_kappa([1,1,0,0], [0,0,1,1])
        self.assertLess(k, 0)


class TestQualityMetrics(unittest.TestCase):
    def test_density(self):
        # 3 요구사항, smell 4개, 2개에 smell 있음
        rows = [
            {'S1': 1, 'S3': 0, 'S4': 1},
            {'S1': 0, 'S3': 0, 'S4': 0},
            {'S1': 1, 'S3': 1, 'S4': 0},
        ]
        m = quality_metrics(rows)
        self.assertEqual(m['total_smells'], 4)
        self.assertEqual(m['reqs_with_smell'], 2)


class TestCorrectionMetrics(unittest.TestCase):
    def test_reduction(self):
        before = [{'S1': 1, 'S3': 1}, {'S1': 1, 'S3': 0}]
        after = [{'S1': 0, 'S3': 0}, {'S1': 1, 'S3': 0}]
        m = correction_metrics(before, after)
        # before: 3 smells, after: 1 smell
        self.assertAlmostEqual(m['smell_reduction_rate'], 2/3, places=2)


if __name__ == '__main__':
    unittest.main()
