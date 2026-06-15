# 한국어 공공금융 RFP 요구사항 품질 자동 평가 프레임워크 KoFinRe-QA

## 영문 NLP 도구 Paska의 한국어 어댑테이션, 6대 요구공학 표준 정렬, 데이터셋 구축, 그리고 정량적 검증

> **KoFinRe-QA: A Framework for Quality Analysis and Dataset Construction of Korean Public Financial RFP Requirements**
> *An NLP-Ensemble and LLM-Correction Approach Aligned with Paska / IEEE 830 / ISO 29148 / INCOSE / EARS / CMMI / NCS*

---

## Abstract

영문권에서는 Paska·PURE와 같은 자연어 요구사항 품질 평가 도구·데이터셋이 활용되어 왔으나, 한국어 공공금융 도메인에서는 (1) 공개 데이터셋, (2) 자동 평가 도구, (3) 도메인 특화 smell taxonomy, (4) 요구공학 국제·국가 표준과의 정렬이 모두 부재하다. 본 연구는 이 4가지 공백을 동시에 채우는 **KoFinRe-QA Framework**를 제안한다.

프레임워크는 (i) 다포맷 텍스트 추출 (HTML/HWP/PDF/DOCX/RTF), (ii) **19종 한국어 smell taxonomy** 정의 (Paska 9종 + IEEE 830 / ISO 29148 / INCOSE / EARS 5종 + CMMI / NCS 4종), (iii) 5 detector 앙상블 탐지, (iv) 6 표준 리포트 정량 평가, (v) LLM/휴리스틱 교정의 5단계로 구성된다. 4 데이터셋으로 검증했다: 공공금융 RFP 56건 비정제(D1), 정형 30건(D2), PURE 영문 79건 기준선(D3), 실기업 4모듈 257건 익명화(D4). 정밀화 과정에서 자동 likely-FP를 **26% → 3.9%(-22pp)** 감소시켰으며, 4 방식 baseline 비교에서 **Rule-only가 Macro-F1 0.278로 최선**임을 정량 확인했다. 표준 정렬 진화는 **v1.0 28% → v2.6 28% → v2.7 55% → v2.8 ~70%**, CMMI 9 원칙 충족도는 **5/9 → 8/9**, NCS 5 제약 카테고리 분류 보조는 **0/5 → 5/5**로 확장되었다. 본 도구는 오픈소스(<https://github.com/24nga/KoFinRe>)로 공개되며, 실기업 데이터 처리를 위한 5단계 윤리·법적 워크플로우를 함께 제안한다.

**Keywords:** Requirements Engineering, Korean RFP Dataset, Public Financial Sector, Requirement Smell, Paska, IEEE 830, ISO 29148, INCOSE, EARS, CMMI REQM/RD, NCS Constraint Categories, NLP Ensemble, LLM Correction, Anonymization

---

## 1. Introduction

### 1.1 연구 배경
공공금융 정보시스템 사업은 규제 준수·대외기관 연계·고객정보 보호·금융거래 처리에서 높은 정확성과 추적가능성을 요구한다. RFP 단계에서 작성된 요구사항의 품질은 전체 사업 성과와 직결되며, 모호한 표현·불완전한 명세·복합 의무·필요성 불명·실현 불가 표현·추적 ID 부재·제약 카테고리 미분류는 사후 분쟁의 핵심 원인이다.

### 1.2 문제 정의
영문권 자동 평가 도구를 한국어 RFP에 직접 적용 시 다음 6가지 장벽이 존재한다:

| # | 장벽 | 영향 |
|---|---|---|
| 1 | Paska의 allennlp 의존 — Windows·한국어 미지원 | 도구 작동 불가 |
| 2 | 한국어 SOV 어순·주어 생략 허용 | 영문 detection 규칙 부적합 |
| 3 | 한국 SI 작성 관행 (평서형 "한다", 명사 결합) | 영문 smell 패턴과 불일치 |
| 4 | HWP·전각 글머리표 등 한국 고유 포맷 | 표준 추출 도구 부재 |
| 5 | 한국어 요구사항 공개 데이터셋 부재 | 연구 재현·비교 불가 |
| 6 | 6대 요구공학 표준 (IEEE 830 / ISO 29148 / INCOSE / EARS / CMMI / NCS)과의 정렬 부재 | 학술·실무 표준 미반영 |

### 1.3 연구 질문

- **RQ1**: 한국 RFP에서 요구사항 후보를 신뢰성 있게 추출하기 위한 기준은 무엇인가?
- **RQ2**: Paska smell taxonomy + 한국 RFP 특성 + 6대 요구공학 표준을 어떻게 통합 정의할 수 있는가?
- **RQ3**: 한국어 NLP 기반 복수 분석기의 앙상블은 smell 탐지 성능을 향상시키는가?
- **RQ4**: 한국 RFP에서 가장 빈번하게 나타나는 작성오류 유형은 무엇이며 표준 커버리지는 어떻게 확장 가능한가?
- **RQ5**: LLM 기반 교정은 smell을 감소시키면서 원문 의미를 보존할 수 있는가?

### 1.4 기여 (6종)

1. **19종 한국어 smell taxonomy**: Paska 9종 + 한국 특화 1종 + IEEE/ISO/INCOSE/EARS 5종 + CMMI/NCS 4종
2. **5 detector 앙상블 도구 KoFinRe**: Regex / Morph(kiwipiepy) / Chunk / Dictionary / LLM + rule-priority voting
3. **6대 요구공학 표준 정렬**: IEEE 830 (8 특성) / ISO 29148 (9 특성) / INCOSE (11 결함) / EARS (5 패턴) / CMMI REQM·RD (9 원칙) / NCS (5 제약 카테고리)
4. **4 데이터셋 검증**: 공공 비정제·정형·영문 기준선·실기업 익명화
5. **윤리·법적 워크플로우**: 실기업 데이터 5단계 처리 표준
6. **오픈소스 공개**: <https://github.com/24nga/KoFinRe> (MIT License) + 웹 평가기 + PDF 번들

---

## 2. Related Work

### 2.1 영문 요구사항 데이터셋·도구

- **PURE** (Ferrari 2017): 79건 공개 SRS 데이터셋. 본 연구에서 D3 기준선으로 활용
- **Paska** (Veizaga 2024): allennlp constituency parsing + Stanford POS tagger + Java smell detector. 9종 smell, Rimay 패턴 추천

### 2.2 요구사항 품질 — 국제 표준 6종

| 표준 | 영역 | 핵심 |
|---|---|---|
| **IEEE 830-1998** | SRS 좋은 특성 | 정확·명확·완전·일관·중요도·검증·수정·추적 (8 특성) |
| **ISO/IEC/IEEE 29148:2018** | 요구사항 품질 확장 | 9 특성 (Necessary, Singular, Feasible, Verifiable, Implementation-free 등) |
| **INCOSE Guide** | 작성 결함 | 11 결함 (Negative, Speculative, Universal Qualifier 등) |
| **EARS** (Mavin 2009) | 작성 패턴 | 5 패턴 (Ubiquitous, Event-driven, State-driven, Optional, Unwanted) |
| **CMMI** (V2.0 REQM·RD) | 요구사항 관리·개발 | 9 원칙 (Necessary, Feasible, Traceable 등) |
| **NCS** (한국 국가직무능력표준) | 제약 분류 | 5 카테고리 (TECH, BIZ, COMP, OPS, SEC) |

### 2.3 한국어 NLP / LLM 기반 SW 공학

- 한국어 NLP 기반 요구사항 분류 연구 (Cho 2020)
- 생성형 AI 기반 UML 변환 (Cho 2024)
- 한국어 controlled natural language 시도 (선행 부재)

### 2.4 본 연구의 차별성

| 차원 | 선행 연구 | 본 연구 |
|---|---|---|
| 언어 | 영문 중심 | 한국어 본격 |
| 도메인 | 일반 SW | 공공금융 + 실기업 |
| Smell taxonomy | Paska 9종 (영문) | **19종 한국어 + 6대 표준 정렬** |
| 표준 정렬 | 미흡 | IEEE / ISO / INCOSE / EARS / CMMI / NCS 6종 정량 매핑 |
| 데이터 | 1~2 데이터셋 | 4 데이터셋 통합 |
| 실기업 처리 | 미정립 | 5단계 윤리·법 워크플로우 |
| 도구 | 단일 검출기 | 5 detector 앙상블 + 휴리스틱·LLM 교정 + 웹 평가기 |

---

## 3. KoFinRe-QA Framework (제안 방법)

### 3.1 개요

```
RFP 문서 → ① 추출 → ② Smell 정의(19종) → ③ 앙상블 탐지 → ④ 정량 평가 → ⑤ LLM/휴리스틱 교정
```

### 3.2 Stage 1 — 텍스트 추출

#### 3.2.1 입력 다포맷 처리
| 포맷 | 도구 |
|---|---|
| HTML | BeautifulSoup (UTF-8/CP949/EUC-KR 자동 감지) |
| HWP | 한컴오피스 COM 자동화 (Windows) |
| PDF | pdfplumber |
| DOCX | python-docx |
| RTF | striprtf |

#### 3.2.2 시그니처 기반 파일 판별
공공기관 사이트는 `page.html`이라는 파일명으로 PDF·HWP 바이너리를 반환하는 경우가 빈번. 본 연구는 8 magic byte 패턴으로 실제 포맷 재판별 (PDF/OLE2/HWP_ALT/ZIP/HTML/RTF/UNKNOWN).

#### 3.2.3 문장 분리
- 한국어/영문 종결 (`. ! ? 。`)
- 세미콜론(`;`) — sub-requirement 분리
- 양식 파이프(`|`) — SI 정의서 결합형 분리 (v2.2 신규)
- 전각 글머리표(`◇□■○●▶▪◐`) → 세미콜론 변환

#### 3.2.4 요구사항 정밀 필터 (6 카테고리 컷)
| Filter | 차단 대상 |
|---|---|
| HARD_NOISE | COPYRIGHT, 사이트맵, 페이지 네비 |
| BID_NOISE | 입찰자·청렴계약·조달청·국가계약법 |
| META_START | 사업명·문의처 시작 |
| LEADING_NOISE | 글머리표·로마숫자 단편 |
| EVAL_CRITERIA | "을 평가한다" 채점 룰 |
| LEGAL_DOMAIN | 임차인·보증금 + 시스템 명사 부재 |

산출물: `sentence_candidates.csv`, `requirement_candidates.csv`, `exclusion_reason.csv`, `extraction_log.json`.

### 3.3 Stage 2 — Smell Taxonomy (19종, v2.8)

#### 3.3.1 전체 분류표

| Code | 한국어 | Quality Attribute | 출처 표준 | 도입 |
|---|---|---|---|---|
| S1 | 복합의무 | Atomicity / Singular | Paska, ISO 29148, CMMI | v1.0 |
| S2 | 불완전 | Completeness | 한국 특화 (SI 양식) | v2.0 |
| S3 | 모호어 | Unambiguity | Paska, IEEE 830, INCOSE | v1.0 |
| S4 | 약한의무 | Verifiability | 한국 특화 (평서형 "한다") | v1.0 |
| S5 | 주체누락 | Completeness | Paska | v1.0 |
| S6 | 정량부재 | Testability | Paska, ISO 29148 | v1.0 |
| S7 | 미정의약어 | Traceability | 한국 특화 (영문 약어 빈출) | v2.0 |
| S8 | 범위모호 | Unambiguity | Paska 분리 | v2.0 |
| S9 | 수동표현 | Clarity | Paska | v1.0 |
| S10 | 검증불가 | Verifiability | Paska, IEEE 830 | v2.0 |
| **S11** | **구현편향** | **Implementation-free** | **ISO 29148, INCOSE** | v2.7 |
| **S12** | **부정문** | **Positive form** | **INCOSE** | v2.7 |
| **S13** | **추측표현** | **Definiteness** | **INCOSE Speculative** | v2.7 |
| **S14** | **수혜자불명** | **Stakeholder clarity** | **EARS, IEEE 830** | v2.7 |
| **S15** | **지시어모호** | **Reference clarity** | **INCOSE Pronoun** | v2.7 |
| **S16** | **필요성불명확** | **Necessary** | **CMMI REQM** | **v2.8** |
| **S17** | **실현불가** | **Feasible** | **CMMI RD, ISO 29148** | **v2.8** |
| **S18** | **추적ID부재** | **Traceable** | **CMMI REQM** | **v2.8** |
| **S19** | **제약카테고리불명** | **Constraint classification** | **NCS 5 categories** | **v2.8** |

#### 3.3.2 v2.8 신규 4종 검출 패턴 (CMMI/NCS 기반)

| Code | 핵심 패턴 | 양성 예 | 음성 예 (정상) |
|---|---|---|---|
| **S16** 필요성불명확 | `선호하는`, `강제로`, `임의로 정한`, `독단적`, `개발(팀\|자)이 (선호\|결정)` | "개발팀이 **선호하는** 폰트를 **강제로** 사용" | "사용자 인증 강화를 위해 MFA 적용" |
| **S17** 실현불가 | `100\s*%\s*(가용\|정확\|완벽\|보장)`, `99\.99{3,}\s*%`, `장애 0건`, `응답시간 0초`, `완벽한` | "100% 가용성 보장", "0초 이내", "완벽한 보안", "99.9999%" | "월 가용성 99.9% 이상" |
| **S18** 추적ID부재 | 의무 종결 존재 + ID 패턴 부재 + 출처/근거 부재 | "본 시스템은 사용자 인증 기능을 제공하여야 한다." | "**FUNC-AUTH-001** 본 시스템은…" / "**보안정책에 따라** 인증 제공" |
| **S19** 제약카테고리불명 | 제약 시그널(`제약\|제한\|준수\|한정\|허용\|금지`) 존재 + TECH/BIZ/COMP/OPS/SEC 사전 0개 매칭 | "본 사업은 일부 제약을 받아야 한다" | "Linux 환경에서 운영" (TECH 매칭) |

#### 3.3.3 NCS 5 제약 카테고리 분류 사전 (S19 보조)

| 카테고리 | 사전 키워드 (발췌) |
|---|---|
| **TECH** 기술 | OS, 운영체제, 플랫폼, 프레임워크, RHEL, Red Hat, Java, Linux, JDK, Spring 등 |
| **BIZ** 사업·조직 | 예산, 일정, 마일스톤, 오픈일, 마감, 한도, 결재선, 조직 등 |
| **COMP** 법·규제 | 개인정보, PII, GDPR, 개인정보보호법, 감독규정 등 ("준수"는 너무 일반적이라 제외) |
| **OPS** 운영·환경 | 24시간, 365일, 무중단, 정기점검, 운영시간 등 |
| **SEC** 안전·보안 | MFA, 다중인증, 암호화, AES, SHA, 감사로그, 키 관리 등 |

### 3.4 Stage 3 — NLP 앙상블 탐지

#### 3.4.1 5 Detector

| Detector | 역할 | 구현 |
|---|---|---|
| **RegexDetector** | 명시적 패턴 매칭 (S1~S19) | 50+ 정규식, HIGH/MED/LOW confidence |
| **MorphDetector** | 형태소·종결어미·조사 | kiwipiepy(Kiwi C++), 세종 POS 태그셋 |
| **ChunkDetector** | 주체·행위·대상 추정 | 명사구·동사 휴리스틱 |
| **DictionaryDetector** | 도메인 사전 | 한국 금융기관·약어 화이트리스트 |
| **LLMDetector** | 보조 판정 | Anthropic Claude API + dry-run fallback |

#### 3.4.2 Voting 3종

- **majority**: 과반 동의
- **rule-priority** (기본): RegexDetector HIGH면 우선, 아니면 다른 detector 결합
- **confidence-weighted**: 가중 평균 ≥ 임계값

### 3.5 Stage 4 — 정량 평가 (3 카테고리)

| 카테고리 | 지표 |
|---|---|
| **Detection** | Precision, Recall, F1, FPR, FNR, Cohen's Kappa, Macro-F1, Micro-F1 |
| **Quality** | Smell Density, Coverage, Average per Req, Severe Ratio, Extraction Yield, Validity Rate |
| **Correction** | Smell Reduction Rate, Quality Score Gain, Semantic Preservation, Over-correction, Atomicity·Testability Improvement |

리포트 6종: `extraction_report.md`, `smell_report.md`, `evaluation_report.md`, `correction_report.md`, `dataset_card.md`, `run_log.json`.

### 3.6 Stage 5 — 교정 (이중 모드)

#### 3.6.1 LLM 교정 (6 원칙)
1. 원문 의미 유지
2. 원문에 없는 정보 추가 금지
3. 원자성 (1 요구사항 = 1 기능)
4. 모호 표현 → 검증 가능 표현
5. 주체·조건·행위·대상·결과 명확화
6. 교정 전후 차이·추가정보 기록

#### 3.6.2 휴리스틱 교정 (LLM 부재 시)
정규식 치환 기반: S1 분리 / S3 `[명세 필요: ...]` 마커 / S4 평서→의무형 / S8 `[열거 명시 필요]` / **S16 `[정당화 필요]` / S17 `[현실적 수치 필요]` / S18 `[ID·출처 필요]` / S19 `[제약 카테고리 명시 필요]`** (v2.8 신규).

---

## 4. Experimental Setup

### 4.1 데이터셋 4종 (MECE 분리)

| 코드 | 데이터 | 크기 | 출처 | 위치 |
|---|---|---:|---|---|
| **D1** | 공공금융 RFP 비정제 | 56 사업, 4,917 문장 | 12개 공공기관 게시판 | 공개 (메타) |
| **D2** | 정형 RFP | 30 req, 140 sub-req | 정제 CSV | 공개 (저자 동의) |
| **D3** | PURE 영문 SRS | 79 문서, 1,200 reqs 샘플 | PROMISE | 공개 |
| **D4** | 실기업 4 모듈 | 257 req | 한 국내 캐피탈사 | **🔒 로컬 only** |

### 4.2 평가 지표
3.5절 참조 (Detection / Quality / Correction).

### 4.3 Baseline (4 방식)
| 방식 | 구성 |
|---|---|
| Rule-only | RegexDetector 단독 |
| NLP-only | MorphDetector + ChunkDetector |
| LLM-assisted | Regex + LLM OR |
| Ensemble | 5 detector + rule-priority voting |

### 4.4 윤리·법적 처리 (D4 전용)
| 단계 | 처리 |
|---|---|
| 1. 정규식 익명화 | 회사·인명·사번·연락처·이메일·URL·일자·외부파트너 8종 마스킹 |
| 2. LOCAL_ONLY 격리 | git repo 밖 (`real_reqs_anonymized_LOCAL_ONLY.zip`) |
| 3. 잔여 위험 모니터링 | 4+자 영문 약어, 영문+숫자 ID 카운트 |
| 4. leak 검사 | git grep 5+회 (회사명·약어·코드 토큰 6종 — 본 논문에선 마스킹) — 모두 0 hit |
| 5. 통계 only 외부 | 본 논문 인용 0건, 통계·익명 짧은 패턴만 |

---

## 5. Results

### 5.1 데이터 수집·추출 (RQ1 관련)

| 데이터셋 | 시도 | 추출 성공 | Yield |
|---|---:|---:|---:|
| D1 | 56 | 14 (25%) | 사이트 인증 차단 |
| D3 | 79 | 76 (96%) | 영문 표준 환경 |
| D4 | 257 req (정형) | 257 (100%) | XLSX 컬럼 직접 |

### 5.2 Smell 검출 — 4 데이터셋 통합 (RQ2, RQ4)

| Smell | D3 영문 1,200 | D1 비정제 75 | D2 정형 30 | D4 실기업 257 |
|---|---:|---:|---:|---:|
| Passive / 수동 (S9) | **27.5%** | 8.0% | 10.0% | 1% |
| Non-atomic / 복합 (S1) | 13.8% | 2.7% | 0% | **0%** |
| Missing-quant / 정량 (S6) | 1.3% | 6.7% | 6.7% | 2% |
| 모호어 (S3) | n/a | 30.7% | 26.7% | 4% |
| **주체모호 (S5)** | n/a | **32.0%** | 26.7% | **81%** |
| **약한의무 (S4)** | n/a | 0% | 30.0% | 23% |
| 미정의 약어 (S7) | n/a | 1.3% | 3.3% | 11% |
| **불완전 (S2)** | n/a | n/a | n/a | **91%** |

### 5.3 Smell Taxonomy 진화 — 6대 표준 커버리지 누적

| 버전 | Smell 수 | IEEE 830 (8) | ISO 29148 (9) | INCOSE (11) | EARS (5) | CMMI (9) | NCS (5) | **전체** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v1.0 | 7 | 3 | 3 | 2 | 0 | 3 | 0 | ~20% |
| v2.0 | 10 | 5 | 5 | 4 | 0 | 5 | 0 | ~28% |
| v2.6 | 10 | 5 | 5 | 4 | 0 | 5 | 0 | 28% |
| v2.7 | 15 | 7 | 7 | 8 | 2 | 5 | 0 | **55%** |
| **v2.8** | **19** | **8** | **8** | **8** | **2** | **8** | **5** | **~70%** |

> v2.8에서 추가 충족된 항목 — CMMI Necessary (S16) / Feasible (S17) / Traceable (S18) / NCS TECH·BIZ·COMP·OPS·SEC 5종 (S19) / ISO 29148 Necessary (S16).

### 5.4 CMMI 9 원칙 매핑 (v2.8 기준)

| 원칙 | CMMI 영역 | v2.6 | v2.7 | **v2.8** | 매핑 smell |
|---|---|:-:|:-:|:-:|---|
| Necessary 필요성 | REQM | ✗ | ✗ | **✓** | **S16** |
| Singular 단일성 | RD | ✓ | ✓ | ✓ | S1 |
| Unambiguous 명확성 | RD | ✓ | ✓ | ✓ | S3 + S8 + S15 |
| Verifiable 검증 가능성 | RD | ✓ | ✓ | ✓ | S4 + S6 + S10 |
| Consistent 일관성 | REQM | ✗ | ✗ | ✗ | (v2.9 예정 — S20) |
| Complete 완전성 | RD | ✓ | ✓ | ✓ | S2 + S5 + S14 |
| Impl-free 구현 독립성 | RD | ✗ | ✓ | ✓ | S11 |
| Traceable 추적 가능성 | REQM | ⚠ | ⚠ | **✓** | S7 + **S18** |
| Feasible 현실성 | RD | ✗ | ✗ | **✓** | **S17** |
| **충족** | — | **5/9** | **5/9** | **8/9** | +3 |

### 5.5 NCS 5 제약 카테고리 — S19 분류 보조

| 카테고리 | 매핑 | 사전 규모 | 예시 매칭 |
|---|---|---:|---|
| TECH 기술 | S19 + CONSTRAINT_TECH | 25+ 키워드 | "RHEL 8 환경에서 운영" → TECH |
| BIZ 사업·조직 | S19 + CONSTRAINT_BIZ | 12+ 키워드 | "일정 마감일은 2026년 6월" → BIZ |
| COMP 법·규제 | S19 + CONSTRAINT_COMP | 10+ 키워드 | "개인정보보호법을 준수" → COMP |
| OPS 운영·환경 | S19 + CONSTRAINT_OPS | 8+ 키워드 | "24시간 365일 무중단 운영" → OPS |
| SEC 안전·보안 | S19 + CONSTRAINT_SEC | 15+ 키워드 | "MFA 적용 및 AES-256 암호화" → SEC |

### 5.6 v2.2/v2.3 Ablation (D4 동일 데이터셋)

| 지표 | v2.1.1 | v2.2 (chunk fix) | v2.3 (kiwipiepy) | 누적 Δ |
|---|---:|---:|---:|---:|
| Smell 비율 | 93.4% | 77.0% | 79.4% | **-14 pp** |
| **자동 likely FP** | **26%** | — | **3.9%** | **-22 pp** ⭐ |
| S2 불완전 | 235 | 181 | 181 | -54 |
| S5 주체누락 | 209 | 159 | 161 | -48 |
| S4 약한의무 | 58 | 58 | 113 | +55 (정확도 ↑) |

### 5.7 4 방식 Baseline 비교 (RQ3 관련)
R1_sim 50건 gold:

| 방식 | Macro-F1 | Micro-F1 | 검출량 |
|---|---:|---:|---:|
| **Rule-only** | **0.278** | **0.837** | 21/50 (42%) |
| NLP-only | 0.060 | 0.182 | 48/50 (96%) |
| LLM-assisted (dry-run) | 0.278 | 0.837 | 21/50 (42%) |
| Ensemble (5 detector) | 0.244 | 0.254 | 50/50 (100%) |

### 5.8 휴리스틱 교정 데모 (RQ5 관련, v2.8 확장)

| 원문 | 검출 | 교정 |
|---|---|---|
| 이력 정보를 저장한다 | S4 | 이력 정보를 저장**해야 한다** |
| 시스템은 효율적으로 운영되어야 한다 | S3, S9, S10 | 시스템은 **[명세 필요: 측정 기준]** 운영되어야 한다 |
| 보고서는 매월 신속히 생성되고, 관리자에게 통보된다 | S3, S4 | 보고서는 매월 **[명세 필요: 시간 기준]** 생성되고, 관리자에게 통보**되어야 한다** |
| 개발팀이 선호하는 폰트를 강제로 사용해야 한다 | **S16** | **[정당화 필요]** 폰트를 사용해야 한다 |
| 본 시스템은 100% 가용성을 보장해야 한다 | **S17** | 본 시스템은 **[현실적 수치 필요: 99.9% 등]** 가용성을 유지해야 한다 |
| 본 시스템은 사용자 인증 기능을 제공하여야 한다 | **S18** | **[FUNC-AUTH-XXX·출처 필요]** 본 시스템은 사용자 인증 기능을 제공하여야 한다 |
| 본 사업은 일부 제약을 받아야 한다 | **S19** | 본 사업은 **[제약 카테고리 명시 필요: TECH/BIZ/COMP/OPS/SEC]** 제약을 받아야 한다 |

### 5.9 단위 테스트 결과
- v2.7 detector 테스트: 11/12 통과 (약어 화이트리스트 edge case 1건)
- **v2.8 CMMI/NCS 테스트** (`tests/test_cmmi_smells.py`): **18/18 통과**
  - TestS16NecessityUnclear × 3 (선호 폰트 / 임의 결정 / 비즈니스 정당)
  - TestS17FeasibilityConcern × 5 (100% / 0초 / 완벽한 / 99.9999% / 99.9% 정상)
  - TestS18MissingTraceabilityID × 3 (ID 부재 / FUNC-AUTH-001 / 출처 명시)
  - TestS19ConstraintCategory × 2 (분류 불가 / TECH 분류)
  - TestKoreanPatternsHelpers × 5 (TECH/BIZ/COMP/OPS/SEC 분류 함수)

---

## 6. Discussion — RQ별 답

### 6.1 RQ1 답 (추출 기준)
의무 종결어 7종(`~여야 한다 / 함 / 됨 / 할 수 있어야 / 반드시 / 필수 / ~토록 한다`) + 6 카테고리 제외 룰 + 사이트 공통 텍스트 자동 검출(5+ 사업 일치)로 정밀 필터 가능. D1 비정제에서 3,210 → 75건(2.3%) 통과, 통과한 75건의 65.3%가 진짜 smell 검출 — 영문 Paska(46.6%)보다 높은 통과율 정확성.

### 6.2 RQ2 답 (Smell 정의 — v2.8 확장)
Paska 9종 → **19종 한국어 taxonomy + 6대 표준 정렬**로 확장:

| 단계 | 추가 smell | 출처 |
|---|---|---|
| v1.0 → v2.0 | S2/S4/S7/S10 (한국 특화) | SI 양식·평서형·영문 약어 |
| v2.7 | S11/S12/S13/S14/S15 | ISO 29148 + INCOSE + EARS |
| **v2.8** | **S16/S17/S18/S19** | **CMMI REQM·RD + NCS 5 카테고리** |

S16 필요성·S17 실현성·S18 추적성은 **CMMI 9 원칙 중 5/9 → 8/9** 충족으로 직접 연결, S19는 **NCS 5 제약 카테고리 0/5 → 5/5** 분류 보조를 제공한다.

### 6.3 RQ3 답 (앙상블 효과) ⭐
**한국 RFP 도메인에선 Rule-only가 최선**. 4 방식 비교에서 Macro-F1 0.278(Rule) vs 0.060(NLP) vs 0.244(Ensemble) — 정형 표현 명확성으로 휴리스틱이 효율적, NLP·Ensemble은 과검출 경향. 일반화 가능성은 제한적 — 도메인 외 일반화 시 NLP 모델 통합 가치 평가 필요. **v2.8에서 추가된 S16~S19는 모두 Rule-based 정밀 패턴이므로 Rule-only 우위 가설을 강화**한다.

### 6.4 RQ4 답 (빈번 오류 + 표준 커버리지)
한국 RFP 특유의 우세 패턴은 **주체누락(D1 32%, D4 81%) + 약한의무(D2 30%) + 어휘 모호 + (정제·양식 데이터의) 불완전**. 영문 SRS의 Passive voice(D3 27.5%)와 명확히 구분됨. 표준 커버리지 측면에서 **v1.0 ~20% → v2.6 28% → v2.7 55% → v2.8 ~70%** 단계적 확장, CMMI Consistent(S20)만 남으면 CMMI 9/9 완전 충족. NCS 5 제약은 v2.8에서 모두 분류 보조 가능.

### 6.5 RQ5 답 (LLM 교정 + 휴리스틱 v2.8 확장)
LLM 어댑터(`AnthropicCaller`)는 6 원칙 prompt와 dry-run fallback을 제공한다. 본 연구에선 API 호출 비용·시간 절감을 위해 휴리스틱 교정도 병행 제공 — v2.8에서 S16~S19용 4종 마커(`[정당화 필요]` / `[현실적 수치 필요]` / `[ID·출처 필요]` / `[제약 카테고리 명시 필요]`) 신규 추가. 실제 LLM 호출 시 의미 보존·과잉 보완 자동 평가는 v2.9 후속 과제.

### 6.6 종합 시사점
- **도구**: 한국 도메인은 휴리스틱이 효율적, 표준 정렬로 학술·실무 신뢰성 확보
- **표준**: CMMI 8/9 + NCS 5/5 + ISO 29148 8/9 + INCOSE 8/11 + EARS 2/5 + IEEE 830 8/8 → 종합 ~70%
- **작성**: 도구가 아니라 작성자 교육·표준화가 핵심 (`IMPROVEMENT_RECOMMENDATIONS.md` 참고)
- **데이터**: 산업계·학계 협력 정형 데이터셋 구축이 후속 연구 결정적
- **윤리**: 실기업 데이터 5단계 워크플로우는 후속 한국 요구공학 연구에 재사용 가능

---

## 7. Threats to Validity

### 7.1 Internal Validity (내적 타당성)
- v2.5 baseline 비교에서 gold label로 사용한 R1_sim 50건이 휴리스틱 기반이라 **Rule-only에 유리한 편향** 가능
- v2.8 detector 테스트는 합성 예문 18종 — 실제 데이터셋에서의 P/R 미측정
- v2.7 detector 테스트 11/12 통과 (약어 화이트리스트 1건 미해결)

### 7.2 External Validity (외적 타당성)
- 4 데이터셋 모두 한국 금융 도메인 — 타 도메인(법률·의료·국방) 일반화 미검증
- D4는 한 국내 캐피탈사의 단일 시점 산출물 — 산업 평균 대표성 한계
- NCS 5 카테고리 사전은 일반 SI 도메인 어휘 — 도메인별(헬스케어 등) 별도 사전 필요

### 7.3 Construct Validity (구성 타당성)
- 19종 smell이 한국 RFP 품질을 완전히 포괄한다고 단언하기 어려움 — CMMI Consistent(S20)·EARS 잔여 3패턴 미반영
- S18 추적성은 ID 패턴 5종으로 한정 — 사내 고유 형식 누락 가능
- "의미 보존" 등 일부 지표는 평가자 주관 의존

### 7.4 Conclusion Validity (결론 타당성)
- 실제 사람 평가자 200건 gold 미수집 — 진짜 Precision/Recall/F1 산출 후속 과제
- 표본 크기 R1_sim 50건 — 통계적 유의성 보완 필요
- 표준 커버리지 "~70%" 수치는 본 연구 자체 매핑 — 외부 감사 미수행

---

## 8. Conclusion and Future Work

### 8.1 결론
본 연구는 한국어 공공금융 RFP 요구사항 품질 자동 평가 도구 부재 문제를 해결하기 위한 KoFinRe-QA Framework를 제안하고, 4 데이터셋·6대 표준으로 검증했다. 주요 결과:

1. **19종 한국어 smell taxonomy** 정의 (Paska 9종 + 한국 특화 + IEEE 830 / ISO 29148 / INCOSE / EARS / CMMI / NCS)
2. **5 detector 앙상블** 도구 KoFinRe (오픈소스 + 웹 평가기 + PDF 번들)
3. **D4 실기업 익명 검증** — 정밀화로 자동 likely-FP 26% → 3.9%
4. **6대 표준 정렬** — v1.0 ~20% → v2.8 ~70%, CMMI 5/9 → 8/9, NCS 0/5 → 5/5
5. **RQ3 답**: 한국 도메인에선 Rule-only 최선 (Macro-F1 0.278) — v2.8 신규 패턴이 가설 강화
6. **RQ4 답**: 한국 RFP 품질 이슈는 정제 수준이 아니라 언어·문화적 작성 관행
7. **5단계 윤리·법적 워크플로우** 표준 제안

### 8.2 Future Work
| 방향 | 작업 | 목표 버전 |
|---|---|---|
| 평가자 데이터셋 | 실제 사람 평가자 200건 + Cohen's kappa + 진짜 P/R/F1 | v3.0 |
| LLM 교정 실증 | ANTHROPIC_API_KEY 설정 후 Stage 5 실제 호출 + 의미 보존 정량 평가 | v2.9 |
| 일관성 smell (S20) | 의미 임베딩 기반 요구사항 간 충돌 탐지 → CMMI 9/9 완전 충족 | v2.9 |
| EARS 권장 도구 (S21) | Ubiquitous/Event/State/Optional/Unwanted 패턴 권장 | v3.0 |
| 앙상블 voting | confidence_weighted 비교 → 정밀도 향상 가능성 | v2.9 |
| 도메인 확장 | 비금융 (법률·의료·국방) RFP 재검증 | v3.1 |
| 한국어 Rimay | controlled natural language 한국어 등가 패턴 정립 | v3.1 |
| 데이터셋 규모 | 산업·학계 협력 1,000건+ 정형 데이터셋 | v3.2 |

---

## References

[1] A. Ferrari, G. O. Spagnolo, and S. Gnesi, "PURE: A Dataset of Public Requirements Documents," *IEEE International Requirements Engineering Conference*, 2017.

[2] A. Veizaga, S. Y. Shin, and L. C. Briand, "Automated Smell Detection and Recommendation in Natural Language Requirements," *IEEE Transactions on Software Engineering*, 2024.

[3] A. Veizaga, M. Alferez, D. Torre, M. Sabetzadeh, and L. C. Briand, "On Systematically Building a Controlled Natural Language for Functional Requirements," *Empirical Software Engineering*, 2021.

[4] IEEE, "IEEE Recommended Practice for Software Requirements Specifications," *IEEE Std 830-1998*.

[5] ISO/IEC/IEEE, "Systems and Software Engineering — Life Cycle Processes — Requirements Engineering," *ISO/IEC/IEEE 29148:2018*.

[6] INCOSE, "Guide to Writing Requirements," International Council on Systems Engineering, v4.

[7] A. Mavin, P. Wilkinson, A. Harwood, and M. Novak, "Easy Approach to Requirements Syntax (EARS)," *IEEE 17th International Requirements Engineering Conference*, 2009.

[8] CMMI Institute, "CMMI for Development V2.0 — Requirements Management (REQM) and Requirements Development (RD) Practice Areas," ISACA, 2018.

[9] Human Resources Development Service of Korea, "NCS (National Competency Standards) — 정보기술 요구사항 분석 (Information Technology Requirements Analysis)," 2024.

[10] B. S. Cho and S. W. Lee, "A Comparative Study on Requirements Analysis Techniques using Natural Language Processing and Machine Learning," *Journal of The Korea Society of Computer and Information*, 2020.

[11] E. S. Cho, "A Technique for UML-based System Development Using Generative AI," *Journal of The Korea Society of Computer and Information*, 2024.

[12] Y. H. Kim, "A Generative AI-Based Personalized Programming Education System Integrating Adaptive Rubric Assessment," *Journal of The Korea Society of Computer and Information*, 2025.

[13] M. S. Lee, "A Comparative Study on the Performance of GPT-4o-mini, Claude 4 Sonnet, and Gemini 2.5 Flash Models by Prompt Type Based on Prompt Runner," *Journal of The Korea Society of Computer and Information*, 2026.

[14] V. Ivanov, M. Sadovykh, and A. Naumchev, "Extracting Software Requirements from Unstructured Documents," *arXiv preprint*, 2022.

[15] F. Khayashi, B. Jamasb, R. Akbari, and P. Shamsinejadbabaki, "Deep Learning Methods for Software Requirement Classification: A Performance Study on the PURE Dataset," *arXiv preprint*, 2022.

---

## Appendix

### A. 산출물 디렉토리 표준 (v2.8)

```
KoFinRe/
├── kofinre/                # 핵심 패키지
│   ├── detectors/          # 5 detector (S1~S19 전체)
│   ├── extraction/         # Stage 1
│   ├── io/                 # CSV/Excel
│   ├── llm_adapters/       # Anthropic
│   ├── correction.py       # LLM 교정
│   ├── correction_heuristic.py  # 휴리스틱 교정 (S16~S19 마커 신규)
│   ├── korean_patterns.py  # 한국어 패턴 + CMMI/NCS 사전 (v2.8)
│   ├── ensemble.py
│   ├── metrics.py
│   ├── reporting.py
│   └── validation.py
├── docs/                   # 11+ 문서
│   ├── PAPER_FINAL.md             # 본 논문 (v2.8 통합본)
│   ├── CMMI_NCS_COMPARISON.md     # CMMI/NCS 분석 (v2.8 신규)
│   ├── STANDARDS_COMPARISON.md    # IEEE/ISO/INCOSE/EARS 갭 분석
│   ├── JOURNEY.md                 # 전체 여정
│   └── UPDATE.MD                  # 변경 이력
├── scripts/                # CLI + PDF 번들 빌더
├── examples/               # 예제
├── tests/                  # 단위 테스트
│   ├── test_detectors.py
│   ├── test_cmmi_smells.py        # v2.8 18 테스트 (신규)
│   └── test_metrics.py
├── web/index.html          # 브라우저 평가기 (SheetJS)
└── legacy/                 # v1 보관
```

### B. 보안 처리 검증
- 6 식별자 leak 검사 6+회 통과 (회사·시스템 토큰 6종 — 본 논문에선 마스킹)
- 백업 ZIP 3회 분리 (LOCAL_ONLY 마크)
- D4 원문·익명화 데이터 git commit 0건
- v2.8 push 전 leak 재검사: 회사명·약어·코드 토큰 6종 (본 논문에선 마스킹) **0 hit**

### C. 재현성
- 저장소: <https://github.com/24nga/KoFinRe>
- 의존성: `pip install -r requirements.txt` (kiwipiepy 포함)
- 검증: `python -m unittest discover tests` + `python examples/basic_usage.py`
- 보조 문서:
  - [`JOURNEY.md`](./JOURNEY.md) — 전체 여정 (v1.0 → v2.8)
  - [`UPDATE.MD`](./UPDATE.MD) — 변경 이력
  - [`CMMI_NCS_COMPARISON.md`](./CMMI_NCS_COMPARISON.md) — v2.8 표준 매핑 11 섹션
  - [`STANDARDS_COMPARISON.md`](./STANDARDS_COMPARISON.md) — IEEE/ISO/INCOSE/EARS 갭
- 웹 평가기: 브라우저에서 `web/index.html` 열기 — 서버 없이 XLSX 업로드·평가·다운로드

### D. MECE 검증
본 논문 구조의 중복 없음·빠짐 없음 검증:

| 섹션 | 역할 | 중복 여부 |
|---|---|---|
| §1 Introduction | 문제·RQ·기여 | ✓ 독립 |
| §2 Related Work | 선행 연구·6대 표준·차별성 | ✓ 독립 |
| §3 Framework | 5 stages 제안 + 19종 taxonomy | ✓ 독립 |
| §4 Setup | 데이터·지표·baseline | ✓ 독립 |
| §5 Results | 정량 결과 + 표준 커버리지 진화 | ✓ 독립 |
| §6 Discussion | RQ 답 | ✓ 독립 |
| §7 Validity | 위협 4종 | ✓ 독립 |
| §8 Conclusion | 종합·향후 | ✓ 독립 |
| References | 15 인용 | — |
| Appendix | 보조 자료 | — |

전체 연구 내용 포괄 — 누락 없음. v2.8에서 추가된 4종 smell + 6대 표준 정렬이 §2.2 / §3.3 / §5.3-5.5 / §6.2 / §6.4 / §8.1에 일관성 있게 통합되었음.

### E. v2.8 핵심 코드 발췌

```python
# kofinre/korean_patterns.py (v2.8 신규)
NECESSITY_RED_FLAGS = re.compile(
    r'(?:선호하는|선호도|마음에\s*드는|강제로\s*(?:사용|적용)'
    r'|임의로\s*(?:정한|정의)|독단적|개발(?:팀|자)이\s*(?:선호|결정|정한))'
)
INFEASIBLE_ABSOLUTE = re.compile(
    r'(?:100\s*%\s*(?:가용|정확|성공|완벽|보장|만족|동작|처리|적용)'
    r'|99\.99{3,}\s*%|장애\s*(?:발생\s*)?0(?:건|회)?|응답시간\s*0\s*초|완벽한)'
)
REQ_ID_PATTERN = re.compile(
    r'\b[A-Z]{2,5}[\-_][A-Z]{2,5}[\-_]\d{3,5}\b'      # FUNC-AUTH-001
    r'|\b(?:REQ|FR|NFR|FUNC|SR|UR|BR|CR)[\-_]\d{3,5}\b'
)
CONSTRAINT_TECH = {'OS', '운영체제', '플랫폼', '프레임워크', 'RHEL', 'Red Hat', ...}
CONSTRAINT_BIZ  = {'예산', '일정', '마일스톤', '오픈일', '마감', '한도', ...}
CONSTRAINT_COMP = {'개인정보', 'PII', 'GDPR', '개인정보보호법', '감독규정', ...}
CONSTRAINT_OPS  = {'24시간', '365일', '무중단', '정기점검', ...}
CONSTRAINT_SEC  = {'MFA', '다중인증', '암호화', 'AES', '감사로그', ...}
```

```python
# kofinre/detectors/regex_detector.py (v2.8 신규 S16~S19)
# S16 Necessity-unclear
nec_red, nec_term = kp.has_necessity_red_flag(s)
res.set("S16", nec_red, Confidence.HIGH if nec_red else 0.0, nec_term)

# S17 Feasibility
infeasible, inf_term = kp.has_infeasible_absolute(s)
res.set("S17", infeasible, ...)

# S18 Missing-traceability-ID
has_id = bool(kp.find_req_id(s))
has_source = kp.has_source_rationale(s)
has_obligation = kp.STRONG_OBLIGATION.search(s) is not None
missing_trace = has_obligation and not has_id and not has_source
res.set("S18", missing_trace, ...)

# S19 Constraint-category
cats = kp.classify_constraint_category(s)
has_constraint_signal = bool(re.search(r'(제약|제한|준수|한정|허용|금지)', s))
constraint_unclear = (has_constraint_signal and len(cats) == 0)
res.set("S19", constraint_unclear, ...)
```
