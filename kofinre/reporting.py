"""Reporting — 논문 Stage 4 표준 리포트 6종.

Reports:
- extraction_report.md       (문서별 추출 성공률, 실패 사유, 후보 수)
- smell_report.md            (smell 유형별 빈도/비율/예시)
- evaluation_report.md       (precision/recall/F1/kappa, 오류분석)
- correction_report.md       (LLM 교정 전후 smell 변화, 의미 보존)
- dataset_card.md            (데이터셋 구성, 출처, 라이선스, 제한)
- run_log.json               (실행 시각, 입력, 모델, 규칙 버전, 결과)
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


SMELL_NAMES_KO = {
    "S1":"복합의무","S2":"불완전","S3":"모호어","S4":"약한의무","S5":"주체누락",
    "S6":"정량부재","S7":"미정의약어","S8":"범위모호","S9":"수동표현","S10":"검증불가",
}


def render_extraction_report(out_path: Path, per_document: List[Dict[str, Any]]):
    lines = [
        "# Extraction Report",
        f"_생성: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## 문서별 추출 결과",
        "",
        "| 문서 | 포맷 | 추출 성공 | 후보 문장 | 요구사항 후보 | 실패 사유 |",
        "|---|---|---|---|---|---|",
    ]
    for d in per_document:
        lines.append(
            f"| {d.get('doc','')} | {d.get('format','')} | "
            f"{'✓' if d.get('extract_ok') else '✗'} | "
            f"{d.get('sentence_candidates', 0)} | "
            f"{d.get('requirement_candidates', 0)} | "
            f"{d.get('failure_reason','')} |"
        )
    n_total = len(per_document)
    n_ok = sum(1 for d in per_document if d.get('extract_ok'))
    total_cand = sum(d.get('sentence_candidates', 0) for d in per_document)
    total_req = sum(d.get('requirement_candidates', 0) for d in per_document)
    lines += [
        "",
        "## 요약",
        f"- 총 문서: {n_total}",
        f"- 추출 성공: {n_ok} ({100*n_ok/max(n_total,1):.1f}%)",
        f"- 문장 후보 합계: {total_cand}",
        f"- 요구사항 후보 합계: {total_req}",
    ]
    out_path.write_text("\n".join(lines), encoding='utf-8')


def render_smell_report(out_path: Path, smell_counts: Dict[str, int],
                        total_requirements: int,
                        examples_per_smell: Dict[str, List[str]] = None):
    lines = [
        "# Smell Report",
        f"_생성: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        f"분석 요구사항: {total_requirements}건",
        "",
        "## Smell 유형별 빈도",
        "",
        "| 코드 | 이름 | 검출 | 비율 |",
        "|---|---|---|---|",
    ]
    for code in ["S1","S2","S3","S4","S5","S6","S7","S8","S9","S10"]:
        n = smell_counts.get(code, 0)
        pct = 100 * n / max(total_requirements, 1)
        lines.append(f"| {code} | {SMELL_NAMES_KO[code]} | {n} | {pct:.1f}% |")

    if examples_per_smell:
        lines += ["", "## 예시 (상위 3건)"]
        for code, exs in examples_per_smell.items():
            if not exs: continue
            lines.append(f"\n### {code} {SMELL_NAMES_KO[code]}")
            for i, e in enumerate(exs[:3], 1):
                lines.append(f"{i}. {e[:200]}")

    out_path.write_text("\n".join(lines), encoding='utf-8')


def render_evaluation_report(out_path: Path,
                             per_smell_metrics: Dict[str, Dict[str, float]],
                             macro_f1: float = None,
                             micro_f1: float = None,
                             kappa: float = None,
                             error_examples: List[Dict[str, Any]] = None):
    lines = [
        "# Evaluation Report",
        f"_생성: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## Smell 유형별 성능",
        "",
        "| 코드 | Precision | Recall | F1 | FPR | FNR |",
        "|---|---|---|---|---|---|",
    ]
    for code, m in per_smell_metrics.items():
        lines.append(f"| {code} | {m.get('precision', 0):.3f} | {m.get('recall', 0):.3f} | "
                    f"{m.get('f1', 0):.3f} | {m.get('fpr', 0):.3f} | {m.get('fnr', 0):.3f} |")

    lines += ["", "## 통합 성능"]
    if macro_f1 is not None: lines.append(f"- Macro-F1: {macro_f1:.3f}")
    if micro_f1 is not None: lines.append(f"- Micro-F1: {micro_f1:.3f}")
    if kappa is not None: lines.append(f"- Cohen's Kappa: {kappa:.3f}")

    if error_examples:
        lines += ["", "## 오류 분석 (상위 10건)"]
        for i, e in enumerate(error_examples[:10], 1):
            lines.append(f"{i}. **{e.get('type','')}** ({e.get('smell','')}) — {e.get('sentence','')[:200]}")

    out_path.write_text("\n".join(lines), encoding='utf-8')


def render_correction_report(out_path: Path, correction_metrics: Dict[str, float],
                             examples: List[Dict[str, str]] = None):
    lines = [
        "# Correction Report (Stage 5)",
        f"_생성: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## 교정 효과 지표",
        "",
        "| 지표 | 값 |",
        "|---|---|",
        f"| 교정 전 smell | {correction_metrics.get('smells_before', 0)} |",
        f"| 교정 후 smell | {correction_metrics.get('smells_after', 0)} |",
        f"| Smell Reduction Rate | {correction_metrics.get('smell_reduction_rate', 0)*100:.1f}% |",
        f"| Quality Score Gain | {correction_metrics.get('quality_score_gain', 0)} |",
        f"| Atomicity Improvement | {correction_metrics.get('atomicity_improvement_rate', 0)*100:.1f}% |",
        f"| Testability Improvement | {correction_metrics.get('testability_improvement_rate', 0)*100:.1f}% |",
    ]
    if 'semantic_preservation_rate' in correction_metrics:
        lines.append(f"| Semantic Preservation Rate | {correction_metrics['semantic_preservation_rate']*100:.1f}% |")
    if 'over_correction_rate' in correction_metrics:
        lines.append(f"| Over-correction Rate | {correction_metrics['over_correction_rate']*100:.1f}% |")

    if examples:
        lines += ["", "## 교정 예시"]
        for i, e in enumerate(examples[:10], 1):
            lines += [
                f"\n### #{i}",
                f"**원문:** {e.get('before','')}",
                f"**교정:** {e.get('after','')}",
                f"**제거된 smell:** {e.get('removed_smells','')}",
            ]
    out_path.write_text("\n".join(lines), encoding='utf-8')


def render_dataset_card(out_path: Path, info: Dict[str, Any]):
    lines = [
        "# Dataset Card",
        f"_생성: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## 데이터셋 구성",
        f"- 이름: {info.get('name','KoFinRe Korean Public Financial RFP')}",
        f"- 버전: {info.get('version','2.0')}",
        f"- 출처: {info.get('source','12개 공공금융기관 공식 게시판')}",
        f"- 라이선스: {info.get('license','연구·평가 목적 한정, 원문 재배포 제한')}",
        "",
        "## 통계",
        f"- 총 사업: {info.get('total_projects', 0)}",
        f"- 본문 추출 성공: {info.get('extracted_ok', 0)}",
        f"- 추출 문장: {info.get('total_sentences', 0)}",
        f"- 요구사항 후보: {info.get('total_requirements', 0)}",
        f"- Smell 검출: {info.get('total_with_smell', 0)}",
        "",
        "## 제한사항",
        "- 본문 미확보 사업이 다수 존재 (사이트 인증·차단)",
        "- HWP 처리는 Windows + 한컴오피스 환경 필요",
        "- 한국 공공금융 도메인 특화 — 타 도메인 확장 시 재검증 필요",
        "",
        "## 인용",
        "본 데이터셋을 사용하실 경우 KoFinRe-QA Framework 논문을 인용해주세요.",
    ]
    out_path.write_text("\n".join(lines), encoding='utf-8')


def render_run_log(out_path: Path, log: Dict[str, Any]):
    log["timestamp"] = datetime.now().isoformat(timespec='seconds')
    out_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')
