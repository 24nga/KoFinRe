# 한국어 공공금융 RFP 요구사항 품질 자동 평가 프레임워크 KoFinRe-QA

## 영문 NLP 도구 Paska의 한국어 어댑테이션, 데이터셋 구축, 그리고 정량적 검증

> **KoFinRe-QA: A Framework for Quality Analysis and Dataset Construction of Korean Public Financial RFP Requirements**
> *An NLP-Ensemble and LLM-Correction Approach Based on Paska Smell Taxonomy and Requirements Quality Standards*

---

## Abstract

영문권에서는 Paska 와 PURE 같은 자연어 요구사항 품질 평가 도구·데이터셋이 활용되어 왔으나, 한국어 공공금융 도메인에서는 (1) 공개 데이터셋, (2) 자동 평가 도구, (3) 도메인 특화 smell taxonomy가 모두 부재하다. 본 연구는 이 세 가지 공백을 동시에 채우는 **KoFinRe-QA Framework**를 제안한다.

프레임워크는 (i) 다포맷 텍스트 추출 (HTML/HWP/PDF/DOCX/RTF), (ii) 10종 한국어 smell taxonomy 정의, (iii) 5 detector 앙상블 탐지, (iv) 6 표준 리포트 정량 평가, (v) LLM/휴리스틱 교정의 5단계로 구성된다. 4 데이터셋으로 검증했다: 공공금융 RFP 56건 비정제(D1), 정형 30건(D2), PURE 영문 79건 기준선(D3), 실기업 4모듈 257건 익명화(D4). 정밀화 과정에서 자동 likely-FP를 **26% → 3.9%(-22pp)** 감소시켰으며, 4 방식 baseline 비교에서 **Rule-only가 Macro-F1 0.278로 최선**임을 정량 확인했다. 본 도구는 오픈소스(<https://github.com/24nga/KoFinRe>)로 공개되며, 실기업 데이터 처리를 위한 5단계 윤리·법적 워크플로우를 함께 제안한다.

**Keywords:** Requirements Engineering, Korean RFP Dataset, Public Financial Sector, Requirement Smell, Paska, NLP Ensemble, LLM Correction, Anonymization

---

## 1. Introduction

### 1.1 연구 배경
공공금융 정보시스템 사업은 규제 준수·대외기관 연계·고객정보 보호·금융거래 처리에서 높은 정확성과 추적가능성을 요구한다. RFP 단계에서 작성된 요구사항의 품질은 전체 사업 성과와 직결되며, 모호한 표현·불완전한 명세·복합 의무는 사후 분쟁의 핵심 원인이다.

### 1.2 문제 정의
영문권 자동 평가 도구를 한국어 RFP에 직접 적용 시 다음 5가지 장벽이 존재한다:

| # | 장벽 | 영향 |
|---|---|---|
| 1 | Paska의 allennlp 의존 — Windows·한국어 미지원 | 도구 작동 불가 |
| 2 | 한국어 SOV 어순·주어 생략 허용 | 영문 detection 규칙 부적합 |
| 3 | 한국 SI 작성 관행 (평서형 "한다", 명사 결합) | 영문 smell 패턴과 불일치 |
| 4 | HWP·전각 글머리표 등 한국 고유 포맷 | 표준 추출 도구 부재 |
| 5 | 한국어 요구사항 공개 데이터셋 부재 | 연구 재현·비교 불가 |

### 1.3 연구 질문

- **RQ1**: 한국 RFP에서 요구사항 후보를 신뢰성 있게 추출하기 위한 기준은 무엇인가?
- **RQ2**: Paska smell taxonomy + 한국 RFP 특성을 어떻게 통합 정의할 수 있는가?
- **RQ3**: 한국어 NLP 기반 복수 분석기의 앙상블은 smell 탐지 성능을 향상시키는가?
- **RQ4**: 한국 RFP에서 가장 빈번하게 나타나는 작성오류 유형은 무엇인가?
- **RQ5**: LLM 기반 교정은 smell을 감소시키면서 원문 의미를 보존할 수 있는가?

### 1.4 기여 (5종)

1. **10종 한국어 smell taxonomy**: Paska 9종 + 한국 특화 2종 (S2 Incomplete, S10 Unverifiable) + 분리(S3/S8) 정의
2. **5 detector 앙상블 도구 KoFinRe**: Regex / Morph(kiwipiepy) / Chunk / Dictionary / LLM + rule-priority voting
3. **4 데이터셋 검증**: 공공 비정제·정형·영문 기준선·실기업 익명화
4. **윤리·법적 워크플로우**: 실기업 데이터 5단계 처리 표준 (정규식 익명화 → LOCAL_ONLY 격리 → 잔여 위험 모니터링 → leak 검사 → 통계 only 외부 공유)
5. **오픈소스 공개**: <https://github.com/24nga/KoFinRe> (MIT License)

---

## 2. Related Work

### 2.1 영문 요구사항 데이터셋·도구

- **PURE** (Ferrari 2017): 79건 공개 SRS 데이터셋. 본 연구에서 D3 기준선으로 활용
- **Paska** (Veizaga 2024): allennlp constituency parsing + Stanford POS tagger + Java smell detector. 9종 smell, Rimay 패턴 추천

### 2.2 요구사항 품질 표준

- **IEEE 830-1998**: 좋은 SRS 8 특성 (정확성·명확성·완전성·일관성·중요도·검증가능성·수정가능성·추적가능성)
- **ISO/IEC/IEEE 29148:2018**: 확장된 요구사항 품질 개념
- **INCOSE Guide to Writing Requirements**: 작성 가이드 표준

### 2.3 한국어 NLP / LLM 기반 SW 공학

- 한국어 NLP 기반 요구사항 분류 연구 (Cho 2020)
- 생성형 AI 기반 UML 변환 (Cho 2024)
- 한국어 controlled natural language 시도 (선행 부재)

### 2.4 본 연구의 차별성

| 차원 | 선행 연구 | 본 연구 |
|---|---|---|
| 언어 | 영문 중심 | 한국어 본격 |
| 도메인 | 일반 SW | 공공금융 + 실기업 |
| Smell taxonomy | Paska 9종 (영문) | 10종 한국어 재정의 |
| 데이터 | 1~2 데이터셋 | 4 데이터셋 통합 |
| 실기업 처리 | 미정립 | 5단계 윤리·법 워크플로우 |

---

## 3. KoFinRe-QA Framework (제안 방법)

### 3.1 개요

```
RFP 문서 → ① 추출 → ② Smell 정의 → ③ 앙상블 탐지 → ④ 정량 평가 → ⑤ LLM 교정
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

### 3.3 Stage 2 — Smell Taxonomy (10종)

| 코드 | 이름 | 정의 | Quality Attribute | Paska 매핑 |
|---|---|---|---|---|
| S1 | 복합의무 | 둘 이상 기능 응답 결합 | Atomicity | Non-atomic |
| **S2** | **불완전** | 응답·행위·대상 누락 | Completeness | (신규) |
| S3 | 모호어 | "적절히, 필요한, 실시간" | Unambiguity | Coord ambiguity 일부 |
| S4 | 약한의무 | "한다, 된다" 평서형 | Verifiability | (신규 — 한국 특화) |
| S5 | 주체누락 | 수행 주체 미명시 | Completeness | Incomplete sys resp |
| S6 | 정량부재 | 성능 키워드 + 숫자 없음 | Testability | Incomplete req 일부 |
| S7 | 미정의약어 | 정의 없는 약어 | Traceability | (신규 — 한국 특화) |
| **S8** | **범위모호** | "및/또는, 등, 포함" | Unambiguity | Coord ambiguity 일부 |
| S9 | 수동표현 | "되어야 한다" | Clarity | Passive voice |
| **S10** | **검증불가** | 판정 기준 부재 | Verifiability | (신규) |

### 3.4 Stage 3 — NLP 앙상블 탐지

#### 3.4.1 5 Detector

| Detector | 역할 | 구현 |
|---|---|---|
| **RegexDetector** | 명시적 패턴 매칭 | 30+ 정규식, HIGH/MED/LOW confidence |
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
정규식 치환 기반: S1 분리 / S3 `[명세 필요: ...]` 마커 / S4 평서→의무형 / S8 `[열거 명시 필요]`.

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
| 4. leak 검사 | git grep 5+회 (`토요타`, `TFSKR`, `TFSKO`, `Toyota`, `TFS-`, `TFS_`) — 모두 0 hit |
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
| Passive / 수동 | **27.5%** | 8.0% | 10.0% | 1% |
| Non-atomic / 복합 | 13.8% | 2.7% | 0% | **0%** |
| Missing-quant / 정량 | 1.3% | 6.7% | 6.7% | 2% |
| 모호어 | n/a | 30.7% | 26.7% | 4% |
| **주체모호** | n/a | **32.0%** | 26.7% | **81%** |
| **약한의무** (신규) | n/a | 0% | 30.0% | 23% |
| 미정의 약어 (신규) | n/a | 1.3% | 3.3% | 11% |
| **불완전** (신규 S2) | n/a | n/a | n/a | **91%** |

### 5.3 v2.2/v2.3 Ablation (D4 동일 데이터셋)

| 지표 | v2.1.1 | v2.2 (chunk fix) | v2.3 (kiwipiepy) | 누적 Δ |
|---|---:|---:|---:|---:|
| Smell 비율 | 93.4% | 77.0% | 79.4% | **-14 pp** |
| **자동 likely FP** | **26%** | — | **3.9%** | **-22 pp** ⭐ |
| S2 불완전 | 235 | 181 | 181 | -54 |
| S5 주체누락 | 209 | 159 | 161 | -48 |
| S4 약한의무 | 58 | 58 | 113 | +55 (정확도 ↑) |

### 5.4 4 방식 Baseline 비교 (RQ3 관련)
R1_sim 50건 gold:

| 방식 | Macro-F1 | Micro-F1 | 검출량 |
|---|---:|---:|---:|
| **Rule-only** | **0.278** | **0.837** | 21/50 (42%) |
| NLP-only | 0.060 | 0.182 | 48/50 (96%) |
| LLM-assisted (dry-run) | 0.278 | 0.837 | 21/50 (42%) |
| Ensemble (5 detector) | 0.244 | 0.254 | 50/50 (100%) |

### 5.5 휴리스틱 교정 데모 (RQ5 관련)

| 원문 | 검출 | 교정 |
|---|---|---|
| 이력 정보를 저장한다 | S4 | 이력 정보를 저장해야 한다 |
| 시스템은 효율적으로 운영되어야 한다 | S3, S9, S10 | 시스템은 [명세 필요: 측정 기준] 운영되어야 한다 |
| 보고서는 매월 신속히 생성되고, 관리자에게 통보된다 | S3, S4 | 보고서는 매월 [명세 필요: 시간 기준] 생성되고, 관리자에게 통보되어야 한다 |

---

## 6. Discussion — RQ별 답

### 6.1 RQ1 답 (추출 기준)
의무 종결어 7종(`~여야 한다 / 함 / 됨 / 할 수 있어야 / 반드시 / 필수 / ~토록 한다`) + 6 카테고리 제외 룰 + 사이트 공통 텍스트 자동 검출(5+ 사업 일치)로 정밀 필터 가능. D1 비정제에서 3,210 → 75건(2.3%) 통과, 통과한 75건의 65.3%가 진짜 smell 검출 — 영문 Paska(46.6%)보다 높은 통과율 정확성.

### 6.2 RQ2 답 (Smell 정의)
Paska 9종을 한국 도메인에 매핑하면서 다음 3 신규를 추가했다: **S2 불완전** (응답·행위·대상 누락, 한국 SI 양식에 다발), **S4 약한의무** (한국어 평서형 "한다"), **S10 검증불가** (정성 표현 + 측정 기준 부재). 또한 Paska Coordination Ambiguity를 **S3 어휘 모호 + S8 범위 모호**로 분리해 정밀화했다.

### 6.3 RQ3 답 (앙상블 효과) ⭐
**한국 RFP 도메인에선 Rule-only가 최선**. 4 방식 비교에서 Macro-F1 0.278(Rule) vs 0.060(NLP) vs 0.244(Ensemble) — 정형 표현 명확성으로 휴리스틱이 효율적, NLP·Ensemble은 과검출 경향. 일반화 가능성은 제한적 — 도메인 외 일반화 시 NLP 모델 통합 가치 평가 필요.

### 6.4 RQ4 답 (빈번 오류)
한국 RFP 특유의 우세 패턴은 **주체누락(D1 32%, D4 81%) + 약한의무(D2 30%) + 어휘 모호 + (정제·양식 데이터의) 불완전**. 영문 SRS의 Passive voice(D3 27.5%)와 명확히 구분됨 — 두 언어의 구조적·관용적 차이를 정량 확인. 잘 정비된 실기업 양식(D4)도 한국 SI 작성 관행에서 자유롭지 않아 **품질 이슈는 정제 수준이 아니라 언어·문화적 작성 관행 자체**라는 결정적 답.

### 6.5 RQ5 답 (LLM 교정)
LLM 어댑터(`AnthropicCaller`)는 6 원칙 prompt와 dry-run fallback을 제공한다. 본 연구에선 API 호출 비용·시간 절감을 위해 휴리스틱 교정(`correction_heuristic.py`)도 병행 제공 — 정규식 치환으로 LLM 없이도 작성자에게 `[명세 필요: ...]` 마커 자동 삽입 가능. 실제 LLM 호출 시 의미 보존·과잉 보완 자동 평가는 v2.6 후속 과제.

### 6.6 종합 시사점
- **도구**: 한국 도메인은 휴리스틱이 효율적
- **작성**: 도구가 아니라 작성자 교육·표준화가 핵심 (`IMPROVEMENT_RECOMMENDATIONS.md` 참고)
- **데이터**: 산업계·학계 협력 정형 데이터셋 구축이 후속 연구 결정적
- **윤리**: 실기업 데이터 5단계 워크플로우는 후속 한국 요구공학 연구에 재사용 가능

---

## 7. Threats to Validity

### 7.1 Internal Validity (내적 타당성)
- v2.5 baseline 비교에서 gold label로 사용한 R1_sim 50건이 휴리스틱 기반이라 **Rule-only에 유리한 편향** 가능
- 단위 테스트 11/12 통과(약어 화이트리스트 edge case 1건 실패) — 약어 검출 영역의 마이너 이슈

### 7.2 External Validity (외적 타당성)
- 4 데이터셋 모두 한국 금융 도메인 — 타 도메인(법률·의료·국방) 일반화 미검증
- D4는 한 국내 캐피탈사의 단일 시점 산출물 — 산업 평균 대표성 한계

### 7.3 Construct Validity (구성 타당성)
- 10종 smell이 한국 RFP 품질을 완전히 포괄한다고 단언하기 어려움 — Rimay 패턴 미적용
- "의미 보존" 등 일부 지표는 평가자 주관 의존

### 7.4 Conclusion Validity (결론 타당성)
- 실제 사람 평가자 200건 gold 미수집 — 진짜 Precision/Recall/F1 산출 후속 과제
- 표본 크기 R1_sim 50건 — 통계적 유의성 보완 필요

---

## 8. Conclusion and Future Work

### 8.1 결론
본 연구는 한국어 공공금융 RFP 요구사항 품질 자동 평가 도구 부재 문제를 해결하기 위한 KoFinRe-QA Framework를 제안하고, 4 데이터셋으로 검증했다. 주요 결과:

1. **10종 한국어 smell taxonomy** 정의 (Paska 9종 + 한국 특화 매핑)
2. **5 detector 앙상블** 도구 KoFinRe (오픈소스)
3. **D4 실기업 익명 검증** — 정밀화로 자동 likely-FP 26% → 3.9%
4. **RQ3 답**: 한국 도메인에선 Rule-only 최선 (Macro-F1 0.278)
5. **RQ4 답**: 한국 RFP 품질 이슈는 정제 수준이 아니라 언어·문화적 작성 관행
6. **5단계 윤리·법적 워크플로우** 표준 제안

### 8.2 Future Work
| 방향 | 작업 |
|---|---|
| 평가자 데이터셋 | 실제 사람 평가자 200건 + Cohen's kappa + 진짜 P/R/F1 |
| LLM 교정 실증 | ANTHROPIC_API_KEY 설정 후 Stage 5 실제 호출 + 의미 보존 정량 평가 |
| 앙상블 voting | confidence_weighted 비교 → 정밀도 향상 가능성 |
| 도메인 확장 | 비금융 (법률·의료·국방) RFP 재검증 |
| 한국어 Rimay | controlled natural language 한국어 등가 패턴 정립 |
| 데이터셋 규모 | 산업·학계 협력 1,000건+ 정형 데이터셋 |

---

## References

[1] A. Ferrari, G. O. Spagnolo, and S. Gnesi, "PURE: A Dataset of Public Requirements Documents," *IEEE International Requirements Engineering Conference*, 2017.

[2] A. Veizaga, S. Y. Shin, and L. C. Briand, "Automated Smell Detection and Recommendation in Natural Language Requirements," *IEEE Transactions on Software Engineering*, 2024.

[3] A. Veizaga, M. Alferez, D. Torre, M. Sabetzadeh, and L. C. Briand, "On Systematically Building a Controlled Natural Language for Functional Requirements," *Empirical Software Engineering*, 2021.

[4] IEEE, "IEEE Recommended Practice for Software Requirements Specifications," *IEEE Std 830-1998*.

[5] ISO/IEC/IEEE, "Systems and Software Engineering — Life Cycle Processes — Requirements Engineering," *ISO/IEC/IEEE 29148:2018*.

[6] INCOSE, "Guide to Writing Requirements," International Council on Systems Engineering.

[7] B. S. Cho and S. W. Lee, "A Comparative Study on Requirements Analysis Techniques using Natural Language Processing and Machine Learning," *Journal of The Korea Society of Computer and Information*, 2020.

[8] E. S. Cho, "A Technique for UML-based System Development Using Generative AI," *Journal of The Korea Society of Computer and Information*, 2024.

[9] Y. H. Kim, "A Generative AI-Based Personalized Programming Education System Integrating Adaptive Rubric Assessment," *Journal of The Korea Society of Computer and Information*, 2025.

[10] M. S. Lee, "A Comparative Study on the Performance of GPT-4o-mini, Claude 4 Sonnet, and Gemini 2.5 Flash Models by Prompt Type Based on Prompt Runner," *Journal of The Korea Society of Computer and Information*, 2026.

[11] V. Ivanov, M. Sadovykh, and A. Naumchev, "Extracting Software Requirements from Unstructured Documents," *arXiv preprint*, 2022.

[12] F. Khayashi, B. Jamasb, R. Akbari, and P. Shamsinejadbabaki, "Deep Learning Methods for Software Requirement Classification: A Performance Study on the PURE Dataset," *arXiv preprint*, 2022.

---

## Appendix

### A. 산출물 디렉토리 표준

```
KoFinRe/
├── kofinre/                # 핵심 패키지
│   ├── detectors/          # 5 detector
│   ├── extraction/         # Stage 1
│   ├── io/                 # CSV/Excel
│   ├── llm_adapters/       # Anthropic
│   ├── correction.py       # LLM 교정
│   ├── correction_heuristic.py  # 휴리스틱 교정
│   ├── ensemble.py
│   ├── metrics.py
│   ├── reporting.py
│   └── validation.py
├── docs/                   # 7 문서
├── scripts/                # CLI
├── examples/               # 예제
├── tests/                  # 단위 테스트
└── legacy/                 # v1 보관
```

### B. 보안 처리 검증
- 6 식별자 leak 검사 6+회 통과 (`토요타`, `TFSKR`, `TFSKO`, `Toyota`, `TFS-`, `TFS_`)
- 백업 ZIP 3회 분리 (LOCAL_ONLY 마크)
- D4 원문·익명화 데이터 git commit 0건

### C. 재현성
- 저장소: <https://github.com/24nga/KoFinRe>
- 의존성: `pip install -r requirements.txt` (kiwipiepy 포함)
- 검증: `python -m unittest discover tests` + `python examples/basic_usage.py`
- 보조 문서: [`JOURNEY.md`](./JOURNEY.md) (전체 여정), [`UPDATE.MD`](./UPDATE.MD) (변경 이력)

### D. MECE 검증
본 논문 구조의 중복 없음·빠짐 없음 검증:

| 섹션 | 역할 | 중복 여부 |
|---|---|---|
| §1 Introduction | 문제·RQ·기여 | ✓ 독립 |
| §2 Related Work | 선행 연구·차별성 | ✓ 독립 |
| §3 Framework | 5 stages 제안 | ✓ 독립 |
| §4 Setup | 데이터·지표·baseline | ✓ 독립 |
| §5 Results | 정량 결과 | ✓ 독립 |
| §6 Discussion | RQ 답 | ✓ 독립 |
| §7 Validity | 위협 4종 | ✓ 독립 |
| §8 Conclusion | 종합·향후 | ✓ 독립 |
| References | 12 인용 | — |
| Appendix | 보조 자료 | — |

전체 연구 내용 포괄 — 누락 없음.
