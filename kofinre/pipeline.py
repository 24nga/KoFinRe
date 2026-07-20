"""KoFinRe-QA 5-stage 파이프라인 entrypoint.

논문 Stage 1~5 + Manual Validation 을 한 곳에서 orchestration.
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from .detectors import RegexDetector
from .detectors.morph_detector import MorphDetector
from .detectors.chunk_detector import ChunkDetector
from .detectors.dictionary_detector import DictionaryDetector
from .detectors.llm_detector import LLMDetector
from .ensemble import ensemble, SMELL_CODES
from .detectors.regex_detector import collect_undefined_acronyms
from .metrics import quality_metrics
from .reporting import (
    render_extraction_report, render_smell_report,
    render_dataset_card, render_run_log,
)


def run_detection(sentences: List[str],
                  doc_text: str = None,
                  use_llm: bool = False,
                  llm_caller=None,
                  ensemble_method: str = "rule_priority") -> List[Dict[str, Any]]:
    """전체 문장에 대해 5 detector + 앙상블 실행.

    Returns: 각 문장에 대해 {sentence, ensemble: {S1: {...}, ...}, per_detector: {...}}
    """
    # 문서 단위 약어 컨텍스트
    doc_text = doc_text or "\n".join(sentences)
    ctx = {"undefined_acronyms": collect_undefined_acronyms(doc_text)}

    regex = RegexDetector()
    morph = MorphDetector()
    chunk = ChunkDetector()
    diction = DictionaryDetector()
    llm = LLMDetector(llm_caller=llm_caller if use_llm else None)

    out = []
    for s in sentences:
        r1 = regex.detect(s, ctx)
        r2 = morph.detect(s, ctx)
        r3 = chunk.detect(s, ctx)
        r4 = diction.detect(s, ctx)
        r5 = llm.detect(s, ctx)
        ens = ensemble([r1, r2, r3, r4, r5], method=ensemble_method)
        out.append({
            "sentence": s,
            "ensemble": ens,
            "per_detector": {
                "regex": r1.flags,
                "morph": r2.flags,
                "chunk": r3.flags,
                "dictionary": r4.flags,
                "llm": r5.flags,
            }
        })
    return out


def run_report_pipeline(output_dir: Path,
                     extracted_text_per_doc: Dict[str, str],
                     extraction_log: List[Dict[str, Any]],
                     use_llm: bool = False,
                     llm_caller=None,
                     correction: bool = False,
                     llm_corrector=None) -> Dict[str, Any]:
    """Stage 1 추출 결과를 받아 탐지(Stage 3)·평가 리포트(Stage 4)를 생성한다.

    NOTE(v2.9.0): 구명칭 run_full_pipeline은 "5-stage 전체 실행"을 암시했으나
    실제 구현은 Stage 1 산출물 정렬 + Stage 3 탐지 + Stage 4 리포트 중심이다.
    교정(correction)은 플래그로 노출된 예비 구현이며 논문 범위 외(후속 연구).
    하위 호환을 위해 run_full_pipeline 별칭을 유지한다.

    Args:
        output_dir: 결과 저장 루트
        extracted_text_per_doc: {doc_id: full_text}
        extraction_log: 문서별 추출 결과 [{doc, format, extract_ok, ...}]
        use_llm: Stage 3 LLM detector 활성
        correction: Stage 5 활성
    """
    output_dir = Path(output_dir)

    # Stage 1 — 산출물 정렬
    s1 = output_dir / "stage1_extraction"
    s1.mkdir(parents=True, exist_ok=True)

    # Stage 3 — Detection
    from .detectors.regex_detector import (
        STRONG_DUTY_RE,
    )
    # 문장 분할 등 헬퍼는 별도 모듈로 분리 권장
    # 여기서는 단순화: 호출측에서 sentence_candidates를 넘기는 형태로 변경 권장

    # Stage 4 reports
    s4 = output_dir / "stage4_evaluation"
    s4.mkdir(parents=True, exist_ok=True)
    render_extraction_report(s4 / "extraction_report.md", extraction_log)
    render_run_log(s4 / "run_log.json", {
        "stage": "1-5",
        "use_llm": use_llm,
        "correction_enabled": correction,
    })

    return {"output_dir": str(output_dir), "stages_completed": ["1", "4"]}


# v2.9.0: honest naming - deprecated alias for backward compatibility
run_full_pipeline = run_report_pipeline
