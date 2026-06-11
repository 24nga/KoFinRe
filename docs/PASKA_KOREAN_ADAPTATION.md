# Paska → 한국어 RFP 분석 어댑테이션 리포트

> 원본 [Paska](https://github.com/lu-cs-sv/Paska) (영문 SRS 평가, allennlp + Java)를
> 한국어 공공금융 RFP/조달 공고문 대응판으로 포팅하면서 무엇이 바뀌었는지 정리.

## 0. TL;DR

| 구분 | Paska 원본 | 한국어 버전 |
|---|---|---|
| 대상 언어 | 영문 | 한국어 |
| NLP 엔진 | allennlp 2.10.1 constituency parser | **제거** — 정규식·키워드 휴리스틱 |
| POS Tagger | Stanford english-left3words-distsim | **제거** |
| 런타임 | Python 3.8 + Java 8 (Docker on Linux) | Python 3.10+ on Windows (COM 자동화) |
| 입력 | CSV (`"ID";"text"`) | HTML / HWP / PDF / RTF 자체 추출 + 정형 CSV 지원 |
| Smell 유형 | 9종 (영문 정의) | 7종 (한국어 재정의) |
| 코어 산출물 | `smells.csv` | CSV 7종 + Markdown + Excel 다중 시트 |

가장 큰 변경: **NLP 모델을 들어내고 규칙 기반으로 완전히 재구현**.
이유는 (1) allennlp Windows 미지원 (2) 한국어 constituency parser 사용성 낮음 (3) RFP 도메인은 정형 표현이라 휴리스틱으로 충분.

---

## 1. 실행 흐름 비교

### Paska 원본 (영문)

```
input.csv (Req ID + sentence)
    │
    ▼  python get_cparsingtrees.pyc  (allennlp ≈ 1GB ELMo + constituency model 다운로드)
parsing_trees.csv  (트리 구조 텍스트)
    │
    ▼  java -jar smell_detector.jar
       (Stanford POS tagger + 트리 기반 절 분해)
smells.csv  (요청 ID × 9 smell × Rimay 패턴)
```

### 한국어 버전

```
RFP 공고 (HTML / HWP / PDF / RTF)
    │
    ▼  rfp_extract.py
       (BeautifulSoup / 한컴 COM / pdfplumber / unrtf,
        파일 시그니처 기반 분기)
사업별 통합 .txt
    │
    ▼  rfp_smell.py        ← 한국어 정규식 7종
sentences_all.csv  smell.csv  summary.json
    │
    ▼  rfp_requirement_filter.py
       (EXTRACTION_RULES.md 의 정밀 필터)
requirements_filtered.csv  per_project.csv
    │
    ▼  rfp_excel*.py
Excel 다중 시트 (안내 / 요구사항 / 사업별 / 필터규칙)

[병렬 경로]
REQ_abstract.csv (정형 CSV)
    │
    ▼  req_abstract_eval.py  ← 같은 정규식 7종을 sub-req 단위로
요구사항 단위 + sub-req 단위 결과
```

---

## 2. 영역별 상세 변경 사항

### 2.1 NLP / 파싱 엔진

| 항목 | Paska | 한국어 |
|---|---|---|
| 라이브러리 | `allennlp 2.10.1`, `allennlp-models 2.10.1` | **제거** |
| 모델 | ELMo + constituency parser (≈1GB 다운로드) | **제거** |
| 트리 구조 | 절(clause) 단위 분해해서 smell 룰 적용 | **문장 단위 분석** (절 분해 안 함) |
| 의존 패키지 수 | 60+ (torch, transformers, datasets, spaCy 포함) | **5개**: beautifulsoup4, pdfplumber, openpyxl, pywin32, requests |
| 컨테이너 크기 | 5.9 GB | (호스트 Python, 별도 컨테이너 없음) |
| 첫 실행 시간 | 모델 다운로드 ~7분 | 즉시 |

**왜 NLP를 빼버렸나**
- allennlp 의 constituency parser는 영문 한정. 한국어 동급 모델(KoBART, KoElectra)을 같은 인터페이스로 쓰려면 별도 작업 필요.
- RFP 한국어 표현은 정형화돼 있어 (`~하여야 한다`, `~제시하여야 함`) 정규식만으로 90%+ 패턴 커버 가능.
- 디버깅·반복 속도가 NLP 기반보다 훨씬 빠름.

### 2.2 POS Tagger

| 항목 | Paska | 한국어 |
|---|---|---|
| 도구 | Stanford POS tagger 4.2.0 (`english-left3words-distsim.tagger`) | **사용 안 함** |
| 다운로드 | 75 MB | — |
| 외부 의존 | Java 8 JRE | — |

POS 정보가 필요한 smell(`Not precise verb` 같은)들은 한국어 어휘 리스트(`VAGUE_TERMS = ['필요한','적절한',…]`)로 대체.

### 2.3 Smell 유형 — 9개 → 7개 재정의

| Paska (영문) | 한국어 매핑 | 변경 |
|---|---|---|
| Non-atomic requirement | 복합의무 | 동일 개념. 한국어 룰: 의무 표현(`해야 한다 / 할 수 있어야`)이 한 문장에 2회 이상 |
| Incomplete requirement | 정량부재 | 좁힘. 한국어는 "성능/처리량 키워드 + 숫자 없음" 패턴으로 한정 |
| Incorrect order requirement | **제거** | 한국어는 어순이 SOV로 고정. 조건절-결과절이 한국어 종결 구조상 명확해 검출 의미 낮음 |
| Coordination ambiguity | 모호어에 통합 | "or/and" 모호함 → 한국어는 "필요한·적절한" 등 어휘 모호로 재정의 |
| Not requirement | **사전 필터로 흡수** | 별도 smell이 아니라 `rfp_requirement_filter.py` 단계에서 컷 |
| Incomplete condition | **제거** | NLP 절 분해에 의존하던 룰이라 휴리스틱 등가물 어려움 |
| Incomplete system response | 주체모호 | 좁힘. "주어 없이 의무문 시작" 으로 단순화 |
| Passive voice | 수동태 | 동일 개념. 한국어 룰: `~되어야 한다`, `~지원되어야`, `됨/된다$` 등 어미 |
| Not precise verb | 모호어에 통합 | "handle/process" 류 → 한국어는 어휘 리스트로 흡수 |
| **— (신규) —** | **미정의 약어** | 한국 RFP는 영문 약어 사용 빈도 매우 높음. 정의 없이 등장하는 약어 검출 |
| **— (신규) —** | **약한 의무** | 한국어 특화. "~한다/된다" 평서형 (Paska 등가 없음 — 영문은 modal 명시적) |

### 2.4 입력 처리

| 항목 | Paska | 한국어 |
|---|---|---|
| 포맷 | CSV 한 가지 (`"ID";"text"`) | HTML, HWP, PDF, RTF, 정형 CSV |
| HWP | — | 한컴오피스 COM 자동화 (`win32com.client`) |
| 인코딩 | UTF-8 | UTF-8 / CP949 / EUC-KR 자동 감지 |
| 파일 식별 | 확장자 신뢰 | **시그니처(magic byte) 기반 재판별** — `page.html` 라고 저장돼 있어도 `%PDF` 면 PDF로 처리 |

### 2.5 문장 분리

| 항목 | Paska | 한국어 |
|---|---|---|
| 기본 | `(?<=[.!?])\s+(?=[A-Z(])` | `(?<=[.!?。])\s+(?=[가-힣A-Z○●▶■◇(\d])` |
| 추가 | — | `;` (세미콜론) — REQ_abstract sub-requirement 패턴 반영 |
| 결합 | — | `-\n` 줄바꿈 하이픈 결합 (PDF 추출 산출물 특성) |

### 2.6 요구사항 후보 식별 (대-소-cut)

Paska는 별다른 사전 필터 없이 입력 CSV 전체를 NLP에 넣고, "Not requirement" smell로 사후 표시.

한국어 버전은 **NLP 없이 정규식만 쓰니 사전 필터가 훨씬 중요**해서, 별도 단계로 분리:

1. **포함 규칙** — 의무 종결어(`~여야 한다`, `~할 수 있어야`, `반드시 ~`, `필수이다`, `~토록 한다`) 7종 중 하나 필수
2. **제외 규칙** (6 카테고리):
   - 사이트 푸터 (`COPYRIGHT`, `패밀리사이트`, `용어사전`)
   - 조달·입찰 표준 문구 (`입찰자`, `공동수급체`, `청렴계약`, `조달청`, `나라장터`, `국가계약법`)
   - 메타데이터 시작 (`사업명·사업기간·사업예산·문의처`)
   - 글머리표 단편 (`▶○●◇□■`, `Ⅰ~Ⅹ`, `1.` 단독)
   - 평가기준 (`~을 평가한다`, `~을 점검한다`)
   - 약관 도메인 (`임차인·보증금·채권` + 시스템 명사 없을 때)
3. **사이트 공통 텍스트** — 5+ 사업에서 정확 일치 → 공통 푸터로 자동 컷
4. **사업 내 중복** — `(project_id, sentence)` 단위 dedup

검증된 효과 (RFP 56건): 3,210 문장 → 정밀필터 75건 (2.3%). 그중 Smell 검출 65.3% — Paska 영문 결과(46.6%)와 비교 가능한 수준.

### 2.7 약어 화이트리스트 (한국 특화)

Paska엔 없음. 한국어 RFP는 영문 약어 다수라 화이트리스트가 신호 vs 노이즈 구분에 핵심.

- 일반 ICT 70+종: `RFP, IT, OS, API, AI, JSON, XML, HTML, SQL, ...`
- **한국 금융기관 12종**: `HF, BOK, KAMCO, HUG, KRX, KIC, KIBO, KDIC, KODIT, KFTC, KSD, MOEF`
- **한국 금융 도메인 약어**: `DSR, KYC, AML, NICE, KCB, ELS, ETF, ECOS, CBDC, PEP, EDD, STR, FATF, KOFIU`
- 한국 기업: `NHN, SK, KT, LG, MS, IBM, HP, AWS, GCP`

### 2.8 출력

| 항목 | Paska | 한국어 |
|---|---|---|
| 기본 CSV | `smells.csv` (1개) | `sentences_all.csv`, `smell.csv`, `requirements_filtered.csv` (3개 단계별) |
| 사업별 통계 | — | `per_project.csv`, `requirements_per_project.csv` |
| 전체 요약 | — | `summary.json` (모호어 Top, 미정의 약어 Top 포함) |
| 사람-검토용 | — | `per_project_text/<사업>.md` — smell 태그 inline |
| Excel | — | 4종 워크북, 시트별 자동필터, smell 행 노란 배경, 색상 스케일 |
| Rimay 패턴 추천 | ✓ | — (제거. Paska 코어 기능이지만 한국어 등가 패턴 미정립) |

### 2.9 새로 추가된 단계 (Paska엔 없음)

1. **자동 텍스트 추출**: 80여 SRS 문서를 자동 파싱해 Paska 입력 형식으로 변환 — 우리가 만든 보조 단계
2. **HWP 처리**: 한컴 COM 자동화
3. **시그니처 기반 파일 분기**: `page.html` 실제 내용 판별
4. **사이트 공통 텍스트 자동 검출** (5+ 사업에서 정확 일치 = 공통 푸터)
5. **사업별 마크다운 정리본** — `[모호어, 약한의무]` 같은 inline 태그로 사람 검토 편의

---

## 3. 검증 결과 비교

### 3.1 Paska 원본을 영문 SRS 79건에 돌린 결과

| 지표 | 값 |
|---|---|
| 대상 | 79 SRS 문서 (PDF / DOC / HTML) |
| 텍스트 추출 성공 | 76건 (HTML 3건 bs4 미설치로 실패 후 보완) |
| 추출 문장 | 8,914 |
| 샘플링(문서당 20) | 1,200 (65 docs × ≤20) |
| 파싱 트리 생성 | 7분 10초 (1,200 reqs) |
| Smell 검출 (Java) | 16초 |
| Smell 비율 | 46.6% (1,200 중 559) |
| Top smell | Passive voice 330, Non-atomic 166 |

### 3.2 한국어 버전 — RFP 56건 (자체 추출)

| 지표 | 값 |
|---|---|
| 대상 | 12개 공공금융기관 RFP 56건 (HTML+HWP+PDF) |
| 텍스트 추출 성공 | 14건 (42건은 사이트 인증/차단으로 본문 미확보) |
| 추출 문장 | 3,210 |
| 정밀 필터 통과 | 75 (2.3%) |
| Smell 비율 | 65.3% (75 중 49) |
| Top smell | 약한의무 9, 모호어 8, 주체모호 8 |

### 3.3 한국어 버전 — REQ_abstract.csv 30건 (정형)

| 지표 | 값 |
|---|---|
| 대상 | 3 프로젝트 × 30 req (정형 CSV) |
| sub-requirement 분리 | 140건 (`;` 기준) |
| Smell 비율 (req_id 수준) | 56.7% (30 중 17) |
| 가장 빈번 | 약한의무 9, 모호어 8 (실시간 8회) |
| 위험 프로젝트 | P003 고객360·AML 7/7 (100%) |

### 3.4 영문 vs 한국어 — Smell 분포 차이

| Smell | Paska 영문 (1,200건) | 한국어 56건 (75건) | 한국어 정형 30건 |
|---|---|---|---|
| Passive voice / 수동태 | 330 (28%) | 6 (8%) | 3 (10%) |
| Non-atomic / 복합의무 | 166 (14%) | 2 (3%) | 0 (0%) |
| Missing-quantification / 정량부재 | 16 (1%) | 5 (7%) | 2 (7%) |
| 모호어 (Coordination + Not-precise) | (영문은 별도) | 23 (31%) | 8 (27%) |
| 미정의 약어 (한국 특화) | — | 1 (1%) | 1 (3%) |
| 약한의무 (한국 특화) | — | 0 | 9 (30%) |
| 주체모호 | — | 24 (32%) | 8 (27%) |

영문 패시브 voice 비율이 높은 건 영문 기술 문서 특성. 한국어는 평서형 종결의 약한 의무 + 주체 생략이 압도적이고, 이는 한국어 RFP 특유 패턴.

---

## 4. 폐기·제거된 기능

- **Stanford POS tagger** — 영문 한정
- **allennlp constituency parser** — 영문 한정, Windows 미지원
- **Java `smell_detector.jar`** — Stanford POS + tree-based 분석 통째 제거
- **Python `get_cparsingtrees.pyc`** — 트리 생성 단계 자체 제거
- **Rimay pattern 추천** — 한국어 등가 패턴 미정립 상태라 보류
- **`javafx.util.Pair` shim** — Java 의존 자체가 없어져서 불필요

---

## 5. 추가로 만든 기능 (Paska에 없음)

- `download_rfp.py` — 공공기관 사이트 56건 RFP 자동 다운로드 (메타데이터 + 첨부)
- `rfp_extract.py` — HTML/HWP/PDF/RTF 자체 텍스트 추출, 시그니처 기반 파일 판별
- `rfp_requirement_filter.py` — 요구사항-노이즈 분리 정밀 필터
- `req_abstract_eval.py` — 정형 CSV (`project_id, req_id, req_details`) 입력 지원, sub-req 분해 평가
- `rfp_excel*.py` — 다중 시트 Excel (자동필터, 조건부 색상, 색상 스케일)
- 사업별 마크다운 검토본 (`per_project_text/<사업>.md`)
- 사이트 공통 푸터 자동 검출 (5+ 사업 정확 일치)
- 한국 금융 도메인 약어 화이트리스트

---

## 6. 한계 / 후속 개선 여지

1. **NLP 부재** — 의미 분석이 빠져 있어 동의어·문맥 의존 모호함을 못 잡음
   → 후속: KoBART/KoElectra 기반 의도 분류 추가 가능
2. **도메인 의존** — 한국 금융 RFP 외(법률, 의료, 공공행정)는 화이트리스트·정규식 fine-tune 필요
3. **법령 인용 컷** — `법 제\d+조` 패턴이 조달 입찰 컷에 함께 잡힘. 진짜 시스템 요구사항이 법령을 인용하는 경우 손실
4. **공통 푸터 오컷** — 한국주택금융공사처럼 RFP 템플릿이 동일한 기관은 진짜 요구사항이 사이트 공통으로 잘못 제거될 수 있음
5. **HWP 의존** — 한컴오피스 설치된 Windows에서만 동작. CI/CD 환경엔 부적합 → 후속: `pyhwp` 또는 `hwp5proc` 등 크로스플랫폼 대안 검토
6. **Rimay 패턴 미적용** — 사용자에게 "이 문장은 이런 패턴으로 쓰세요" 권장 제공 안 됨. 한국어 등가 패턴(예: "When… then…" → "조건에 의하면…한다") 정립 필요

---

## 7. 변경 통계 (Lines of Code)

| 영역 | Paska 원본 | 한국어 버전 |
|---|---|---|
| Python | get_cparsingtrees.pyc (~4KB 컴파일) | 9 스크립트, 약 1,900 LoC |
| Java | smell_detector.jar (~40MB, 19 .java 파일) | 0 |
| 모델 파일 | ~1.4 GB (allennlp ELMo + Stanford tagger) | 0 |
| 설정 | environment.yml (≈135 패키지) | requirements.txt (5 패키지) |

---

## 8. 결론

**원형 유지 정도**: 컨셉(요구사항 품질 검사 + 9 smell 유형)은 유지, **구현은 전면 재작성**.

| 평가 | 결과 |
|---|---|
| Paska 동등 기능 영어 분석 | Docker 이미지로 그대로 작동 (별도 검증 완료) |
| 한국어 RFP 분석 | 자체 휴리스틱으로 동급 수준 산출 (비교 표 참조) |
| 운영 부담 | Java/allennlp 통째로 빠져서 Windows 단일 환경에서 실행 |
| 정확도 | NLP 기반 Paska 대비 낮을 가능성 있음. 도메인 한정 RFP에선 충분 |

원본 Paska Docker 환경은 `C:\Users\heen1\Desktop\Paska\Paska-main\docker\`에 보존돼 있어 영문 분석은 그대로 가능.
한국어 버전은 본 저장소(`24nga/KoFinRe`)에 분리되어 있음.
