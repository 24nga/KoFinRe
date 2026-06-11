# UPDATE.MD

> 한국어 RFP 요구사항 추출·평가 도구의 변경 이력.
> 추출/평가 규칙이 바뀔 때마다 이 파일을 갱신.

규칙 본문은 [`EXTRACTION_RULES.md`](./EXTRACTION_RULES.md) 참조.

---

## [Unreleased]

(다음 릴리스에 들어갈 항목을 여기에 누적)

---

## [1.0.2] — 2026-06-10

### Added

- **`PAPER_DRAFT.md`** — 논문 작성용 학술 정리본
  - Abstract, Introduction, Related Work, Problem Analysis 섹션
  - Methodology (5단계 파이프라인 상세)
  - Implementation, Experimental Setup (D1·D2·D3 데이터셋 정의)
  - Results — 영문 Paska vs 한국어 자체/정형 데이터 정량 비교
  - Insights 8개 (한국어 RFP 특유 패턴, "실시간" 함정, AML 도메인 취약성 등)
  - Limitations, Conclusion, Future Work, References, Appendix A~D

## [1.0.1] — 2026-06-10

### Added

- **`PASKA_KOREAN_ADAPTATION.md`** — 원본 Paska(영문 SRS 평가, allennlp+Java)와 본 한국어 버전 차이의 상세 보고서
  - 영역별 변경: NLP 엔진(allennlp → 정규식), POS Tagger(Stanford → 제거), Smell 9종 → 7종 매핑
  - 실행 흐름·입력 처리·출력 산출물 비교표
  - 검증 결과 (Paska 영문 1,200건 vs 한국어 56건/30건)
  - 폐기·신규 기능, 한계·후속 개선 여지

---

## [1.0.0] — 2026-06-10

### 데이터 소스

- **참고 정답셋**: `RFP요구사항 - REQ_abstract.csv` (3 프로젝트 30건, sub-req 140건) — 잘 작성된 RFP의 정답 패턴
- **분석 대상**: 12개 공공금융기관 56건 RFP 공고 (HTML 페이지 + HWP/PDF 첨부)

### 추가 (Added)

- **추출 규칙 v1.0** (`EXTRACTION_RULES.md`)
  - 문장 분리: 마침표·물음표·느낌표 + 세미콜론(`;`) — REQ_abstract sub-req 패턴 반영
  - 길이/한글 비율 1차 필터
  - 포함 규칙: 요구사항 종결어 7종 + 시스템 명사
  - 제외 규칙: 사이트 푸터·조달 입찰·메타데이터·글머리표·평가기준·약관 6 카테고리
  - 중복 제거: 사이트 공통 + 사업 내 중복
- **Smell 검사 7종**
  - 모호어, 수동태, 복합의무, 정량부재, 미정의약어, 주체모호, 약한의무
- **스크립트**
  - `rfp_extract.py` — HTML(BeautifulSoup) / HWP(한컴오피스 COM) / PDF(pdfplumber) 추출
  - `rfp_smell.py` — Smell 7종 검사
  - `rfp_requirement_filter.py` — 정밀 필터링
  - `rfp_excel*.py` — Excel 리포트 생성
  - `req_abstract_eval.py` — REQ_abstract.csv 정형 CSV 평가
  - `download_rfp.py` — 56건 RFP 자동 다운로드 (이전 단계 산출)

### 한국어 약어 화이트리스트

- 일반 ICT: RFP, IT, API, AI, JSON, XML, HTML, SQL, ...
- 금융기관: HF, BOK, KAMCO, HUG, KRX, KIC, KIBO, KDIC, KODIT, KFTC, KSD
- 금융 도메인: DSR, KYC, AML, NICE, KCB, ELS, ETF, ECOS, CBDC, PEP, EDD, STR, FATF, KOFIU

### 검증 결과

| 데이터셋 | 입력 | 추출 | Smell |
|---|---|---|---|
| RFP 56건 자체 추출 | 3,210 문장 | 75 (2.3%) | 49 (65.3%) |
| REQ_abstract 30건 | 30 req / 140 sub | 30 (100%) | 17 req (56.7%) |

### 알려진 한계

- 첨부 다운로드 차단 사업(56건 중 ~42건)은 본문 추출 자체 불가
- 양식 표(여러 셀이 합쳐 한 문장처럼 들어옴) 분리 어려움
- 법령 인용("제3조의2")이 조달 입찰 컷에 같이 걸림 — 추후 개선 필요
- 사업 공통 템플릿 문장이 사이트 공통으로 잘못 제거될 가능성

---

## 변경 항목 분류 (Keep a Changelog 스타일)

새 항목을 추가할 때 아래 카테고리 사용:

- `### Added` — 새로 추가된 규칙/스크립트/패턴
- `### Changed` — 기존 규칙 수정
- `### Deprecated` — 사용하지 않는 규칙 (다음 릴리스에서 제거 예정)
- `### Removed` — 제거된 규칙/기능
- `### Fixed` — 잘못된 매칭/오류 수정
- `### Security` — 토큰·키 노출 등 보안 수정

## 릴리스 헤더 양식

```markdown
## [버전] — YYYY-MM-DD

### Added
- 한 줄 요약 — 자세한 설명/규칙 변경 위치
- ...

### Changed
- ...
```

## 규칙 변경 시 체크리스트

1. `EXTRACTION_RULES.md` 본문 수정
2. 해당 정규식/패턴 수정한 코드 파일 함께 변경
3. UPDATE.MD에 변경 카테고리·이유·영향 받는 데이터 기록
4. 기존 결과와의 diff(통과·컷 변경) 1~2건 예시 첨부 권장
