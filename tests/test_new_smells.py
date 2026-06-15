"""v2.7 신규 smell S11~S15 단위 테스트."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.detectors import RegexDetector


class TestS11ImplementationBias(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_oracle_db(self):
        s = "데이터베이스는 Oracle을 사용하여 구축해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S11']['detected'], 'Oracle 구축 명시 검출 실패')

    def test_java_language(self):
        s = "본 시스템은 Java를 사용하여 개발해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S11']['detected'], 'Java 사용 명시 검출 실패')

    def test_spring_framework(self):
        s = "백엔드는 Spring Boot를 적용하여 구현하여야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S11']['detected'], 'Spring Boot 명시 검출 실패')

    def test_clean(self):
        s = "본 시스템은 표준 RDBMS를 사용하여 데이터를 저장해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S11']['detected'], '벤더 명시 없는데 검출')


class TestS12NegativeStatement(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_should_not(self):
        s = "외부 IP에서의 접속은 허용하지 않아야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S12']['detected'])

    def test_not_supported(self):
        s = "본 모듈은 구버전 브라우저를 지원하지 않는다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S12']['detected'])

    def test_positive(self):
        s = "본 시스템은 IP 차단 정책을 적용해야 한다."  # 같은 의미 긍정 표현
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S12']['detected'])


class TestS13Speculation(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_if_possible(self):
        s = "가능하면 추가 기능을 제공해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S13']['detected'])

    def test_when_needed(self):
        s = "필요시 외부 시스템과 연계할 수 있어야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S13']['detected'])

    def test_later_decided(self):
        s = "세부 사항은 추후 협의에 따라 결정한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S13']['detected'])

    def test_definite(self):
        s = "본 시스템은 외부 시스템과 실시간 연계해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S13']['detected'])


class TestS14MissingPersona(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_system_only(self):
        s = "본 시스템은 자료를 정기적으로 백업하여야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S14']['detected'],
                       '시스템만 명시, 수혜자 없는데 검출 실패')

    def test_with_user(self):
        s = "본 시스템은 사용자가 입력한 자료를 백업하여야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S14']['detected'],
                        '사용자 명시되어 있는데 잘못 검출')


class TestS15PronounAmbiguity(unittest.TestCase):
    def setUp(self):
        self.det = RegexDetector()
        self.ctx = {'undefined_acronyms': set()}

    def test_haedang(self):
        s = "해당 시스템은 외부 데이터를 처리하여야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S15']['detected'])

    def test_sangki(self):
        s = "상기 항목에 해당하는 경우 보고서를 작성해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertTrue(r.flags['S15']['detected'])

    def test_specific_name(self):
        s = "재무관리 시스템은 월말에 결산 자료를 생성해야 한다."
        r = self.det.detect(s, self.ctx)
        self.assertFalse(r.flags['S15']['detected'])


if __name__ == '__main__':
    unittest.main()
