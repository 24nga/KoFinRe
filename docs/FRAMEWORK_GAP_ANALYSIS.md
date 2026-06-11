# 논문 KoFinRe-QA Framework vs 현재 구현 갭 분석

> 원본: `Korean Public Financial RFP Quality Analysis Framework.pdf` (2026-06-10, 11p)
> 현재 구현: 본 저장소(24nga/KoFinRe) v1.0.2

## 0. 결론 요약

| 단계 | 논문 명세 | 현재 구현 | 갭 |
|---|---|---|---|
| **Stage 1** 요구사항 추출 | ✓ 다포맷 + 산출물 표준화 | ✓ 다포맷 추출 + 산출물 비표준 | 산출물 명명 정렬 필요 |
| **Stage 2** Smell 정의 | **10종** | **7종** | S2/S8 분리, S10 신규 — 3종 추가 |
| **Stage 3** 앙상블 탐지 | 5 detector + voting | Regex 단일 | **앙상블 구조 부재 — 주요 갭** |
| **Stage 4** 정량 평가 | 3 카테고리 + 6 리포트 | summary.json + xlsx | 평가 모듈·리포트 표준 부재 |
| **Stage 5** LLM 교정 | 6원칙 + 6지표 | **미구현** | **전면 신규 작업** |
| Manual Validation | 2+평가자, kappa, 200건 | 없음 | 검증 워크플로우 부재 |
| Baseline 비교 | Rule/NLP/LLM/Ensemble/Paska-EN | Rule만 (Paska-EN 별도) | 4 분기 비교 부재 |

---

## 1. Stage 별 상세 갭

### 1.1 Stage 1 — RFP 문서 수집 및 요구사항 후보 추출

#### 논문 명세
- 수집 대상: 정보시스템 구축·고도화·개선·데이터 플랫폼·AI/데이터 RFP
- 제외: 감리, PMO, 단순 컨설팅, 유지보수 단독
- 포맷: HWP, PDF, DOCX, HTML, RTF
- 후처리: 문장 분리, 표 구조 보존, 중복 제거, 입찰안내문/평가기준/푸터/메타데이터 제거
- 요구사항 후보 식별 기준: 의무 표현, 시스템 행위 동사, 기능 대상 객체, 데이터 처리 단서, 인터페이스 단서, 품질속성 단서

#### 산출물 명명 (논문 표준)
```
raw_documents/
extracted_text/
sentence_candidates.csv
requirement_candidates.csv
extraction_log.json
exclusion_reason.csv
```

#### 현재 구현
| 항목 | 현재 | 갭 |
|---|---|---|
| 포맷 | HTML, HWP, PDF, RTF ✓ | DOCX 미지원 |
| 후처리 | ✓ (대부분) | 표 구조 보존 미흡 |
| 후보 식별 | ✓ EXTRACTION_RULES.md | 데이터 처리·인터페이스·품질속성 단서 명시 미흡 |
| **산출물 명명** | `rfp_extract/*.txt`, `sentences_all.csv`, `requirements_filtered.csv` | **논문 표준과 다름** |
| **exclusion_reason.csv** | ❌ | **신규 필요** — 컷 사유 추적 |

**개선 작업**:
- 산출물 이름 정렬: `sentences_all.csv` → `sentence_candidates.csv`, `requirements_filtered.csv` → `requirement_candidates.csv`
- `exclusion_reason.csv` 신규 — 각 문장이 왜 컷됐는지 사유 기록
- DOCX 지원 추가 (python-docx)

---

### 1.2 Stage 2 — Smell 정의 (가장 중요한 갭)

#### 논문 명세 (10종)

| Code | Name | Definition | Quality Attribute |
|---|---|---|---|
| S1 | Non-atomic Requirement | 한 요구사항에 둘 이상의 기능 응답 | Atomicity |
| S2 | **Incomplete Requirement** | 시스템 응답·행위·대상이 불완전 | Completeness |
| S3 | Ambiguous Term | "적절히, 필요한, 관련, 실시간" 등 | Unambiguity |
| S4 | Weak Obligation | "한다, 된다, 가능하다" | Verifiability |
| S5 | Missing Actor | 수행 주체·책임 주체 미명시 | Completeness |
| S6 | Missing Quantification | 성능·용량·처리량·시간·정확도 정량 부재 | Testability |
| S7 | Undefined Acronym | 영문/도메인 약어 정의 없음 | Traceability |
| S8 | **Coordination Ambiguity** | "및/또는, 등, 포함, 관련" 범위 불명확 | Unambiguity |
| S9 | Passive or Agentless Expression | "처리되어야 한다, 관리되어야 한다" | Clarity |
| S10 | **Unverifiable Requirement** | 검증 방법·판정 기준 불명확 | Verifiability |

#### 현재 구현 (7종)

| 현재 | 논문 매핑 | 변경 |
|---|---|---|
| 모호어 | S3 Ambiguous Term + S8 Coordination Ambiguity (혼합) | **분리** |
| 수동태 | S9 Passive Expression | ✓ 일치 |
| 복합의무 | S1 Non-atomic | ✓ 일치 |
| 정량부재 | S6 Missing Quantification | ✓ 일치 |
| 미정의 약어 | S7 Undefined Acronym | ✓ 일치 |
| 주체모호 | S5 Missing Actor | ✓ 일치 |
| 약한의무 | S4 Weak Obligation | ✓ 일치 |
| — | **S2 Incomplete Requirement** | **신규 필요** |
| — | **S10 Unverifiable Requirement** | **신규 필요** |

**개선 작업**:
- 모호어 → S3 (어휘 모호) + S8 (범위 모호 "및/또는, 등") 분리
- S2 Incomplete Requirement 신규: 시스템 응답/행위/대상 중 하나라도 누락
- S10 Unverifiable Requirement 신규: 검증·판정 기준 명시 부재

---

### 1.3 Stage 3 — NLP 앙상블 탐지 (가장 큰 갭)

#### 논문 명세 (5 detector + voting)

| Analyzer | Role |
|---|---|
| Regex-based Detector | 의무·모호어·정량부재·약어 등 명시적 패턴 |
| Morphological Analyzer | 형태소·품사·종결어미·조사·명사구 |
| Dependency/Chunk Heuristic | 주체-행위-대상 구조 추정 |
| Domain Dictionary Detector | 금융기관·업무·데이터·인터페이스·약어 사전 |
| LLM-assisted Classifier | 규칙으로 판단 어려운 smell 보조 판정 |
| Manual Gold Label | 평가자 검증용 기준 라벨 |

**Voting**: majority / rule-priority / confidence-weighted 중 rule-priority 기본

#### 현재 구현
- **Regex 단일** — 나머지 4 detector 모두 부재
- Voting 메커니즘 없음
- Confidence 출력 없음

**이게 가장 큰 차이**. 현재는 사실상 "rule-only baseline"에 해당. 논문이 비교하려는 Ensemble 그룹을 형성할 수 없음.

**개선 작업** (우선순위 ↑):
1. `detectors/regex_detector.py` — 기존 로직 분리
2. `detectors/morph_detector.py` — 형태소 분석기 (KoNLPy/Mecab 또는 가벼운 대안)
3. `detectors/chunk_detector.py` — 주체-행위-대상 휴리스틱
4. `detectors/dictionary_detector.py` — 도메인 사전
5. `detectors/llm_detector.py` — Claude/GPT API 호출 골격
6. `ensemble.py` — rule-priority voting
7. 각 detector는 표준 인터페이스: `detect(sentence) -> {smell_code: (label, confidence)}`

---

### 1.4 Stage 4 — 정량 평가 + 리포팅

#### 논문 명세

**4.1 Detection Performance Metrics** (gold label 있을 때)
- Precision, Recall, F1-score
- False Positive Rate, False Negative Rate
- Cohen's Kappa
- Macro-F1, Micro-F1

**4.2 Requirement Quality Metrics**
- Smell Density (전체 smell / 전체 요구사항)
- Smell Coverage (smell≥1 요구사항 비율)
- Average Smell per Requirement
- Severe Smell Ratio (정량부재·불완전·검증불가 등)
- Requirement Extraction Yield
- Dataset Validity Rate

**4.3 리포트 6종** (모두 마크다운)
| Report | Content |
|---|---|
| `extraction_report.md` | 문서별 추출 성공률·실패 사유·요구사항 후보 수 |
| `smell_report.md` | smell 유형별 빈도·비율·예시 |
| `evaluation_report.md` | precision·recall·F1·kappa·오류분석 |
| `correction_report.md` | LLM 교정 전후 smell 변화·의미보존 |
| `dataset_card.md` | 데이터셋 구성·출처·라이선스·제한사항 |
| `run_log.json` | 실행 시각·입력 파일·모델·규칙 버전·결과 파일 |

#### 현재 구현
- `summary.json` 1종 (요약 통계만)
- Excel 다중 시트 (논문 표준 아님)
- gold label 기반 metric (precision/recall/F1/kappa) **전무**
- Quality metric 일부 (Smell Density 동등 산출 가능)

**개선 작업**:
- `metrics.py` 신규: detection + quality + correction 카테고리
- 리포트 6종 골격 마크다운 자동 생성
- `run_log.json` 형식 표준화 (재현성)

---

### 1.5 Stage 5 — LLM 교정 (전면 신규)

#### 논문 명세

**교정 원칙 6개**
1. 원문 의미 유지
2. 원문에 없는 기능·조건·정책·인터페이스·데이터 항목 추가 금지
3. 한 요구사항 = 하나의 기능 또는 품질조건 (원자성)
4. 모호 표현 → 검증 가능 표현
5. 주체·조건·행위·대상·결과 명확화
6. 교정 전후 의미 차이·추가정보 기록

**교정 효과 평가 6지표**
| Metric | Definition |
|---|---|
| Smell Reduction Rate | 교정 전 smell 수 대비 감소율 |
| Quality Score Gain | 교정 후 - 교정 전 품질점수 |
| Semantic Preservation Rate | 원문 의미가 유지된 비율 |
| Over-correction Rate | 원문에 없는 정보가 추가된 비율 |
| Atomicity Improvement Rate | 복합 → 원자로 개선된 비율 |
| Testability Improvement Rate | 정량/검증 기준이 보완된 비율 |

#### 현재 구현
- **전무**

**개선 작업**:
- `correction.py` 신규
- 6원칙 시스템 prompt
- LLM API 호출 (Claude/GPT 등) 인터페이스
- 교정 전후 동일 detector 재실행
- 의미보존 vs 과잉보완 자동 분류 (또는 평가자 검토 양식)

---

### 1.6 Manual Validation (신규)

#### 논문 명세
- 최소 2명 평가자 독립 판정
- Cohen's kappa 일치도
- 불일치 항목 합의 → gold label
- 최소 200건 표본, 층화추출 (smell 있음/없음 모두 포함)

#### 현재 구현
- 없음

**개선 작업**:
- `validation/sampling.py` — 층화 표본 추출
- `validation/cohens_kappa.py` — 평가자 간 일치도 계산
- `validation/gold_label_template.csv` — 평가자 입력 양식

---

### 1.7 Baseline 및 비교 (논문 표 5종)

| Method | 설명 | 현재 구현 |
|---|---|---|
| Rule-only | 정규식·키워드 | ✓ 본질적으로 이게 현재 상태 |
| NLP-only | 한국어 NLP 전처리 기반 | ❌ |
| LLM-assisted | LLM 보조 판정 | ❌ |
| Ensemble | 위 셋 결합 | ❌ |
| Paska-English | PURE에 대한 Paska 기준선 | ✓ Docker 환경 보존 |

**개선 작업**: Stage 3 앙상블 골격이 완성되면 4 방식 비교표 자동 산출 가능

---

## 2. Smell Taxonomy 7→10 상세 매핑

| 논문 코드 | 논문 이름 | 현재 매핑 | 처리 |
|---|---|---|---|
| S1 | Non-atomic Requirement | 복합의무 | 유지, S1로 리네임 |
| **S2** | **Incomplete Requirement** | 없음 | **신규**: 시스템 응답·행위·대상 중 하나라도 누락 |
| S3 | Ambiguous Term | 모호어 (어휘 부분) | 좁힘 — 어휘 모호만 |
| S4 | Weak Obligation | 약한의무 | 유지 |
| S5 | Missing Actor | 주체모호 | 유지, 리네임 |
| S6 | Missing Quantification | 정량부재 | 유지 |
| S7 | Undefined Acronym | 미정의 약어 | 유지 |
| **S8** | **Coordination Ambiguity** | 모호어 (범위 부분) | **분리**: "및/또는, 등, 포함, 관련" |
| S9 | Passive or Agentless | 수동태 | 유지, 리네임 |
| **S10** | **Unverifiable Requirement** | 없음 | **신규**: 검증·판정 기준 부재 |

### 2.1 S2 Incomplete Requirement — 신규 정의 안

**규칙**:
- 의무 표현이 있지만(`~해야 한다` 등) 시스템 응답·행위·대상 중 하나라도 명확하지 않으면 검출
- 구체적 패턴:
  - 행위 동사 부재 (`해야 한다` 직전에 동사 명사형 없음)
  - 대상 객체 부재 (`~를/을` 보조사 없이 의무 표현)
  - 시스템 응답 부재 (조건절만 있고 결과절 없음)

### 2.2 S8 Coordination Ambiguity — 분리 안

**규칙**:
- `및/또는|등|포함|관련` 표현 + 명사구가 열거된 경우
- 예: "사용자 인증, 권한관리 **등**을 지원해야 한다" → "등"의 범위 불명확
- 예: "보안 시스템 **및/또는** 인증 모듈을 구축해야 한다" → 둘 다인가 하나만인가

### 2.3 S10 Unverifiable Requirement — 신규 정의 안

**규칙**:
- 의무 표현이 있지만 검증 방법·판정 기준 부재
- 구체적 패턴:
  - 측정 가능 키워드(`성능, 응답시간, 처리량, 정확도` 등) 부재 + 정성 표현(`효율적, 안정적, 신뢰성 있는` 등)
  - 또는 조건 표현(`~경우`)이 있지만 결과 측정 기준 미명시
- S6 Missing Quantification과 차이: S6은 정량 지표가 빠진 것, S10은 검증 절차 자체가 불명확한 것 (더 포괄적)

---

## 3. 산출물 디렉토리 표준 (논문 → 본 저장소)

논문 표준 디렉토리 구조로 정렬:

```
KoFinRe/
├── raw_documents/                      ← 원본 RFP (HWP/PDF/HTML/RTF)
├── extracted_text/                     ← 텍스트 추출 후
├── stage1_extraction/
│   ├── sentence_candidates.csv         ← 문장 후보 전체
│   ├── requirement_candidates.csv      ← 요구사항 후보 (정밀 필터 통과)
│   ├── extraction_log.json
│   └── exclusion_reason.csv            ← (신규) 각 문장 컷 사유
├── stage2_smell_definition/
│   └── smell_taxonomy.yaml             ← (신규) 10종 smell 정의
├── stage3_detection/
│   ├── detector_outputs/
│   │   ├── regex_detector.csv
│   │   ├── morph_detector.csv          ← (신규)
│   │   ├── chunk_detector.csv          ← (신규)
│   │   ├── dictionary_detector.csv     ← (신규)
│   │   └── llm_detector.csv            ← (신규)
│   ├── ensemble_smell_labels.csv
│   ├── detector_confidence.csv
│   └── manual_validation_sample.csv    ← (신규)
├── stage4_evaluation/
│   ├── extraction_report.md            ← (신규)
│   ├── smell_report.md                 ← (신규)
│   ├── evaluation_report.md            ← (신규, gold label 있을 때)
│   ├── dataset_card.md                 ← (신규)
│   └── run_log.json                    ← (신규)
└── stage5_correction/
    ├── corrected_requirements.csv       ← (신규)
    ├── correction_diff.csv             ← (신규)
    ├── correction_report.md            ← (신규)
    └── re_evaluation.csv               ← (신규)
```

---

## 4. 우선순위 매트릭스

| 항목 | 영향 | 작업량 | 우선순위 |
|---|---|---|---|
| Smell 7→10 확장 (S2, S8 분리, S10) | 高 | 중 | **P0** |
| 디렉토리·산출물 명명 표준화 | 中 | 저 | **P0** |
| `exclusion_reason.csv` 신규 | 中 | 저 | **P0** |
| 리포트 6종 골격 | 高 | 중 | **P1** |
| 평가 지표 모듈 (`metrics.py`) | 高 | 중 | **P1** |
| Detector 분리 (Regex 단독 → 5개 골격) | 高 | 大 | **P1** |
| Ensemble voting | 高 | 중 | **P1** |
| Stage 5 LLM 교정 | 高 | 大 | **P2** |
| Manual Validation 도구 | 中 | 중 | **P2** |
| Baseline 4 방식 비교 자동화 | 中 | 중 | **P3** |
| DOCX 추출 지원 | 저 | 저 | **P3** |
| 표 구조 보존 강화 | 저 | 大 | **P4** |

---

## 5. 단계별 실행 계획

### v2.0 (이번 PR) — P0 항목
- Smell 10종 정의·구현
- 디렉토리·산출물 명명 표준화
- `exclusion_reason.csv` 추가

### v2.1 — P1 항목
- Detector 분리·앙상블 골격
- 평가 지표 모듈
- 리포트 6종 마크다운 골격

### v2.2 — P2 항목
- Stage 5 LLM 교정 모듈
- Manual Validation 도구 + Cohen's kappa

### v2.3 — P3 항목
- 4 방식 baseline 자동 비교
- DOCX 지원

---

## 6. 검증 — 이번 작업 완료 시 논문 기준 충족도

| 논문 RQ | 현재 충족 | v2.0 후 | 최종 (v2.x) |
|---|---|---|---|
| RQ1 요구사항 후보 추출 기준 | 부분 | ✓ (exclusion 사유 추적) | ✓ |
| RQ2 한국어 smell 정의 | 7종 (부족) | ✓ 10종 | ✓ |
| RQ3 앙상블 성능 향상 | ❌ | 일부 (골격) | ✓ (5 detector 완성) |
| RQ4 빈번 smell 유형 | 부분 (7종) | ✓ | ✓ |
| RQ5 LLM 교정 효과 | ❌ | ❌ | ✓ (v2.2 후) |
