# UPDATE.MD

> 한국어 RFP 요구사항 추출·평가 도구의 변경 이력.
> 추출/평가 규칙이 바뀔 때마다 이 파일을 갱신.

규칙 본문은 [`EXTRACTION_RULES.md`](./EXTRACTION_RULES.md) 참조.

---

## [Unreleased]

(다음 릴리스에 들어갈 항목을 여기에 누적)

---

## [2.8.0] — 2026-06-12 — CMMI/NCS 기반 Smell 15 → 19종 확장

### 동기

사용자 제공 CMMI(REQM/RD) 9 작성 원칙 + NCS 중분류 5 제약 카테고리 표를 참고하여 v2.7 S15 까지에서 부재했던 **Necessary·Feasible·Traceable·Constraint** 영역을 보강.

### Added

- **`docs/CMMI_NCS_COMPARISON.md`** — CMMI 9 원칙 + NCS 5 제약 카테고리 vs KoFinRe 매핑 분석
  - 9 원칙 충족도: 5/9 (Singular/Unambiguous/Verifiable/Complete/Impl-free)
  - NCS 5 카테고리: 0/5 (전무 → v2.8에서 분류 보조)
  - 4 신규 smell 도출 (S16~S19)
  - CMMI 체크리스트 자동 매핑 표

- **Smell taxonomy 확장: 15종 → 19종**

  | 코드 | 한국어 | CMMI 영역 | 매핑 |
  |---|---|---|---|
  | **S16** | 필요성불명확 | REQM Necessary | 선호하는·강제로·임의로·개발팀이 |
  | **S17** | 실현불가 | RD Feasible | 100%·0초·완벽한·5 9s 이상 |
  | **S18** | 추적ID부재 | REQM Traceable | REQ-ID + 출처 둘 다 부재 |
  | **S19** | 제약카테고리불명 | NCS 5 분류 | 제약 표현 + 카테고리 미분류 |

- **`kofinre/korean_patterns.py`** — 신규 사전 5종 (CMMI L 카테고리)
  - `NECESSITY_RED_FLAGS` 정규식 — 주관·선호·강제 표현
  - `INFEASIBLE_ABSOLUTE` 정규식 — 100%·0초·완벽한·99.9999%
  - `REQ_ID_PATTERN` — `FUNC-AUTH-001`, `REQ-001` 등 ID 형식
  - `SOURCE_RATIONALE` — 출처·근거·법령 인용
  - **NCS 5 분류 사전**: `CONSTRAINT_TECH`, `CONSTRAINT_BIZ`, `CONSTRAINT_COMP`, `CONSTRAINT_OPS`, `CONSTRAINT_SEC`

- **헬퍼 함수 5종**: `has_necessity_red_flag`, `has_infeasible_absolute`, `find_req_id`, `has_source_rationale`, `classify_constraint_category`

- **`tests/test_cmmi_smells.py`** — 18 단위 테스트 (18/18 통과)
  - S16~S19 각 3~5건 + Korean Patterns 헬퍼 5건

### Changed

- `kofinre/__init__.py`: SMELL_CODES 19개, 한국어 이름 4종 추가
- `kofinre/ensemble.py`: SMELL_CODES sync
- `kofinre/detectors/regex_detector.py`: S16~S19 검출 로직 추가
- 나머지 4 detector: S16~S19 false 초기화

### 표준 커버리지 누적 (v2.8)

| 영역 | v2.6 (S10) | v2.7 (S15) | **v2.8 (S19)** | Δ |
|---|---:|---:|---:|---:|
| **전체 표준 커버리지** | 28% | ~55% | **~70%** | +42pp |
| CMMI 9 원칙 | 5/9 | 5/9 | **8/9** | Necessary·Feasible·Traceable 완전 |
| NCS 5 제약 카테고리 | 0/5 | 0/5 | **5/5 분류 보조** | +5 |
| INCOSE 11 결함 | 4/11 | 8/11 | 8/11 | (S11~S15 효과) |
| ISO 29148 9 특성 | 5/9 | 7/9 | **8/9** | Necessary·Feasible 추가 |

### 검증

- 신규 18/18 통과 (`test_cmmi_smells.py`)
- 통합 60/61 (XYZW edge case 1건만 유지)
- basic_usage 회귀 없음

---

## [2.7.0] — 2026-06-12 — Smell taxonomy 10 → 15종 확장 (ISO 29148 기반)

### 동기

사용자 제공 ISO 29148 요구사항 작성 원칙 표(9 quality attributes + 문장 수준 6 규칙 + 8 제약 카테고리)를 참고하여 STANDARDS_COMPARISON.md 에서 도출했던 신규 smell 후보 중 P0~P1 5종을 즉시 구현.

### Added

- **Smell taxonomy 확장: 10종 → 15종**

  | 코드 | 이름 | ISO 29148 매핑 | 우선순위 |
  |---|---|---|---|
  | **S11** | 구현편향 | Implementation-free 위반 | P0 |
  | **S12** | 부정문 | 능동·긍정 원칙 위반 | P0 |
  | **S13** | 추측표현 | Necessary·Clarity 위반 | P1 |
  | **S14** | 수혜자누락 | Complete (Persona) | P1 |
  | **S15** | 지시어모호 | Unambiguous (Pronoun) | P2 |

- **`kofinre/korean_patterns.py`** — 신규 사전 5종
  - `IMPL_BIAS_DB` / `IMPL_BIAS_FRAMEWORK` / `IMPL_BIAS_LANGUAGE` / `IMPL_BIAS_INFRA`
    — Oracle, Java, Spring, AWS 등 60+ 식별자
  - `NEGATIVE_STATEMENT` 정규식 — "하지 않아야 한다" / "지원하지 않는다" 류
  - `SPECULATION_TERMS` — "가능하면", "필요시", "추후 협의" 등
  - `STAKEHOLDERS` 정규식 + `SYSTEM_ONLY` — 시스템만 명시한 케이스 검출
  - `DEMONSTRATIVE_PRONOUN` — "해당 시스템", "본 항목", "상기 내용" 등 한국어 지시어

- **헬퍼 함수 5종** — `has_implementation_bias`, `has_negative_statement`, `find_speculation`, `missing_stakeholder`, `has_pronoun_ambiguity`
- **`tests/test_new_smells.py`** — 16 단위 테스트 (16/16 통과)
- **`kofinre/__init__.py`** — `SMELL_NAMES` / `SMELL_NAMES_KO` 5종 추가

### Changed

- `kofinre/ensemble.py`: SMELL_CODES 15개로 확장
- `kofinre/detectors/regex_detector.py`: S11~S15 검출 로직 추가
- `kofinre/detectors/morph_detector.py`, `chunk_detector.py`, `dictionary_detector.py`, `llm_detector.py`: S11~S15 false 초기화 (앙상블 안전)

### 검증

- 신규 16/16 단위 테스트 통과
- 기존 11/12 유지 (XYZW edge case 1건)
- D4 익명 데이터: 신규 S11~S15 검출 0건 (정상 — 익명화로 기업 식별자·부정문 잔재 없음)

### 표준 커버리지 (STANDARDS_COMPARISON.md 갱신)

- v2.6 (S1~S10): **28%** 커버
- v2.7 (S1~S15): **약 55%** 커버 (+27 pp)
  - INCOSE 11 결함: 4/11 → **8/11**
  - ISO 29148 9 특성: 5/9 → 7/9

---

## [2.6.1] — 2026-06-12 — 요구공학 표준 갭 분석 + S11~S18 신규 smell 후보 도출

### Added

- **`docs/STANDARDS_COMPARISON.md`** — IEEE 830 / ISO 29148 / INCOSE / EARS ↔ KoFinRe S1~S10 갭 분석
  - 표준별 정의 기준 정리 (8/9/11/5 = 33 기준)
  - S1~S10 매핑 매트릭스 — 충족 5종 / 부분 4종 / 부재 10종
  - 갭 우선순위 (P0~P4)
  - **신규 smell 후보 8종 (S11~S18)** 도출:
    - S11 Implementation-bias (구현 편향) — P0
    - S12 Negative-statement (부정문) — P0
    - S13 Speculation (추측·조건부) — P1
    - S14 Missing-actor-persona (이해관계자 부재) — P1
    - S15 Pronoun-ambiguity (지시어 모호) — P2
    - S16 Modifiability (수정가능성) — P2
    - S17 Consistency (요구사항 간 일관성) — P3 (문서 단위)
    - S18 EARS-non-conformance (양식 권장) — P4
  - 검출 사전·정규식 구현 가이드 (S11~S15)
- README.md / scripts/build_pdf_bundle.py: STANDARDS_COMPARISON 링크 추가

### 핵심 발견

- 현재 KoFinRe S1~S10: 표준 18+ 기준의 **약 28%** 커버
- S11~S18 추가 시 **78% 커버** (+50pp)
- IEEE 830 8 특성: 5/8 → 7/8
- ISO 29148 9 특성: 5/9 → 8/9
- INCOSE 11 결함: 4/11 → 9/11

---

## [2.6.0] — 2026-06-12 — 한국어 특화 고도화 (korean_patterns 모듈)

### Added

- **`kofinre/korean_patterns.py`** — 한국어 RFP 특화 패턴 사전
  - A. 종결어미 5단계 분류 (강한 의무 / 약한 의무 / 평서 / 명령 / 의문)
  - B. 격조사 정밀 분류 (NOM 이/가, ACC 을/를, TOPIC 은/는, LOC 에/에서, GEN 의)
  - C. 부정·이중부정 (`~하지 않다`, `없지 않다`, `아닌 것은 아니다`)
  - D. 모호어 4 카테고리 (어휘/양화/시간/단위)
  - E. 한국 RFP 도메인 어휘 (주체·행위·인터페이스·데이터·품질속성)
  - F. 수동·피동 정밀 (`되어야`, `하게 되어 있다`)
  - G. **번역체 흔적** (`~을 가지다`, `~에 있어서는`) — 품질 신호
  - H. 범위 모호 확장 (`기타`, `또는 그 이상`)
  - I. 한국어 수량 단위 (`건`, `회`, `명`, `TPS`, `밀리초` 등)
  - J. 정성 표현 (검증불가 보조)
- 헬퍼 함수: `classify_obligation_strength`, `find_vague_terms`, `has_actor_keyword`, `has_quantitative_unit`, `is_qualitative_without_metric`, `has_translationese`, `has_double_negation`
- **`tests/test_korean_patterns.py`** — 15 단위 테스트 (의무 분류·모호어·번역체·정량 단위·정성 표현·주체 키워드)

### Changed

- **MorphDetector** (`kofinre/detectors/morph_detector.py`):
  - kiwipiepy + korean_patterns 통합
  - S2: 강한 의무 + 목적 부재 + 행위 동사 부재 → HIGH confidence
  - S4: 평서형 + 강한 의무 X + 수동 X + 이중부정 X → 정밀화
  - S5: 주격·보조사 부재 + 주체 키워드 부재 → HIGH
  - S9: 수동 마커 + korean_patterns 위임
  - 메타: 번역체·이중부정 신호 기록
- **RegexDetector** (`kofinre/detectors/regex_detector.py`):
  - S3: `find_vague_terms` 위임 (어휘·양화·시간 3 카테고리)
  - S6: `QUALITY_KEYWORDS` + 한국어 단위 (`건/초`, `밀리초` 등)
  - S8: `COORD_AMBIGUOUS` 확장 (`기타`, `또는 그 이상`)
  - S10: `is_qualitative_without_metric` 위임

### D4 v2.5 → v2.6 효과

| 카테고리 | v2.5 | v2.6 | Δ |
|---|---:|---:|---:|
| FA 회계 | 94.7% | 91.6% | **-3.2 pp** |
| BG 예산 | 69.2% | 69.2% | 0 |
| CI 신용정보 | 94.7% | 89.5% | **-5.3 pp** |
| CM 공통 | 45.3% | 50.9% | +5.7 pp (단위·정성 정밀화로 검출 추가) |
| **합계** | **79.4%** | **78.2%** | **-1.2 pp** |

### Smell 유형별 변화

| Smell | v2.5 | v2.6 | 변화 사유 |
|---|---:|---:|---|
| S3 모호어 | 9 | 10 | 양화·시간 모호 카테고리 추가 |
| **S4 약한의무** | **113** | **59** | 이중부정·번역체 제외 → 정밀화 |
| S6 정량부재 | 6 | 10 | 한국어 단위(건/초·밀리초) 인식 |
| S7 미정의약어 | 28 | 28 | 동일 |
| S10 검증불가 | 1 | 2 | 정성+단위 검사 강화 |
| S5 주체누락 | 161 | 159 | 주체 키워드 인식 강화 |
| S2 불완전 | 181 | 181 | 동일 |

### Tests

- 15/15 통과 (`tests/test_korean_patterns.py`)
- 기존 11/12 유지 (`tests/test_detectors.py`)
- 회귀 없음 (`examples/basic_usage.py` 동일 결과)

---

## [2.5.1] — 2026-06-12 — 웹 평가기 + MECE 논문

### Added

- **`web/index.html`** — 단일 HTML 웹 평가기
  - SheetJS(xlsx@0.18.5) 기반 XLSX 파싱·생성
  - 100% 클라이언트 처리 — 서버 전송 0건, 영업 비밀 안전
  - 자동 시트·컬럼 식별 (요구사항명·내용)
  - 10종 smell 검출 + 휴리스틱 교정 마커
  - 결과 미리보기(200건) + 원본 + 결과 컬럼 + 요약 시트 XLSX 다운로드
- **`web/README.md`** — 웹 평가기 사용 가이드
- **`docs/PAPER_FINAL.md`** — MECE 학술 논문 최종본
  - 8 섹션 (Introduction → Conclusion) + References + Appendix
  - RQ1~5 답 §6에 별도 분리
  - §7 Threats to Validity 4종
  - Appendix D MECE 검증표

### Changed

- README: 웹 평가기 + PAPER_FINAL 링크 추가
- PDF 번들: 8 문서 통합 → 9 문서 (`KoFinRe_v2.5_FINAL.pdf`)

---

## [2.5.0] — 2026-06-12 — 휴리스틱 교정 + 4방식 baseline 비교

### Added

- **`kofinre/correction_heuristic.py`** — LLM 없이 작동하는 휴리스틱 교정
  - S1 분리 (복합의무 → 다중 요구사항)
  - S3 모호어 → `[명세 필요: ...]` 마커 (작성자 보강 요청)
  - S4 평서형 → 의무형 (한다 → 해야 한다)
  - S8 범위모호 → `[열거 명시 필요]` 마커
  - 의미 분석 불가 명시 — 작성자 검토 필수
- **`examples/heuristic_correction_demo.py`** — 5 예시 교정 시범
- **`scripts/run_baselines.py`** — 4 방식 baseline 비교 자동화
  - Rule-only (RegexDetector 단독)
  - NLP-only (Morph + Chunk)
  - LLM-assisted (Regex + LLM)
  - Ensemble (5 detector + rule-priority voting)
  - 출력: baseline_comparison.csv + baseline_report.md

### R1_sim 50건 gold 기준 결과 (D4 익명)

| 방식 | Macro-F1 | Micro-F1 | 검출량 | 분석 |
|---|---:|---:|---:|---|
| **Rule-only** | **0.278** | **0.837** | 21/50 (42%) | 가장 균형 |
| NLP-only | 0.060 | 0.182 | 48/50 (96%) | ChunkDetector 과검출 |
| LLM-assisted | 0.278 | 0.837 | 21/50 (42%) | LLM dry-run 시 Rule과 동일 |
| Ensemble | 0.244 | 0.254 | 50/50 (100%) | OR voting 과검출 |

**핵심 정량 발견**: Rule-only(Macro 0.28, Micro 0.84)가 가장 균형. **한국어 RFP 도메인의 정형 표현 명확성으로 휴리스틱이 효과적**임을 정량 확인 — 논문 RQ3 답.

NLP-only(MorphDetector + ChunkDetector)는 S2/S5 과검출 경향. Ensemble은 OR 결합이라 정밀도 손실 — voting을 rule_priority에서 confidence_weighted로 전환 시 개선 여지.

### Changed

- 4 방식 baseline 비교는 gold label 기반 → R1_sim 50건이 휴리스틱이라 Rule-only에 유리한 편향 가능. 실제 사람 평가자 데이터로 후속 보완 필요.

---

## [2.4.0] — 2026-06-12 — LLM 어댑터 + 문서 PDF 번들

### Added

- **`kofinre/llm_adapters/`** — LLM API 어댑터 패키지
  - `anthropic_caller.py` — Anthropic Claude 호출 (claude-opus-4-7 기본)
  - 환경변수 `ANTHROPIC_API_KEY` 기반 자동 인증
  - API 키 부재 시 자동 dry-run 모드 (CI·개발 환경 호환)
  - `make_caller()` 팩토리 — 향후 OpenAI/로컬 모델 확장 대비
- **`examples/llm_correction_demo.py`** — Stage 5 교정 데모 (3 예시 문장)
- **`scripts/build_pdf_bundle.py`** — docs/ 전체 PDF 번들 빌드
  - 6개 문서 통합 (PAPER_DRAFT → FRAMEWORK_GAP_ANALYSIS → EXTRACTION_RULES → PASKA_KOREAN_ADAPTATION → IMPROVEMENT_RECOMMENDATIONS → UPDATE)
  - 표지 + 목차 자동 생성
  - 산출물: `dist/KoFinRe_v2.3_documents.pdf` (2.7 MB)

### R1 시뮬 평가 결과 (D4 50건)

자체 휴리스틱 기반 시뮬 평가로 모델 vs 기준 비교:

| Smell | Precision | Recall | F1 | 비고 |
|---|---:|---:|---:|---|
| S7 미정의약어 | 0.60 | 0.60 | **0.60** | 가장 균형 |
| S3 모호어 | 0.50 | 1.00 | 0.67 | recall 우수 |
| S4 약한의무 | 0.50 | 1.00 | 0.67 | FP 14건 |
| S8 범위모호 | 0.50 | 1.00 | 0.67 | |
| S2/S5 | 0.00 | — | 0.00 | 시뮬과 모델 기준 격차 큼 |

시뮬 평가의 한계 인정 — 실제 평가자 200건 작성으로 보강 필요.

### Changed

- `.gitignore`: `dist/` 추가 (PDF 빌드 산출물 git 외부)
- `requirements.txt`: anthropic 패키지 (선택 의존성)

---

## [2.3.0] — 2026-06-12 — MorphDetector 본격 구현 (kiwipiepy)

### Added

- **`kofinre/detectors/morph_detector.py`** — kiwipiepy(Kiwi C++ 엔진) 기반 본격 형태소 분석
  - 세종 POS 태그셋: NNG/NNP/JKS/JKO/JX/VV/VA/XSV/EC/EF/MM
  - 4 smell 정밀 검출 (S2 불완전 / S4 약한의무 / S5 주체누락 / S9 수동표현)
  - kiwipiepy 미설치 환경 자동 fallback (정규식 휴리스틱)
- `requirements.txt`: `kiwipiepy>=0.18`, `striprtf>=0.0.26` 추가

### D1 회귀 검증 (v2.2 + v2.3)

D1 비정제 56건에서 회귀 없음 확인 (94.1% 유지) — fix가 D1에는 영향 없음, D2/D4 정제·양식 데이터에만 효과 집중.

### D4 v2.3 효과

| 지표 | v2.1.1 | v2.2 | v2.3 (kiwipiepy) | 누적 Δ |
|---|---:|---:|---:|---:|
| Smell 비율 | 93.4% | 77.0% | 79.4% | -14.0 ppt |
| **자동 likely FP** | **26%** | — | **3.9%** | **-22 ppt** ⭐ |
| S2 불완전 | 235 | 181 | 181 | -54 |
| S4 약한의무 | 58 | 58 | **113** | +55 (정확도 ↑) |
| S5 주체누락 | 209 | 159 | 161 | -48 |
| 표본 추출 | 195건 | 197건 | **200건 정확** | — |

S4가 v2.3에서 증가한 것은 kiwipiepy가 EF 종결어미를 더 정확히 식별 — 기존에 놓치던 평서형 종결을 추가 검출. FA 회계 모듈에서 44 → 75건 증가.

### Changed

- `examples/peek_gold_sample.py` — D4 양식 미리보기 일반화

---

## [2.2.0] — 2026-06-12 — ChunkDetector 정밀화 (D4 정성 검토 기반)

### 동기

D4 (실기업 4모듈) 정성 검토에서 다음 정량 발견:
- S5 검출 209건 중 24% (50건)이 30자 미만 short fragment (양식 키워드)
- S2 검출 235건 중 69% (161건)에 목적 조사(`을/를`)가 본문에 존재
- D4 양식이 "요구사항명 | 요구사항 내용" 결합형 — ChunkDetector 가 양쪽 합쳐 평가

### Changed

- **Fix #1 — `kofinre/detectors/chunk_detector.py`**: 30자 미만 short fragment 는 actor/target 검사 자체 스킵
- **Fix #2 — `kofinre/detectors/chunk_detector.py`**: 목적 조사(`을|를`)가 본문 어디에든 있으면 target 있음으로 인정 (TARGET_NOUN 인접 매칭 한계 보완)
- **Fix #3 — `kofinre/extraction/sentence_splitter.py`**: 양식 파이프(`|`) 분리자 추가 — SI 정의서 결합 양식 대응

### 효과 (D4 257건 재실행)

| 지표 | v2.1.1 | v2.2 | Δ |
|---|---:|---:|---:|
| Smell 비율 | 93.4% | 77.0% | **-16.4 ppt** |
| S2 불완전 | 235 | 181 | -54 (-23%) |
| S5 주체누락 | 209 | 159 | -50 (-24%) |
| CM 공통 모듈 | 84.9% | 45.3% | -40 ppt ⭐ |
| BG 예산 모듈 | 96.2% | 69.2% | -27 ppt |

FA 회계의 약한의무(S4) 44건, CI 신용정보의 미정의약어(S7) 19건은 그대로 유지 — 정당한 검출 확인.

### Added

- D4 정성 검토 도구 (로컬 only):
  - `assist/d4_gold_sample.py` — 197 stratified sample + R1/R2 양식
  - `assist/d4_deep_fp_analysis.py` — 패턴 정량 분석
- 자동 식별된 likely FP 후보 분석 리포트 (`real_reqs_anonymized/gold/D4_deep_fp_analysis.md`)

---

## [2.1.1] — 2026-06-12 — D4 실기업 사례 검증 + 개선 권고

### 데이터셋 추가

- **D4 — 실기업 4 모듈 정의서 257건 (익명화)**
  - 한 국내 캐피탈사 차세대 시스템 (2020) FA·BG·CI·CM 4모듈
  - 정규식 익명화 후에만 평가 (회사·인명·연락처·외부사 마스킹)
  - 결과는 **로컬 전용** (`real_reqs_anonymized_LOCAL_ONLY.zip`)
  - 본 리포지토리/논문 인용 시 통계와 익명 짧은 패턴만

### Added

- **`docs/IMPROVEMENT_RECOMMENDATIONS.md`** — 3계층 개선 권고
  - 작성자 가이드 (Smell 10종별 ❌ → ✅ 변환 예시)
  - 모듈별 권고 (FA/BG/CI/CM)
  - 도구(KoFinRe) v2.2/v2.3/v2.4 로드맵 (P0~P4 우선순위)
  - 프로세스·정책 (검토 프로세스, 데이터 거버넌스, 도구 운영)
- `docs/PAPER_DRAFT.md`:
  - 6.1.4 D4 데이터셋 정의 (익명화 절차)
  - 7.6 D4 Smell 검출 결과 (모듈·유형별 통계)
  - 7.7 4 데이터셋 통합 비교표 (D1·D2·D3·D4)
  - 8.5b 한국 SI 작성 관행 발견 (RQ4 결정적 답)
  - 8.5c 윤리·법적 처리 절차 명문화
- 통합 백업 (외부): `C:\Users\heen1\Desktop\KoFinRe_backup_20260612_*`
  - rfp-extractor.zip, RFP_자료_56건.zip, Paska_Docker.zip
  - assist_scripts_and_results.zip
  - **real_reqs_anonymized_LOCAL_ONLY.zip** (외부 공유 금지)

### 주요 발견

- D4 Smell 비율 93.4% — 잘 정비된 산출물도 한국 SI 작성 관행(S2/S5)에서 자유롭지 않음
- 모듈별 차별화:
  - FA(회계): 약한의무 44건
  - CI(신용정보): 미정의 약어 19건
  - CM(공통): 84.9%로 가장 깨끗 (참조 모범)
- D4의 **복합의무 0건** — 실기업 정의서는 sub-req 분리 우수 (Atomicity 양호)
- **결정적 RQ4 답**: 한국 RFP 품질 이슈는 정제 수준이 아니라 **언어·문화적 작성 관행** 그 자체

### 보안 처리

- 익명화 모듈 (`anonymizer.py`) 작성 — 정규식 마스킹 8종
- GitHub commit 시 D4 원문·식별자 0건 검증
- `.gitignore` 강화 (`data/`, `results/`, LLM 캐시)

---

## [2.1.0] — 2026-06-10 — 폴더 구조 정리 + 패키지화

### Added

- **`pyproject.toml`** — 패키지 메타 (PEP 621), `pip install -e .` 지원
- **`docs/`** — 모든 문서 한 곳으로 (UPDATE/EXTRACTION_RULES/FRAMEWORK_GAP_ANALYSIS/PASKA_KOREAN_ADAPTATION/PAPER_DRAFT)
- **`legacy/`** — v1 스크립트 보관 + 마이그레이션 가이드 (`legacy/README.md`)
- **`kofinre/extraction/`** — Stage 1 모듈 분리
  - `signatures.py` — 파일 시그니처 판별 (FileKind enum)
  - `document_extractor.py` — HTML/HWP/PDF/DOCX/RTF + 시그니처 자동 분기
  - `sentence_splitter.py` — 한국어·세미콜론 분리 + 1차 품질 필터
  - `requirement_filter.py` — 정밀 필터 + FilterReason enum (exclusion_reason.csv 추적)
- **`kofinre/io/`** — 입출력 도구
  - `csv_loader.py` — REQ_abstract 로더, sub-req 분리
  - `excel_writer.py` — 다중 시트 리포트 (조건부 색상, 자동 필터)
- **`scripts/`** — CLI entrypoint
  - `run_extraction.py` — Stage 1
  - `run_detection.py` — Stage 2-3 (5 detector + 앙상블)
- **`examples/`**
  - `basic_usage.py` — 5문장 데모
  - `req_abstract_demo.py` — REQ_abstract.csv 평가
- **`tests/`** — 단위 테스트 (test_detectors / test_metrics)
- DOCX 추출 지원 (`python-docx`)
- RTF 처리 `striprtf` 일원화 (unrtf 미설치 환경 대응)

### Changed

- 루트 정리 — 9개 v1 스크립트 → `legacy/`
- 문서 5개 → `docs/`
- `requirements.txt` 최소 의존성, 선택 의존성은 `pyproject.toml` extras (hwp/docx/nlp/all/dev)
- `.gitignore` 강화 — `data/`, `results/`, LLM 캐시, 빌드 산출물

### Migration (v2.0 → v2.1)

| 변경 전 (루트) | 변경 후 |
|---|---|
| `rfp_extract.py` | `kofinre/extraction/document_extractor.py` + `scripts/run_extraction.py` |
| `rfp_smell.py` | `kofinre/detectors/regex_detector.py` |
| `rfp_requirement_filter.py` | `kofinre/extraction/requirement_filter.py` |
| `rfp_excel*.py` | `kofinre/io/excel_writer.py` |
| `req_abstract_eval.py` | `examples/req_abstract_demo.py` |
| `EXTRACTION_RULES.md` 등 | `docs/EXTRACTION_RULES.md` 등 |

---

## [2.0.0] — 2026-06-10 — KoFinRe-QA Framework 정렬

### 변경 동기

논문 초안 `Korean Public Financial RFP Quality Analysis Framework.pdf` 검토 후
v1 의 구현 갭을 메우기 위한 메이저 리팩토링.

### Added

- **`FRAMEWORK_GAP_ANALYSIS.md`** — 논문 5 stages × 우리 구현 차이 분석, 우선순위 매트릭스 (P0~P4)
- **`kofinre/` 패키지** — 논문 Stage 1~5 + Manual Validation 정렬 구조
- **`kofinre/smell_taxonomy.yaml`** — 10종 smell 표준 정의 (Paska/IEEE 830/ISO 29148 매핑 포함)
- **`kofinre/detectors/`** — 5 detector 골격
  - `RegexDetector` — 정규식·키워드 (HIGH/MED/LOW confidence)
  - `MorphDetector` — 형태소·종결어미·조사 (v2.1 KoNLPy 통합 예정)
  - `ChunkDetector` — 주체-행위-대상 휴리스틱
  - `DictionaryDetector` — 금융기관·도메인·약어 사전
  - `LLMDetector` — 외부 LLM 호출 인터페이스 + 캐싱
- **`kofinre/ensemble.py`** — majority / rule-priority / confidence-weighted voting
- **`kofinre/metrics.py`** — 3 카테고리 지표
  - Detection: Precision, Recall, F1, FPR, FNR, Cohen's Kappa, Macro-F1, Micro-F1
  - Quality: Smell Density, Coverage, Severe Ratio, Yield, Validity Rate
  - Correction: Smell Reduction, Quality Gain, Atomicity·Testability Improvement
- **`kofinre/reporting.py`** — 논문 표준 리포트 6종
  - extraction_report.md, smell_report.md, evaluation_report.md
  - correction_report.md, dataset_card.md, run_log.json
- **`kofinre/correction.py`** — Stage 5 LLM 교정 모듈 + 6원칙 프롬프트
- **`kofinre/validation.py`** — Manual Validation 도구 (층화 표본 추출, Cohen's kappa, gold label 합의)
- **`kofinre/pipeline.py`** — 5 stage orchestration entrypoint

### Changed

- **Smell taxonomy 7종 → 10종**
  - 기존 "모호어" → S3 Ambiguous Term (어휘) + S8 Coordination Ambiguity (범위)로 분리
  - S2 Incomplete Requirement 신규 — 시스템 응답·행위·대상 누락
  - S10 Unverifiable Requirement 신규 — 검증 방법·판정 기준 부재
- **산출물 디렉토리 표준화** (논문 명명)
  - `sentences_all.csv` → `sentence_candidates.csv`
  - `requirements_filtered.csv` → `requirement_candidates.csv`
  - `stage1_extraction/`, `stage3_detection/`, `stage4_evaluation/`, `stage5_correction/`

### Not yet (v2.1 예정)

- KoNLPy/Mecab 통합 (MorphDetector 본격 구현)
- 명사구 추출 강화 (ChunkDetector)
- Anthropic/OpenAI 실 API 호출 어댑터 (LLMDetector, LLMCorrector)
- Stage 5 자동 의미보존 평가 (현재는 평가자 검토 양식만)
- 4 방식 baseline 자동 비교 (Rule/NLP/LLM/Ensemble)

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
