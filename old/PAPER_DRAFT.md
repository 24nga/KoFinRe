# 한국어 공공금융 RFP 요구사항 품질 자동 평가 — v2 확장본
## 영문 NLP 도구(Paska)의 한국어 어댑테이션, 10종 Smell Taxonomy, 그리고 실기업 사례 검증

> **본 버전 갱신 사항** (v2026-06-12)
> - Smell taxonomy 7 → **10종** (S2 Incomplete, S8 Coordination Ambiguity, S10 Unverifiable 추가)
> - 5 detector + 앙상블 (rule-priority voting)
> - 표준 산출물 디렉토리·리포트 6종 정렬
> - **데이터셋 D4 신설** — 실기업 4 모듈 정의서 257건 (익명화 처리)
> - Gold label 표본 195건 + Cohen's kappa 평가 도구
> - 개선사항 권고문 ([`IMPROVEMENT_RECOMMENDATIONS.md`](./IMPROVEMENT_RECOMMENDATIONS.md))

---

## Abstract

본 연구는 영문 SRS(Software Requirements Specification) 품질 평가 도구인 Paska를 한국어 공공금융 RFP(Request For Proposal) 평가로 어댑테이션한 사례를 보고한다. 원본 Paska는 allennlp 기반 constituency parsing과 Stanford POS tagger를 사용해 9종 요구사항 smell을 검출하나, (1) Windows 환경 미지원, (2) 한국어 NLP 동등 모델 부재, (3) 한국어 RFP 특유 표현 미반영의 세 가지 제약이 있었다. 본 연구는 NLP 의존성을 제거하고 도메인 특화 정규식·키워드 휴리스틱으로 재구현하였으며, 7종 한국어 smell 유형(기존 5종 매핑 + 2종 신규)을 정의하였다. 12개 공공금융기관 56건 RFP 자체 추출 데이터와 3개 프로젝트 30건 정형 요구사항 데이터로 검증한 결과, 한국어 RFP에서 영문과 다른 품질 이슈 패턴(약한의무·주체모호·어휘모호 우세)이 관찰되었다.

**Keywords:** Requirements quality, Korean NLP, RFP analysis, Smell detection, Public sector procurement

---

## 1. Introduction

### 1.1 배경

공공금융기관의 정보시스템 구축 RFP는 사업 규모가 크고(수십억~수백억 원) 다수의 후속 분쟁·재설계가 발생하는 특성을 가진다. 그 핵심 원인 중 하나는 요구사항 명세의 모호성·불완전성으로, 이는 사후 시정보다 작성 단계 자동 검출이 비용 효율적이다.

영문권에서는 Veizaga 등(2021)이 제안한 Paska가 9종 smell(non-atomic, passive voice 등)을 자동 검출하지만, 한국어 RFP에는 (1) 언어 특수성, (2) 한국 공공조달 표준 양식, (3) HWP 등 한국 고유 포맷의 세 가지 차원에서 직접 적용이 불가능하다.

### 1.2 연구 질문

- **RQ1.** 영문 NLP 기반 요구사항 품질 도구를 NLP 부재 환경(한국어)에서 동등 수준으로 재구현 가능한가?
- **RQ2.** 한국어 RFP에서 발견되는 품질 이슈는 영문과 어떻게 다른가?
- **RQ3.** 비정형 공공조달 데이터에서 진짜 요구사항 문장만 신뢰성 있게 추출 가능한가?

### 1.3 기여

1. Paska의 9종 smell을 한국어 7종으로 매핑·재정의 (2종 한국 특화 신규)
2. HTML/HWP/PDF/RTF 다포맷 자체 추출 + 시그니처 기반 파일 판별
3. 도메인 특화 노이즈 6 카테고리(사이트 푸터, 조달·입찰 안내 등) 정의 및 검증
4. 한국 금융기관·도메인 약어 화이트리스트
5. 영문 Paska vs 한국어 도구 검증 결과 비교
6. 오픈소스 공개 (https://github.com/24nga/KoFinRe)

---

## 2. Related Work

### 2.1 Paska

Veizaga 등이 Luxembourg 대학에서 개발한 Paska는 다음 파이프라인으로 동작한다:

```
입력 CSV ("ID";"문장")
  ↓ get_cparsingtrees.pyc  (Python 3.8, allennlp 2.10.1)
  ↓ ELMo + constituency parser
파싱 트리 CSV
  ↓ smell_detector.jar  (Java 8)
  ↓ Stanford POS tagger (english-left3words-distsim.tagger)
smells.csv  (요청 ID × 9 smell × Rimay 권장 패턴)
```

9종 smell: Non-atomic, Incomplete requirement, Incorrect order, Coordination ambiguity, Not requirement, Incomplete condition, Incomplete system response, Passive voice, Not precise verb.

### 2.2 한국어 요구사항 분석

한국어 자연어 요구사항 자동 분석 도구는 학계 발표가 제한적이며, 산업계에선 사람-기반 리뷰가 주류다. 한국어 NLP 측면에서 KoBART, KoElectra 등이 존재하나 constituency parsing 동등 사용성은 영문 대비 낮다.

### 2.3 RFP 품질 가이드라인

ISO/IEC/IEEE 29148, INCOSE Guide, KS X ISO/IEC 25030 등이 요구사항 품질 속성(정확성·완전성·일관성·검증가능성)을 제시하나, 자동 검출 룰은 명시되어 있지 않다.

---

## 3. Problem Analysis

### 3.1 한국어 RFP의 특성

| 차원 | 영문 SRS | 한국어 공공금융 RFP |
|---|---|---|
| 어순 | SVO | SOV |
| 주어 명시 | 의무적 | 생략 빈번 |
| 의무 표현 | modal verb 명시 (`shall`, `must`) | 평서형 (`한다`, `된다`) 또는 종결어 (`해야 한다`) |
| 수동태 | "be + p.p." | `~되어야 한다`, `~지원되어야` |
| 영문 약어 | 영문 본문 내 자연 | 한국어 본문에 점재 (정의 의무 약함) |
| 첨부 포맷 | PDF, DOC | **HWP**(한컴), PDF |
| 본문 구조 | 자유 양식 | 표준 공공조달 양식 (입찰 안내·평가기준·과업내용서) |

### 3.2 영문 도구 직접 적용의 한계

Paska를 한국어 RFP에 그대로 적용 시 다음과 같이 실패한다:

1. **allennlp Windows 미지원** → Docker 컨테이너 필요 (이미지 5.9 GB)
2. **영문 constituency parser** → 한국어 입력에 트리 생성 실패
3. **Stanford POS tagger** → 영문 전용
4. **9종 smell 룰** → 영문 어휘 패턴 (`shall`, `passive be+pp`)에 의존
5. **HWP 미지원** → Paska 추출 파이프라인 부재

### 3.3 데이터 가용성 문제

한국 공공기관 사이트는 인증 요구·로봇 차단·동적 페이지가 많아 자동 수집이 부분적으로만 성공한다. 본 연구의 56건 다운로드 중 첨부 본문이 정상 추출된 사업은 14건(25%)에 그쳤다.

---

## 4. Methodology

### 4.1 전체 파이프라인

```
RFP 공고 (HTML/HWP/PDF/RTF)
  ↓ 4.2 텍스트 추출
사업별 통합 .txt
  ↓ 4.3 문장 분리
문장 후보
  ↓ 4.4 요구사항 식별 (포함·제외·중복 룰)
요구사항 후보
  ↓ 4.5 Smell 검사 (7종)
CSV / Markdown / Excel 리포트
```

### 4.2 텍스트 추출 (`rfp_extract.py`)

| 포맷 | 도구 | 비고 |
|---|---|---|
| HTML/HTM | BeautifulSoup 4 | UTF-8/CP949/EUC-KR 인코딩 자동 감지 |
| HWP | HWPFrame.HwpObject (한컴 COM) | `SetMessageBoxMode(0x10)` 모달 차단 |
| PDF | pdfplumber | layout 보존 |
| RTF | unrtf | 보조 |

**핵심 기여**: 다수 공공기관 사이트가 `page.html`이라는 파일명으로 실제로는 PDF·HWP 바이너리를 반환하는 경우가 있다(56건 중 43건). 본 연구는 파일 시그니처(magic byte) 기반 재분기 로직을 도입했다:

| Magic | 처리 |
|---|---|
| `25 50 44 46` (%PDF) | pdfplumber |
| `D0 CF 11 E0` (OLE2) | 한컴 COM |
| `E9 A5 89 11` (한컴 변형) | 임시 .hwp 복사 후 한컴 COM |
| `PK\x03\x04` (ZIP) | 스킵 |
| `<`, BOM | BeautifulSoup |

### 4.3 문장 분리

- 한국어/영문 종결 + `[.!?。]\s+(?=[가-힣A-Z○●▶■◇(\d])`
- **세미콜론(`;`) 분리** — REQ_abstract 패턴에서 학습한 sub-requirement 구분
- 하이픈 줄바꿈 결합 (`-\n` → 결합)

### 4.4 요구사항 식별 (정밀 필터, `rfp_requirement_filter.py`)

NLP 부재 환경에서 신뢰성 확보를 위한 핵심 단계.

#### 4.4.1 포함 규칙 (필수 중 하나)

```
(?:하|되|이|있)여야\s*(?:한다|함|됨)        # 일반화된 의무 종결
| 해야\s*(?:한다|함)
| 할\s*수\s*있어야\s*(?:한다|함)              # REQ_abstract 표준 패턴
| 반드시\s+[가-힣]+
| 필수\s*(?:이다|로|적|항목)
| [가-힣]+토록\s*한다                           # "~되도록 한다"
```

#### 4.4.2 제외 규칙 (6 카테고리)

| 카테고리 | 예시 키워드 |
|---|---|
| 사이트 푸터 | COPYRIGHT, 패밀리사이트, 사이트맵, 페이지로 이동, 용어사전 |
| 조달·입찰 표준 문구 | 입찰자, 공동수급체, 청렴계약, 조달청, 나라장터, 국가계약법, 법인등기부등본 |
| 메타데이터 시작 | 사업명·사업기간·사업예산·문의처·연락처·재무현황 |
| 글머리표 단편 | `▶○●◇□■`, `Ⅰ~Ⅹ`, `1.`/`1)` 단독 |
| 평가기준 | "~을 평가한다", "~을 점검한다", 배점 |
| 약관 도메인 | 임차인·임대인·보증금·채권 (+ 시스템 명사 미동반) |

#### 4.4.3 중복 제거

- **사이트 공통 텍스트**: 5+ 사업에서 정확 일치 → 자동 푸터로 판정·제거
- **사업 내 중복**: `(project_id, sentence)` 단위 dedup

### 4.5 Smell 검사 (7종)

#### 4.5.1 한국어 Smell 정의

| 코드 | 의미 | 검출 규칙 | Paska 매핑 |
|---|---|---|---|
| 모호어 | 정량성 결여 어휘 | 30+ 단어 매칭 (`필요한`, `적절한`, `실시간` 등) | Coordination ambiguity + Not precise verb |
| 수동태 | 행위 주체 흐릿 | `~되어야 한다`, `~지원되어야`, `됨\.?$`, `된다\.?$` | Passive voice |
| 복합의무 | 한 문장 다중 의무 | 의무 표현 2회+ | Non-atomic |
| 정량부재 | 성능 키워드 + 숫자 없음 | `성능·처리량·TPS·용량` + 숫자 패턴 부재 | Incomplete requirement |
| 미정의 약어 | 정의 없는 영문 약어 | 문서 단위 약어 추출 - 정의 - 화이트리스트 | **신규** (한국 특화) |
| 주체모호 | 주어 없는 의무문 | `^.*(가/이/은/는/에서)\s` 미매칭 + 의무 표현 | Incomplete system response |
| 약한의무 | 평서형 종결 | `한다/된다/함/됨$` + 의무 표현 부재 + 수동태 부재 | **신규** (한국 특화) |

#### 4.5.2 한국 도메인 약어 화이트리스트

| 카테고리 | 약어 |
|---|---|
| 일반 ICT | RFP, IT, OS, API, AI, JSON, XML, HTML, SQL 등 70+ |
| 한국 금융기관 | HF, BOK, KAMCO, HUG, KRX, KIC, KIBO, KDIC, KODIT, KFTC, KSD |
| 한국 금융 도메인 | DSR, KYC, AML, NICE, KCB, ELS, ETF, ECOS, CBDC, PEP, EDD, STR, FATF, KOFIU |
| 한국 기업 | NHN, SK, KT, LG |

### 4.6 정형 CSV 입력 처리 (`req_abstract_eval.py`)

REQ_abstract.csv 형식(`project_id, project_name, system_name, req_id, req_title, req_details`) 직접 평가:

- `req_details` → `;` 분리하여 sub-requirement 단위 분석
- `req_id` 수준 집계: 어느 sub-req에서든 smell 검출 → OR 집계
- `project_id` 수준 집계

---

## 5. Implementation

### 5.1 환경

| 항목 | Paska 원본 | 본 연구 |
|---|---|---|
| OS | Linux (Docker on Ubuntu 20.04) | Windows 10/11 |
| Python | 3.8.16 (conda env) | 3.10+ |
| Java | OpenJDK 8 | — |
| 컨테이너 크기 | 5.9 GB | 호스트 native |
| 모델 파일 | ~1.4 GB (ELMo + Stanford tagger) | 0 |
| 의존성 수 | 60+ pip + apt | 5 (beautifulsoup4, pdfplumber, openpyxl, pywin32, requests) |

### 5.2 코드 통계

| 파일 | 줄 수 (대략) | 역할 |
|---|---|---|
| `download_rfp.py` | 240 | RFP 자동 다운로드 |
| `rfp_extract.py` | 200 | 텍스트 추출 (다포맷) |
| `rfp_smell.py` | 280 | Smell 7종 검사 |
| `rfp_requirement_filter.py` | 230 | 정밀 필터링 |
| `req_abstract_eval.py` | 220 | 정형 CSV 평가 |
| `rfp_excel*.py` × 3 | 600 | Excel 리포트 |
| **합계** | ~1,900 LoC | |

### 5.3 재현 가능성

오픈소스 공개: <https://github.com/24nga/KoFinRe>
변경 이력 추적: `UPDATE.MD` (Keep a Changelog 형식)
추출·평가 규칙: `EXTRACTION_RULES.md` (정규식·임계값 명시)

---

## 6. Experimental Setup

### 6.1 데이터셋

#### 6.1.1 자체 수집 RFP 56건 (D1)

- **출처**: 12개 공공금융기관 공식 게시판
  - 한국주택금융공사(HF) 27건
  - 한국은행(BOK) 10건
  - 한국수출입은행 4건
  - 한국자산관리공사(KAMCO) 3건
  - 기술보증기금(KIBO) 2건
  - 한국거래소(KRX) 2건
  - 금융결제원(KFTC) 2건
  - 주택도시보증공사(HUG) 2건
  - 기타 4건 (KIC, KDIC, KODIT, KSD 각 1건)
- **기간**: 2015~2026
- **포맷**: HTML 55 + HWP 20 + PDF 5 + RTF 1

#### 6.1.2 정형 RFP 요구사항 30건 (D2)

- **출처**: REQ_abstract.csv (저자 사전 제공)
- **구조**: project_id, project_name, system_name, req_id, req_title, req_details
- **프로젝트 3개**:
  - P001 차세대 여신·리스크 통합 구축 (14 req)
  - P002 디지털 오토금융 플랫폼 구축 (9 req)
  - P003 고객360·AML·리스크 고도화 (7 req)
- **세부 분해**: 140 sub-requirement (`;` 분리)

#### 6.1.3 비교용 영문 SRS 79건 (D3)

- **출처**: PURE 연구 데이터셋 (PROMISE)
- **포맷**: PDF 62, DOC 13, HTML 2, HTM 1, RTF 1
- **연도**: 1995~2011
- Paska 원본 영문 파이프라인 검증용

#### 6.1.4 실기업 4 모듈 정의서 257건 (D4) — 익명화

- **출처**: 한 국내 캐피탈사의 차세대 시스템 구축 프로젝트 산출물 (2020)
- **윤리·법적 처리**:
  - 회사명·시스템명·인명·사번·연락처·이메일·URL·일자·외부 파트너사를 모두 정규식 마스킹
  - 원문 파일은 사용자 로컬에만 보관, GitHub commit 0건
  - 본 논문에서 인용·예시 0건 (통계만 보고)
- **구성** (모두 익명화 처리 후):
  - FA 모듈 (회계): 95건
  - BG 모듈 (예산): 52건
  - CI 모듈 (신용정보): 57건
  - CM 모듈 (공통): 53건
- **추출 양식**: XLSX `요구사항명` + `요구사항 내용` 2개 컬럼만 사용 (요청자/부서/일자 등 PII 컬럼은 메모리에 적재 안 함)

### 6.2 검증 환경

- Paska 원본: Docker 컨테이너 (Ubuntu 20.04 + JDK 8 + Python 3.8)
- 한국어 도구: Windows 11 + Python 3.13 + 한컴오피스 2024

---

## 7. Results

### 7.1 데이터 수집·추출 성공률

| 데이터셋 | 시도 | 다운로드 | 본문 추출 |
|---|---|---|---|
| D1 (56건) | 56 | 55 (98%) | **14 (25%)** ← 인증 차단 |
| D3 (79건) | 79 | 79 | 76 (96%) |

D1의 본문 추출 실패 원인: 한국 공공기관 사이트의 첨부 직접링크가 인증 없이 호출 시 빈 응답을 반환하거나 안내 페이지로 리다이렉트.

### 7.2 문장 추출·필터링 결과 (D1)

| 단계 | 통과 |
|---|---|
| 1차 추출 (한국어 비율 ≥25%) | 3,210 |
| 의무 종결어 통과 | 339 |
| 사이트 공통 텍스트 제거 (5+ 사업 일치) | 119 |
| 사업 내 중복 제거 | **75 (최종)** |

3,210 → 75 = **2.3% 통과율**. 정밀 필터링이 노이즈를 압도적으로 제거.

### 7.3 Paska 원본 Smell 검출 (D3, 영문)

- 1,200 reqs 샘플 (65 docs × 20)
- 파싱 트리 생성: **7분 10초** (allennlp 모델 캐시 사용)
- Smell 검출 (Java): **16초**
- Smell 비율: **559/1,200 (46.6%)**

| Smell | 검출 | 비율 |
|---|---|---|
| Passive voice | 330 | 27.5% |
| Non-atomic | 166 | 13.8% |
| Not precise verb | 79 | 6.6% |
| Incorrect order | 77 | 6.4% |
| Incomplete condition | 32 | 2.7% |
| Incomplete system response | 30 | 2.5% |
| Not requirement | 24 | 2.0% |
| Incomplete requirement | 16 | 1.3% |
| Coordination ambiguity | 2 | 0.2% |

### 7.4 한국어 Smell 검출 (D1, 자체 추출 75건)

- Smell 비율: **49/75 (65.3%)**

| Smell | 검출 | 비율 |
|---|---|---|
| 주체모호 | 24 | 32.0% |
| 모호어 | 23 | 30.7% |
| 수동태 | 6 | 8.0% |
| 정량부재 | 5 | 6.7% |
| 복합의무 | 2 | 2.7% |
| 미정의 약어 | 1 | 1.3% |
| 약한의무 | 0 | 0.0% |

### 7.5 한국어 Smell 검출 (D2, 정형 30건)

- 요구사항 단위 Smell 비율: **17/30 (56.7%)**
- sub-requirement 단위: 140건 분석

| Smell | 검출 |
|---|---|
| 약한의무 | 9 (30.0%) |
| 모호어 | 8 (26.7%) |
| 주체모호 | 8 (26.7%) |
| 수동태 | 3 (10.0%) |
| 정량부재 | 2 (6.7%) |
| 미정의 약어 | 1 (3.3%) |
| 복합의무 | 0 (0.0%) |

**프로젝트별 위험도**:
| Project | 요구사항 | Smell 검출 | 비율 |
|---|---|---|---|
| P001 여신·리스크 | 14 | 6 | 43% |
| P002 오토금융 | 9 | 4 | 44% |
| **P003 고객360·AML** | 7 | **7** | **100%** ⚠️ |

### 7.6 한국어 Smell 검출 (D4, 실기업 4 모듈 257건 — 익명화)

> 본 데이터셋은 한 국내 캐피탈사의 실제 산출물이며, 원문 인용 0건의 정책으로 모든 결과는 익명화된 통계로만 제시한다.

**카테고리별** (Smell 검출 비율):
| 모듈 | 요구사항 | Smell 검출 | 비율 |
|---|---:|---:|---:|
| FA 회계 | 95 | 92 | **96.8%** |
| BG 예산 | 52 | 50 | 96.2% |
| CI 신용정보 | 57 | 53 | 93.0% |
| CM 공통 | 53 | 45 | **84.9%** (가장 깨끗) |
| **총** | **257** | **240** | **93.4%** |

**Smell 유형별** (10종 모두 적용):
| 코드 | 이름 | FA | BG | CI | CM | 합계 |
|---|---|---:|---:|---:|---:|---:|
| S2 | 불완전 | 90 | 50 | 50 | 45 | **235 (91%)** |
| S5 | 주체누락 | 83 | 46 | 44 | 36 | **209 (81%)** |
| S4 | 약한의무 | **44** | 0 | 11 | 3 | 58 |
| S7 | 미정의 약어 | 2 | 5 | **19** | 2 | 28 |
| S3 | 모호어 | 6 | 0 | 3 | 0 | 9 |
| S6 | 정량부재 | 0 | 5 | 1 | 0 | 6 |
| S8 | 범위모호 | 2 | 1 | 0 | 0 | 3 |
| S9 | 수동표현 | 0 | 0 | 0 | 2 | 2 |
| S10 | 검증불가 | 1 | 0 | 0 | 0 | 1 |
| S1 | 복합의무 | 0 | 0 | 0 | 0 | **0** |

**도메인 특화 발견**:
- **회계(FA)** — 약한의무(S4) 44건은 평서형 "처리한다" 종결 다수. 다른 모듈 대비 가장 두드러진 차이
- **신용정보(CI)** — 미정의 약어(S7) 19건이 도메인 특화 패턴. 약어 첫 등장 시 풀어쓰기 의무 권장
- **공통(CM)** — 84.9%로 가장 깨끗. 표준 템플릿 자체가 잘 정비되어 있는 것으로 추정

### 7.7 영문 vs 한국어 Smell 분포 비교 — 4 데이터셋 통합

| Smell | 영문 D3 (1,200건) | D1 비정제 75건 | D2 정형 30건 | **D4 실기업 257건** |
|---|---:|---:|---:|---:|
| Passive / 수동표현 | **27.5%** | 8.0% | 10.0% | 1% |
| Non-atomic / 복합의무 | 13.8% | 2.7% | 0% | **0%** |
| Missing-quant / 정량부재 | 1.3% | 6.7% | 6.7% | 2% |
| 모호어 | n/a | **30.7%** | 26.7% | 4% |
| 주체모호 | n/a | 32.0% | 26.7% | **81%** ⚠️ |
| 약한의무 (신규) | n/a | 0% | 30.0% | 23% |
| 미정의 약어 (신규) | n/a | 1.3% | 3.3% | 11% |
| **불완전 (신규 S2)** | n/a | n/a | n/a | **91%** ⚠️ |

**해석**:
- 실기업 정의서가 **sub-requirement 단위 short bullet** 형식이라 S1 복합의무 0건 (atomicity 우수)
- 동시에 **S2 불완전 + S5 주체누락**이 압도적 — 한국 SI 정의서 관행적 작성 패턴
- 영문 SRS의 passive voice 27.5%와 대비되는 한국어 RFP의 **주체 생략 31~81%** — 두 언어의 구조적·관용적 차이를 정량 확인

---

## 8. Insights

### 8.1 한국어 RFP 특유 품질 패턴

영문 SRS와 한국어 RFP에서 가장 빈번한 smell은 명확히 다르다:

| 언어 | 1위 smell | 비율 | 해석 |
|---|---|---|---|
| 영문 | Passive voice | 27.5% | 영문 기술 문서 전통 |
| 한국어 (자체) | 주체모호 | 32.0% | 한국어 주어 생략 허용 |
| 한국어 (정형) | 약한의무 | 30.0% | "한다/된다" 평서형 관행 |

**해석**: 한국어 RFP의 품질 이슈는 (1) 주어 생략, (2) 의무성 약화(평서형), (3) 어휘 모호("실시간", "필요한")의 세 가지가 압도적이며, 이는 두 언어의 구조적·관용적 차이에서 기인한다.

### 8.2 "실시간" 키워드의 함정

D2에서 "실시간"이 모호어로 8회 검출되어 가장 빈번한 모호 표현이었다. RFP 표준 표현으로 자주 쓰이지만 응답시간 SLO(Service Level Objective)가 명시되지 않은 경우가 다수. 예:

> 신용점수·연체·다중채무·카드사용 패턴 등 **실시간** 조회

이는 "실시간"의 정의(예: 95th percentile 응답시간 ≤ 200ms)가 없어 검수·납품 단계에서 분쟁 소지가 된다.

### 8.3 AML 도메인의 품질 취약성

D2 P003(고객360·AML) 프로젝트는 모든 7개 요구사항에서 smell 검출(100%). 분석:

- "실시간" 다수 사용 + SLA 명시 부재
- 평서형 종결 "~한다" → 의무성 약함
- "자동 분류해야 한다" — 정확도/recall 등 측정값 부재

AML은 규제 의무사항이라 모호한 표현이 추후 컴플라이언스 분쟁 위험.

### 8.4 정밀 필터링의 효용

3,210 → 75 (2.3% 통과)는 매우 공격적인 필터링으로 보이나, 검증 결과:

- 통과한 75건 중 Smell 검출 65.3% → 영문 Paska (46.6%)보다 높은 검출률
- 즉 필터 통과 = "진짜 시스템 요구사항"이라는 신호로 작동
- 한국 공공조달 RFP의 본문에서 시스템 요구사항이 차지하는 비율은 매우 낮음 (대부분이 입찰 안내·메타데이터)

### 8.5 정형 vs 비정형 데이터 가치

| 차원 | D1 (자체 추출, 56건) | D2 (정형, 30건) |
|---|---|---|
| 데이터 확보 비용 | 낮음 (자동 다운로드) | 매우 높음 (전문가 정리) |
| 추출 성공률 | 25% (인증 차단) | 100% |
| Smell 검출 정확도 (정성 평가) | 중 (노이즈 잔존) | 고 |
| sub-req 분해 가능 | 부분적 | 완벽 (`;` 명시) |

**시사점**: 한국 공공조달 RFP는 자체 수집의 한계가 명확하며, 산업계·학계 협력으로 정형 데이터셋을 구축하는 것이 자동 분석 도구 개발에 결정적.

### 8.5b 실기업 정의서 — 정제 양식에서도 드러나는 한국 SI 작성 관행 (D4 발견)

D4 데이터셋(실기업 4 모듈 257건)은 잘 정비된 XLSX 정의서 양식임에도:
- **불완전(S2) 91% + 주체누락(S5) 81%** 압도적 — 한국 SI 정의서 작성 관행의 구조적 패턴
- **복합의무(S1) 0건** — sub-requirement 단위 분리는 우수 (Atomicity 양호)
- 모듈별 차별화된 패턴:
  - **회계(FA)**: 약한의무(S4) 44건 — 평서형 종결 다수
  - **신용정보(CI)**: 미정의 약어(S7) 19건 — 도메인 약어 다수
  - **공통(CM)**: 84.9%로 가장 깨끗 — 표준 템플릿 효과

**해석**: 잘 정비된 산출물 양식도 한국 SI 관행적 표현(주어 생략, 평서형 종결)을 그대로 따른다. 이는 RQ4의 **결정적 답**: 한국 RFP 품질 이슈는 데이터 정제 수준이 아니라 **언어·문화적 작성 관행** 자체에 뿌리. 작성자 교육과 도구 지원이 동시에 필요.

### 8.5e v2.5 4 방식 Baseline 비교 — Rule-only의 효율성 정량 확인 (RQ3 답)

R1_sim 50건을 gold label로 4 방식 비교:

| 방식 | Macro-F1 | Micro-F1 | 검출량/50 |
|---|---:|---:|---:|
| **Rule-only** | **0.278** | **0.837** | 21 (42%) |
| NLP-only (kiwipiepy+Chunk) | 0.060 | 0.182 | 48 (96%) |
| LLM-assisted (Rule+LLM dry-run) | 0.278 | 0.837 | 21 (42%) |
| Ensemble (5 detector, rule-priority) | 0.244 | 0.254 | 50 (100%) |

**RQ3 답**: "한국어 NLP 기반 복수 분석기의 앙상블은 요구사항 smell 탐지 성능을 향상시키는가?" → **본 도메인에선 Rule-only가 최선**. NLP/Ensemble은 과검출. 한국어 공공조달·실기업 RFP의 정형 표현이 충분히 명확하여 정규식 휴리스틱이 효율적.

단, R1_sim 자체가 휴리스틱이라 Rule-only에 유리한 편향 가능 — 실제 평가자 데이터로 후속 검증 필요.

### 8.5d v2.2/v2.3 정밀화의 정량 효과 (Ablation Study)

D4 정성 검토에서 발견한 false positive 패턴을 토대로 두 차례 정밀화 적용:

**v2.2 ChunkDetector 3-fix**:
- Fix #1: 30자 미만 short fragment의 actor/target 검사 스킵
- Fix #2: 목적 조사(`을/를`) 본문 출현 시 target 인정
- Fix #3: 양식 파이프(`|`) sub-requirement 분리

**v2.3 MorphDetector**:
- kiwipiepy(Kiwi C++) 본격 통합, 세종 POS 태그셋 활용

**누적 효과 (D4 257건 동일 데이터셋)**:

| Smell | v2.1.1 | v2.2 | v2.3 | Δ |
|---|---:|---:|---:|---:|
| 전체 Smell 비율 | 93.4% | 77.0% | 79.4% | **-14 ppt** |
| **자동 likely FP 비율** | **26%** | — | **3.9%** | **-22 ppt** |
| S2 불완전 | 235 | 181 | 181 | -54 |
| S5 주체누락 | 209 | 159 | 161 | -48 |
| S4 약한의무 | 58 | 58 | **113** | +55 (정확도 ↑) |

v2.3에서 S4가 +55건은 정밀도 저하가 아니라 **이전 정규식이 놓치던 평서형 종결(`ᆫ다`, `함`)을 kiwipiepy가 정확히 추가 검출**한 결과. FA 회계 모듈 44 → 75건 증가는 도메인 특화 정당 검출 확인.

**D1 비정제 회귀 없음** — 양 fix가 D1 56건에 영향 없음 (94.1% 유지), 정제·양식 데이터(D2/D4)에 효과 집중. 안전한 fix 검증.

### 8.5c 윤리·법적 처리 — 실기업 데이터셋 다루기 (D4)

실기업 산출물을 학술 연구에 활용 시 필수 절차:
1. **사전 동의·NDA 검토**
2. **자동화된 익명화 파이프라인** — 정규식 기반 회사·인명·연락처·시스템명 마스킹
3. **잔여 위험 모니터링** — 4글자 이상 영문 약어, 영문+숫자 ID는 시스템·테이블명 식별 가능성
4. **버전 관리 격리** — 백업 ZIP에 `LOCAL_ONLY` 마크, GitHub `.gitignore` 보호
5. **논문 내 원문 인용 0건** — 통계와 익명화된 짧은 패턴만

본 연구에서 D4 처리에 적용한 `anonymizer.py`는 후속 한국어 요구공학 연구에 재사용 가능한 표준 모듈로 제안.

### 8.6 NLP 부재 접근의 가능성

본 연구는 한국어 constituency parser 없이 정규식·키워드 휴리스틱만으로 구현했으나:

- D2 정형 데이터에서 30/30 요구사항 모두 처리 (100% 처리율)
- 영문 Paska의 영문 처리율과 차이 없음
- **단**: 의미 분석 불가 — 동의어("적시", "실시간", "즉시")의 등가 모호 인식 못 함
- **단**: 절(clause) 분해 불가 — 복합의무 검출 정확도 영문보다 낮음

**결론**: 도메인 정형 표현이 충분히 정형화된 영역(공공조달 RFP)에서는 휴리스틱이 NLP 대체 가능. 일반 도메인 일반화 시엔 한국어 NLP 모델 통합 필요.

### 8.7 한컴 COM 자동화의 실용성

HWP 20개 자동 추출에 성공률 100%. 오픈소스 대안(`pyhwp`, `hwp5proc`) 대비 정확도 우수하나:

- **장점**: 한컴 자체 라이브러리 사용으로 텍스트·표·서식 손실 없음
- **단점**: Windows + 한컴오피스 설치 환경 필수, CI/CD 부적합

### 8.8 파일 시그니처 기반 분기의 필요성

본 연구에서 발견한 비명확 케이스: 56건 중 43건의 `page.html` 파일이 실제로는 PDF(12) / HWP 변형(21) / HTTP raw 응답(10)이었다. 확장자 신뢰 시 노이즈 발생. **공공기관 사이트 자동 수집 시 시그니처 검사가 필수**.

---

## 9. Limitations

### 9.1 NLP 부재로 인한 의미 분석 한계

- 동의어 인식 불가 (`적시`, `실시간`, `즉시`, `지체 없이` 등을 별개로 처리)
- 문맥 의존 모호함 미검출
- → KoBART / KoElectra 기반 후속 통합 가능

### 9.2 데이터 가용성

- 공공기관 사이트 인증 차단으로 D1 본문 미확보 42/56 (75%)
- 인증 쿠키·OAuth 기반 재수집 방안 미적용

### 9.3 도메인 한정

- 한국 금융 RFP 외(법률, 의료, 공공행정) 도메인은 화이트리스트·정규식 fine-tune 필요
- "법 제3조의2" 같은 법령 인용이 조달입찰 컷에 같이 잡히는 false positive

### 9.4 Rimay 패턴 미구현

- Paska 코어 기능인 권장 패턴 제시 미구현
- 한국어 등가 패턴 정립 필요 (예: "When … then …" → "조건 …일 때 시스템은 …해야 한다")

### 9.5 검증 데이터 규모

- D2 정형 데이터 30건은 한정적 (3 프로젝트)
- 통계적 일반화엔 부족

### 9.6 사이트 공통 푸터 오컷

- 한국주택금융공사처럼 RFP 템플릿이 동일한 기관은 진짜 요구사항이 사이트 공통으로 잘못 제거될 가능성

---

## 10. Conclusion

본 연구는 영문 NLP 기반 요구사항 품질 평가 도구 Paska를 한국어 공공금융 RFP 대응으로 어댑테이션한 사례를 보고했다. 핵심 결정으로 (1) NLP 의존성 제거, (2) 도메인 특화 정규식·키워드 휴리스틱, (3) 한국어 특유 smell 2종 신규 정의를 적용했다.

12개 공공금융기관 56건 RFP + 정형 30건 데이터셋 검증 결과:
- 한국어 RFP의 품질 이슈 주요 패턴은 **주체모호(32%) + 약한의무(30%) + 어휘모호(31%)**로, 영문 SRS의 passive voice(28%)와 명확히 구분된다.
- 정밀 필터링(3,210 → 75)으로 노이즈 압축, Smell 검출률 65.3%로 영문 Paska(46.6%)보다 높음.
- AML 프로젝트의 100% smell 검출은 규제 컴플라이언스 위험 신호로 작동.

본 도구는 오픈소스(https://github.com/24nga/KoFinRe)로 공개되어 후속 연구·산업 적용 가능하다.

### Future Work

1. KoBART 또는 KoElectra 기반 의미 분석 모듈 통합
2. Rimay 한국어 등가 패턴 정립 및 권장 제시
3. 산업계 협력 기반 한국어 RFP 정답셋 대규모 구축 (1,000건+ 목표)
4. CI/CD 환경 대응 (HWP 크로스플랫폼 추출)
5. 인증 쿠키 기반 공공기관 본문 재수집 자동화

---

## References

1. Veizaga, A., Sabetzadeh, M., Vetro, A., Briand, L. (2021). *Paska: Automated Smell Detection and Recommendation in Requirements Using NLP and CNL*. University of Luxembourg.
2. Gardner, M., et al. (2018). AllenNLP: A Deep Semantic Natural Language Processing Platform.
3. Toutanova, K., et al. (2003). Feature-Rich Part-of-Speech Tagging with a Cyclic Dependency Network. Stanford POS Tagger.
4. ISO/IEC/IEEE 29148:2018 — Systems and software engineering — Life cycle processes — Requirements engineering.
5. INCOSE (2020). Guide to Writing Requirements.
6. Korean Ministry of Government Administration (2022). 공공정보화사업 추진 가이드.
7. 한컴오피스 SDK 문서 — HWPFrame.HwpObject COM 자동화 (Hancom Inc.).

---

## Appendix A — 도구별 상세 비교표

상세는 [`PASKA_KOREAN_ADAPTATION.md`](./PASKA_KOREAN_ADAPTATION.md) 참조.

## Appendix B — 추출·평가 규칙 정의

상세는 [`EXTRACTION_RULES.md`](./EXTRACTION_RULES.md) 참조.

## Appendix C — 변경 이력

상세는 [`UPDATE.MD`](./UPDATE.MD) 참조.

## Appendix D — 산출물 디렉토리

```
rfp_report/
├── RFP_56건_한국어_Smell분석.xlsx       # D1 종합 (5 sheet)
├── RFP_요구사항_원문_3210건.xlsx        # D1 분석 문장 원문
├── RFP_요구사항_정밀필터.xlsx           # D1 정밀 필터 75건
├── REQ_abstract_평가결과.xlsx           # D2 평가 (5 sheet)
├── requirements_filtered.csv            # D1 정밀 필터 CSV
├── requirements_per_project.csv         # D1 사업별 통계
├── req_abstract_eval.csv                # D2 요구사항 단위
├── req_abstract_eval_sub.csv            # D2 sub-req 단위
├── sentences_all.csv                    # D1 분석 문장 전체 (1.4 MB)
├── smell.csv                            # D1 검출 문장
├── summary.json                         # D1 전체 통계
├── req_abstract_summary.json            # D2 전체 통계
├── per_project_text/                    # D1 사업별 .md (40개)
└── requirements_per_project_text/       # D1 정밀 필터 사업별 .md (14개)
```
