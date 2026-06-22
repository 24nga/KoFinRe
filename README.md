# KoFinRe — Korean Public Financial RFP Quality Analyzer

> **K**orean **Fin**ancial **Re**quirements — 한국어 공공금융 RFP 요구사항 품질 자동 평가 프레임워크
>
> 논문 [`KoFinRe-QA Framework`](./docs/PAPER_DRAFT.md) 기반 / Paska smell taxonomy + IEEE 830 / ISO 29148 참조

[![version](https://img.shields.io/badge/version-2.8.0-blue)](./docs/UPDATE.MD)
[![smells](https://img.shields.io/badge/smells-19-orange)](./kofinre/smell_taxonomy.yaml)
[![standards](https://img.shields.io/badge/standards-IEEE%20830%20%2F%20ISO%2029148%20%2F%20INCOSE%20%2F%20EARS%20%2F%20CMMI%20%2F%20NCS-success)](./docs/CMMI_NCS_COMPARISON.md)
[![python](https://img.shields.io/badge/python-3.10+-blue)](pyproject.toml)
[![license](https://img.shields.io/badge/license-MIT-green)](#license)

---

## 무엇을 하나

| 단계 | 입력 | 출력 |
|---|---|---|
| **Stage 1** 추출 | RFP 공고 (HTML/HWP/PDF/DOCX/RTF) | 문장 후보 + 요구사항 후보 CSV |
| **Stage 2** 정의 | — | **19종** 한국어 smell taxonomy (Paska + IEEE 830 / ISO 29148 / INCOSE / EARS / CMMI / NCS) |
| **Stage 3** 탐지 | 요구사항 후보 | 5 detector + 앙상블 라벨 |
| **Stage 4** 평가 | 라벨 + (선택) gold label | Precision/Recall/F1/Kappa + 리포트 6종 |
| **Stage 5** 교정 | smell 검출 요구사항 | LLM 6원칙 교정 + 재평가 |

> **논문 최종본 (MECE, v2.8 19종, 다도메인)**: [`docs/PAPER_FINAL.md`](./docs/PAPER_FINAL.md) 📄
> **CMMI/NCS 비교 분석**: [`docs/CMMI_NCS_COMPARISON.md`](./docs/CMMI_NCS_COMPARISON.md) 📋
> **금융 vs 공공 다도메인 비교 (NEW)**: [`docs/DOMAIN_COMPARISON.md`](./docs/DOMAIN_COMPARISON.md) 📊
> **전체 프로젝트 여정 (v1.0 → v2.8)**: [`docs/JOURNEY.md`](./docs/JOURNEY.md) ⭐
> **D5 다도메인 샘플 실험 (NEW)**: [`experiments/rfp_2013_sample/`](./experiments/rfp_2013_sample/) 🧪
> **웹 평가기 (XLSX 업로드)**: [`web/index.html`](./web/index.html) 🌐

---

## 디렉토리 구조 (v2.8)

```
KoFinRe/
├── README.md                     ← 이 파일
├── pyproject.toml                ← 패키지 메타·의존성
├── requirements.txt              ← 최소 의존성
│
├── docs/                         ← 활성 문서 (v2.8)
│   ├── PAPER_FINAL.md            ← ⭐ MECE 학술 최종본 (19종, 다도메인)
│   ├── CMMI_NCS_COMPARISON.md    ← CMMI 9 원칙 + NCS 5 카테고리 (v2.8)
│   ├── DOMAIN_COMPARISON.md      ← 📊 금융(D1·D2·D4) vs 공공 다도메인(D5) 직접 비교
│   ├── JOURNEY.md                ← 전체 여정 v1.0 → v2.8 (13단계)
│   ├── UPDATE.MD                 ← Changelog (v1.0~v2.8)
│   ├── EXTRACTION_RULES.md       ← 추출·필터 규칙
│   ├── PASKA_KOREAN_ADAPTATION.md← Paska 원본 대비 변경
│   └── IMPROVEMENT_RECOMMENDATIONS.md ← 작성자·도구·프로세스 권고
│
├── old/                          ← 📜 시점별 historical 보관 (NEW v2.8)
│   ├── README.md                 ← 보관 안내 + 후속 매핑
│   ├── PAPER_DRAFT.md            ← v2.1 시점 초안 (10종)
│   ├── FRAMEWORK_GAP_ANALYSIS.md ← v2.0 시점 갭 분석
│   └── STANDARDS_COMPARISON.md   ← v2.7 시점 IEEE/ISO/INCOSE/EARS 갭
│
├── kofinre/                      ← 핵심 패키지
│   ├── __init__.py               ← __version__ = "2.8.0", SMELL_CODES S1~S19
│   ├── smell_taxonomy.yaml       ← 19종 smell 정식 정의 (S1~S19, v2.8)
│   ├── korean_patterns.py        ← 한국어 패턴 + CMMI/NCS 사전 (v2.8)
│   ├── detectors/
│   │   ├── base.py               ← BaseDetector / DetectorResult / Confidence
│   │   ├── regex_detector.py     ← S1~S19 전체 정규식
│   │   ├── morph_detector.py     ← 형태소·종결어미·조사 (kiwipiepy)
│   │   ├── chunk_detector.py     ← 주체-행위-대상 휴리스틱
│   │   ├── dictionary_detector.py← 금융·도메인 사전
│   │   └── llm_detector.py       ← LLM 보조 판정 + 캐싱 (19종 prompt)
│   ├── extraction/               ← Stage 1
│   │   ├── signatures.py         ← 파일 시그니처 판별
│   │   ├── document_extractor.py ← 다포맷 추출기
│   │   ├── sentence_splitter.py  ← 문장 분리
│   │   └── requirement_filter.py ← 정밀 필터 + 컷 사유 추적
│   ├── io/                       ← CSV / Excel 입출력
│   ├── llm_adapters/             ← Anthropic Claude 어댑터
│   ├── ensemble.py               ← rule-priority / majority / weighted voting
│   ├── metrics.py                ← Detection / Quality / Correction 지표
│   ├── reporting.py              ← 6 표준 리포트 (md + json)
│   ├── correction.py             ← Stage 5 LLM 교정 6원칙
│   ├── correction_heuristic.py   ← 휴리스틱 교정 (S3·S4·S8 + S16~S19 마커)
│   ├── validation.py             ← Manual Validation + Cohen's kappa
│   └── pipeline.py               ← 5-stage orchestration
│
├── web/                          ← 🌐 브라우저 평가기 (서버 불필요)
│   ├── index.html                ← 19종 smell 검출 + 마커 (v2.8 동기화)
│   └── README.md                 ← 사용법
│
├── scripts/                      ← CLI entrypoint
│   ├── run_extraction.py         ← Stage 1
│   ├── run_detection.py          ← Stage 2-3
│   ├── build_pdf_bundle.py       ← 문서 PDF 번들 (v2.8, --include-old 옵션)
│   ├── extract_rfp2013_xlsx.py   ← D5 XLSX 정형 추출 (NEW)
│   └── evaluate_rfp2013.py       ← D5 평가 + report.md 자동 생성 (NEW)
│
├── experiments/                  ← 🧪 재현 가능한 샘플 실험 (NEW v2.8)
│   └── rfp_2013_sample/          ← D5: 2013 다도메인 RFP 사례 (4,075 req / 87.5%)
│       ├── README.md             ← 실험 설명·재현 방법·핵심 발견
│       ├── stage1/               ← 추출 산출물 (sentence/requirement/xlsx CSV)
│       └── stage3/               ← 평가 산출물 (all_detection + report.md)
│
├── examples/                     ← 사용 예제
├── tests/                        ← 단위 테스트
│   ├── test_detectors.py
│   ├── test_new_smells.py        ← S11~S15 (v2.7)
│   ├── test_cmmi_smells.py       ← S16~S19 (v2.8) — 18/18 통과
│   └── test_metrics.py
│
├── data/                         ← 입력 (gitignore — 직접 추가)
├── results/                      ← 산출물 (gitignore)
├── dist/                         ← PDF 번들 출력 (gitignore)
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

## Smell Taxonomy (19종, v2.8)

### 핵심 10종 (Paska + 한국 특화) — v1.0~v2.0

| Code | 한국어 | Quality Attribute | 예시 |
|---|---|---|---|
| S1 | 복합의무 | Atomicity / Singular | 한 문장에 둘 이상 기능 |
| S2 | 불완전 | Completeness | 응답·행위·대상 누락 |
| S3 | 모호어 | Unambiguity | "적절히, 필요한, 실시간" |
| S4 | 약한의무 | Verifiability | "~한다 / ~된다" |
| S5 | 주체누락 | Completeness | 수행 주체 미명시 |
| S6 | 정량부재 | Testability | 성능 키워드 + 숫자 없음 |
| S7 | 미정의약어 | Traceability | 정의 없이 등장하는 약어 |
| S8 | 범위모호 | Unambiguity | "및/또는, 등, 포함, 관련" |
| S9 | 수동표현 | Clarity | "~되어야 한다" |
| S10 | 검증불가 | Verifiability | "효율적으로" + 측정 기준 부재 |

### 확장 5종 (ISO 29148 / INCOSE / EARS) — v2.7

| Code | 한국어 | 출처 표준 | 예시 |
|---|---|---|---|
| S11 | 구현편향 | ISO 29148 Implementation-free | "Java로 구현해야 한다" |
| S12 | 부정문 | INCOSE Positive form | "X를 지원하지 않아야 한다" |
| S13 | 추측표현 | INCOSE Speculative | "가능하다면 / 추후 결정" |
| S14 | 수혜자불명 | EARS / IEEE 830 | "사용자" 명시 없는 의무문 |
| S15 | 지시어모호 | INCOSE Pronoun | "해당, 상기, 그것" |

### CMMI / NCS 4종 — v2.8 신규

| Code | 한국어 | 출처 표준 | 예시 |
|---|---|---|---|
| **S16** | **필요성불명확** | **CMMI REQM Necessary** | "개발팀이 선호하는 폰트를 강제로" |
| **S17** | **실현불가** | **CMMI RD Feasible** | "100% 가용성", "0초 응답", "완벽한" |
| **S18** | **추적ID부재** | **CMMI REQM Traceable** | 의무문 + ID/출처 동시 부재 |
| **S19** | **제약카테고리불명** | **NCS 5 카테고리 (TECH/BIZ/COMP/OPS/SEC)** | "일부 제약" (분류 사전 0개 매칭) |

상세: [`kofinre/smell_taxonomy.yaml`](./kofinre/smell_taxonomy.yaml) · 표준 정렬: [`docs/CMMI_NCS_COMPARISON.md`](./docs/CMMI_NCS_COMPARISON.md) · [`docs/STANDARDS_COMPARISON.md`](./docs/STANDARDS_COMPARISON.md)

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
| v2.6 | ✓ | 한국어 특화 고도화 — korean_patterns 모듈 (종결5분류/격조사/번역체) |
| v2.6.1 | ✓ | ISO 29148 갭 분석 — STANDARDS_COMPARISON.md |
| v2.7 | ✓ | Smell 10 → 15종 (S11~S15: 구현편향/부정문/추측/수혜자/지시어) |
| **v2.8** | **현재** | **Smell 15 → 19종** (S16~S19: 필요성·실현·추적·제약) — CMMI/NCS 기반 |
| v2.9 | 예정 | S20 일관성 (의미 임베딩) → CMMI 9/9 완전 충족 |
| v3.0 | 예정 | S21 EARS Pattern Advisor → 전체 표준 ~80% |
| v3.1 | 예정 | 실제 사람 평가자 200건 gold + Cohen's kappa + 진짜 P/R/F1 |

---

## 문서 트리

### 활성 문서 (v2.8)
- 사용법: 이 파일
- ⭐ **논문 최종본 (MECE, 19종)**: [`docs/PAPER_FINAL.md`](./docs/PAPER_FINAL.md)
- **CMMI 9 + NCS 5 표준 정렬**: [`docs/CMMI_NCS_COMPARISON.md`](./docs/CMMI_NCS_COMPARISON.md)
- **전체 여정 (v1.0 → v2.8)**: [`docs/JOURNEY.md`](./docs/JOURNEY.md)
- 변경 이력: [`docs/UPDATE.MD`](./docs/UPDATE.MD)
- 추출 규칙 상세: [`docs/EXTRACTION_RULES.md`](./docs/EXTRACTION_RULES.md)
- Paska 대비 변경: [`docs/PASKA_KOREAN_ADAPTATION.md`](./docs/PASKA_KOREAN_ADAPTATION.md)
- 작성자·도구·프로세스 권고: [`docs/IMPROVEMENT_RECOMMENDATIONS.md`](./docs/IMPROVEMENT_RECOMMENDATIONS.md)
- 웹 평가기: [`web/index.html`](./web/index.html) · [`web/README.md`](./web/README.md)

### 시점별 historical (📜 `old/`)
- 보관 안내: [`old/README.md`](./old/README.md)
- v2.1 시점 초안 (10종): [`old/PAPER_DRAFT.md`](./old/PAPER_DRAFT.md)
- v2.0 시점 갭 분석: [`old/FRAMEWORK_GAP_ANALYSIS.md`](./old/FRAMEWORK_GAP_ANALYSIS.md)
- v2.7 시점 IEEE/ISO/INCOSE/EARS 갭: [`old/STANDARDS_COMPARISON.md`](./old/STANDARDS_COMPARISON.md)

### 레거시
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
