"""KoFinRe 기본 사용법 — Python에서 직접 호출."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.detectors import RegexDetector
from kofinre.detectors.regex_detector import collect_undefined_acronyms
from kofinre.ensemble import SMELL_CODES
from kofinre import SMELL_NAMES_KO


def main():
    requirements = [
        "본 시스템은 사용자 인증, 권한관리 등을 실시간으로 지원해야 한다.",  # S3, S8, S5
        "보고서는 자동으로 생성되어야 한다.",                                    # S9, S5
        "이력 정보를 저장한다.",                                                  # S4
        "신용점수 조회는 NICE/KCB를 통해 수행하여야 하며, 응답시간은 200ms 이하여야 한다.",  # 양호
        "시스템은 효율적으로 운영되어야 한다.",                                    # S3, S10
    ]

    doc_text = '\n'.join(requirements)
    ctx = {'undefined_acronyms': collect_undefined_acronyms(doc_text)}

    detector = RegexDetector()
    print(f'{"#":<3} {"문장":<60} {"검출":<25}')
    print('-' * 90)
    for i, s in enumerate(requirements, 1):
        result = detector.detect(s, ctx)
        detected = [f'{c}({SMELL_NAMES_KO[c]})' for c in SMELL_CODES
                   if result.flags[c]['detected']]
        smell_str = ', '.join(detected) if detected else '(없음)'
        print(f'{i:<3} {s[:58]:<60} {smell_str}')


if __name__ == '__main__':
    main()
