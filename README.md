# KoFinRe — Korean Public Financial RFP Quality Analyzer

> **K**orean **Fin**ancial **Re**quirements — 한국어 공공금융 RFP 요구사항 품질 자동 평가 프레임워크
>
> 논문 [`KoFinRe-QA Framework`](./docs/PAPER_DRAFT.md) 기반 / Paska smell taxonomy + IEEE 830 / ISO 29148 참조

[![version](https://img.shields.io/badge/version-2.1.0-blue)](./docs/UPDATE.MD)
[![python](https://img.shields.io/badge/python-3.10+-blue)](pyproject.toml)
[![license](https://img.shields.io/badge/license-MIT-green)](#license)

---

## 무엇을 하나

| 단계 | 입력 | 출력 |
|---|---|---|
| **Stage 1** 추출 | RFP 공고 (HTML/HWP/PDF/DOCX/RTF) | 문장 후보 + 요구사항 후보 CSV |
| **Stage 2** 정의 | — | 10종 한국어 smell taxonomy |
| **Stage 3** 탐지 | 요구사항 후보 | 5 detector + 앙상블 라벨 |
| **Stage 4** 평가 | 라벨 + (선택) gold label | Precision/Recall/F1/Kappa + 리포트 6종 |
| **Stage 5** 교정 | smell 검출 요구사항 | LLM 6원칙 교정 + 재평가 |

> **논문 최종본 (MECE)**: [`docs/PAPER_FINAL.md`](./docs/PAPER_FINAL.md) 📄
> **요구공학 표준 ↔ KoFinRe 갭 분석**: [`docs/STANDARDS_COMPARISON.md`](./docs/STANDARDS_COMPARISON.md) 📊
> **전체 프로젝트 여정 (v1.0 → v2.5)**: [`docs/JOURNEY.md`](./docs/JOURNEY.md) ⭐
> **웹 평가기 (XLSX 업로드)**: [`web/index.html`](./web/index.html) 🌐

---

## 디렉토리 구조 (v2.1)

```
KoFinRe/
├── README.md                     ← 이 파일
├── pyproject.toml                ← 패키지 메타·의존성
├── requirements.txt              ← 최소 의존성
│
├── docs/                         ← 모든 문서 한 곳에
│   ├── UPDATE.MD                 ← 변경 이력 (Keep a Changelog)
│   ├── EXTRACTION_RULES.md       ← 추출·필터 규칙
│   ├── FRAMEWORK_GAP_ANALYSIS.md ← 논문 vs 구현 갭
│   ├── PASKA_KOREAN_ADAPTATION.md← Paska 원본 대비 변경
│   └── PAPER_DRAFT.md            ← 학술용 정리본
│
├── kofinre/                      ← 핵심 패키지
│   ├── __init__.py
│   ├── smell_taxonomy.yaml       ← 10종 smell 정식 정의
│   ├── detectors/
│   │   ├── base.py               ← BaseDetector / DetectorResult / Confidence
│   │   ├── regex_detector.py     ← S1~S10 전체 정규식
│   │   ├── morph_detector.py     ← 형태소·종결어미·조사
│   │   ├── chunk_detector.py     ← 주체-행위-대상 휴리스틱
│   │   ├── dictionary_detector.py← 금융·도메인 사전
│   │   └── llm_detector.py       ← LLM 보조 판정 + 캐싱
│   ├── extraction/               ← Stage 1
│   │   ├── signatures.py         ← 파일 시그니처 판별
│   │   ├── document_extractor.py ← 다포맷 추출기
│   │   ├── sentence_splitter.py  ← 문장 분리
│   │   └── requirement_filter.py ← 정밀 필터 + 컷 사유 추적
│   ├── io/                       ← CSV / Excel 입출력
│   │   ├── csv_loader.py
│   │   └── excel_writer.py
│   ├── ensemble.py               ← rule-priority / majority / weighted voting
│   ├── metrics.py                ← Detection / Quality / Correction 지표
│   ├── reporting.py              ← 6 표준 리포트 (md + json)
│   ├── correction.py             ← Stage 5 LLM 교정 6원칙
│   ├── validation.py             ← Manual Validation + Cohen's kappa
│   └── pipeline.py               ← 5-stage orchestration
│
├── scripts/                      ← CLI entrypoint
│   ├── run_extraction.py         ← Stage 1
│   └── run_detection.py          ← Stage 2-3
│
├── examples/                     ← 사용 예제
│   ├── basic_usage.py            ← 5문장 데모
│   └── req_abstract_demo.py      ← REQ_abstract.csv 평가
│
├── tests/                        ← 단위 테스트
│   ├── test_detectors.py
│   └── test_metrics.py
│
├── data/                         ← 입력 (gitignore — 직접 추가)
├── results/                      ← 산출물 (gitignore)
│
└── legacy/                       ← v1 스크립트 보관 (마이그레이션 참고용)
```

---

## 빠른 시작

### 설치

```powershell
# 필수
pip install -r requirements.txt

# HWP 처리 (Windows + 한컴오피스 필요)
pip install pywin32

# DOCX 처리
pip install python-docx
```

### 가장 빠른 데모 — 5문장 평가

```powershell
python examples/basic_usage.py
```

출력 예:
```
1   본 시스템은 사용자 인증, 권한관리 등을 실시간으로 지원해야 한다.   S3(모호어), S5(주체누락), S8(범위모호)
2   보고서는 자동으로 생성되어야 한다.                                S5(주체누락), S9(수동표현)
3   이력 정보를 저장한다.                                              S4(약한의무)
4   신용점수 조회는 NICE/KCB를 통해 수행하여야 하며, 응답시간은 200ms…  (없음)
5   시스템은 효율적으로 운영되어야 한다.                              S3(모호어), S10(검증불가)
```

### 정형 CSV (REQ_abstract.csv 형식) 평가

```powershell
python examples/req_abstract_demo.py \
    --input "C:/Users/heen1/Downloads/REQ_abstract.csv" \
    --output results/req_abstract_demo/
```

### 비정형 RFP 공고 → 평가

```powershell
# Stage 1
python scripts/run_extraction.py \
    --input data/raw_documents/ \
    --output results/stage1_extraction/

# Stage 2-3
python scripts/run_detection.py \
    --input results/stage1_extraction/requirement_candidates.csv \
    --output results/stage3_detection/
```

### 단위 테스트

```powershell
python -m unittest discover tests
```

---

## Smell Taxonomy (10종)

| Code | 한국어 | Quality Attribute | 예시 |
|---|---|---|---|
| S1 | 복합의무 | Atomicity | 한 문장에 둘 이상 기능 |
| S2 | 불완전 | Completeness | 응답·행위·대상 누락 |
| S3 | 모호어 | Unambiguity | "적절히, 필요한, 실시간" |
| S4 | 약한의무 | Verifiability | "~한다 / ~된다" |
| S5 | 주체누락 | Completeness | 수행 주체 미명시 |
| S6 | 정량부재 | Testability | 성능 키워드 + 숫자 없음 |
| S7 | 미정의약어 | Traceability | 정의 없이 등장하는 약어 |
| S8 | 범위모호 | Unambiguity | "및/또는, 등, 포함, 관련" |
| S9 | 수동표현 | Clarity | "~되어야 한다" |
| S10 | 검증불가 | Verifiability | "효율적으로" + 측정 기준 부재 |

상세: [`kofinre/smell_taxonomy.yaml`](./kofinre/smell_taxonomy.yaml)

---

## 검증 결과 (v1 데이터셋)

| 데이터셋 | 입력 | 추출 | Smell 비율 |
|---|---|---|---|
| RFP 56건 (자체 추출) | 3,210 문장 | 75건 | 65.3% |
| REQ_abstract 30건 (정형) | 30 req / 140 sub | 30건 | 56.7% |
| PURE 영문 79건 (Paska 기준선) | 1,200 reqs | — | 46.6% |
| **실기업 4모듈 257건 (D4, 익명)** | 257 reqs | — | **93.4%** |

v2.x 에서 4 방식 baseline (Rule/NLP/LLM/Ensemble) 비교 자동화 예정.

### D4 모듈별 (익명화)

| 모듈 | 건수 | Smell | 비율 | 두드러진 패턴 |
|---|---:|---:|---:|---|
| FA 회계 | 95 | 92 | 96.8% | 약한의무(S4) 44건 |
| BG 예산 | 52 | 50 | 96.2% | 불완전(S2) 50건 |
| CI 신용정보 | 57 | 53 | 93.0% | 미정의약어(S7) 19건 |
| CM 공통 | 53 | 45 | 84.9% | 가장 깨끗 (모범) |

---

## 로드맵

| 버전 | 상태 | 주요 변경 |
|---|---|---|
| v1.0 | ✓ | 7-smell, 단일 detector |
| v2.0 | ✓ | 10-smell, 5-detector 골격, 6 리포트, 논문 정렬 |
| v2.1 | ✓ | 폴더 구조 정리, 패키지화, CLI, 단위 테스트 |
| v2.1.1 | ✓ | D4 실기업 검증, 익명화 모듈, 개선 권고문 |
| v2.2 | ✓ | ChunkDetector 정밀화 (short bullet/목적조사/양식 파이프) — D4 -16ppt |
| v2.3 | ✓ | kiwipiepy 형태소 분석 본격 통합 — 자동 FP 26→3.9% (-22ppt) |
| v2.4 | ✓ | Anthropic LLM 어댑터, 문서 PDF 번들, R1 시뮬 평가 |
| v2.5 | ✓ | 휴리스틱 교정 + 4방식 baseline 비교 — Rule-only Macro 0.28 |
| v2.5.1 | ✓ | 웹 HTML 평가기, MECE 논문 PAPER_FINAL.md |
| **v2.6** | **현재** | **한국어 특화 고도화** — korean_patterns 모듈 (종결5분류/격조사/번역체/이중부정) |
| v2.7 | 예정 | confidence_weighted ensemble + 실제 평가자 데이터셋 |
| v2.3 | 예정 | 200건 gold label, baseline 비교 자동화 |

---

## 문서 트리

- 사용법: 이 파일
- 추출 규칙 상세: [`docs/EXTRACTION_RULES.md`](./docs/EXTRACTION_RULES.md)
- 변경 이력: [`docs/UPDATE.MD`](./docs/UPDATE.MD)
- 논문 vs 구현 갭: [`docs/FRAMEWORK_GAP_ANALYSIS.md`](./docs/FRAMEWORK_GAP_ANALYSIS.md)
- Paska 대비 변경: [`docs/PASKA_KOREAN_ADAPTATION.md`](./docs/PASKA_KOREAN_ADAPTATION.md)
- 논문용 정리: [`docs/PAPER_DRAFT.md`](./docs/PAPER_DRAFT.md)
- v1 스크립트 보관: [`legacy/`](./legacy/)

## License

MIT (한컴오피스 COM 자동화는 한컴 라이선스 약관 준수 필요)

## 인용

본 프레임워크 사용 시 KoFinRe-QA Framework 논문 인용:

```bibtex
@article{kofinre2026,
  title={A Framework for Quality Analysis and Dataset Construction of Korean Public Financial RFP Requirements},
  author={...},
  year={2026},
}
```
