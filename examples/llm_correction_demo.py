"""Stage 5 LLM 교정 데모.

사용:
    # API 키 있으면 실제 호출
    $env:ANTHROPIC_API_KEY = "sk-ant-..."
    python examples/llm_correction_demo.py

    # API 키 없으면 dry-run (구조만 확인)
    python examples/llm_correction_demo.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.llm_adapters import AnthropicCaller
from kofinre.correction import LLMCorrector
from kofinre.detectors import RegexDetector
from kofinre.detectors.regex_detector import collect_undefined_acronyms
from kofinre.ensemble import SMELL_CODES
from kofinre import SMELL_NAMES_KO

SAMPLES = [
    "본 시스템은 사용자 인증, 권한관리 등을 실시간으로 지원해야 한다.",
    "이력 정보를 저장한다.",
    "시스템은 효율적으로 운영되어야 한다.",
]


def main():
    # 1. detector — smell 검출
    det = RegexDetector()
    ctx = {'undefined_acronyms': collect_undefined_acronyms('\n'.join(SAMPLES))}

    # 2. LLM caller
    caller = AnthropicCaller(model='claude-opus-4-7', dry_run=False)
    print(f"LLM caller: {'실제 호출' if not caller.dry_run else 'DRY-RUN (API 키 없음)'}\n")

    # 3. corrector
    corrector = LLMCorrector(llm_caller=caller)

    for i, s in enumerate(SAMPLES, 1):
        res = det.detect(s, ctx)
        detected = [c for c in SMELL_CODES if res.flags[c]['detected']]
        print(f"#{i} 원문: {s}")
        print(f"   검출: {', '.join(detected) if detected else '(없음)'}")

        if not detected:
            print("   교정 불필요\n")
            continue

        cr = corrector.correct(s, detected)
        print(f"   교정: {cr.corrected}")
        print(f"   제거 smell: {cr.removed_smells}")
        print(f"   의미 보존: {cr.semantic_preserved}")
        if cr.added_info:
            print(f"   ⚠️ 추가 정보: {cr.added_info}")
        if cr.error:
            print(f"   ERROR: {cr.error}")
        print()


if __name__ == '__main__':
    main()
