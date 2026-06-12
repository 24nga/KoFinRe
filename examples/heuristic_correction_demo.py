"""휴리스틱 교정 데모 (LLM 없이 작동)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.detectors import RegexDetector
from kofinre.detectors.regex_detector import collect_undefined_acronyms
from kofinre.ensemble import SMELL_CODES
from kofinre.correction_heuristic import heuristic_correct
from kofinre import SMELL_NAMES_KO

SAMPLES = [
    "본 시스템은 사용자 인증, 권한관리 등을 실시간으로 지원해야 한다.",
    "이력 정보를 저장한다.",
    "시스템은 효율적으로 운영되어야 한다.",
    "신용점수 조회는 NICE/KCB를 통해 수행하여야 하며, 응답시간은 200ms 이하여야 한다.",
    "보고서는 매월 신속히 생성되고, 관리자에게 통보된다.",
]


def main():
    det = RegexDetector()
    ctx = {'undefined_acronyms': collect_undefined_acronyms('\n'.join(SAMPLES))}

    for i, s in enumerate(SAMPLES, 1):
        res = det.detect(s, ctx)
        detected = [c for c in SMELL_CODES if res.flags[c]['detected']]
        print(f"#{i} 원문:")
        print(f"   {s}")
        print(f"   검출: {', '.join(f'{c}({SMELL_NAMES_KO[c]})' for c in detected) if detected else '(없음)'}")

        if not detected:
            print("   → 교정 불필요\n")
            continue

        cr = heuristic_correct(s, detected)
        print(f"   교정 결과:")
        for j, c in enumerate(cr.corrected, 1):
            print(f"     {j}) {c}")
        if cr.applied_rules:
            print(f"   적용 규칙: {', '.join(cr.applied_rules)}")
        print()


if __name__ == '__main__':
    main()
