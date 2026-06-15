# KoFinRe Project Journey — 전체 과정 정리

> 한국어 공공금융 RFP 요구사항 품질 자동 평가 도구 KoFinRe의
> 1.0 → 2.8 전 과정 회고 (2026-06-07 ~ 2026-06-15)

---

## 0. 한 줄 요약

영문 SRS 평가 도구 **Paska**를 한국어 공공금융 RFP·실기업 정의서 대응으로 어댑테이션하면서, NLP 의존성 제거 → 정규식 → 형태소 분석(kiwipiepy) → LLM 어댑터 → 휴리스틱 교정 → **6대 표준 정렬(IEEE 830 / ISO 29148 / INCOSE / EARS / CMMI / NCS)** 까지 진화. 4 데이터셋(D1~D4) 검증, 자동 likely-FP **26% → 3.9%**, Smell **7 → 10 → 15 → 19**, 표준 커버리지 **~20% → ~70%**, RQ3 답 "Rule-only가 한국 RFP 도메인에서 최선" 정량 확인.

---

## 1. 프로젝트 동기

### 출발점
- 한국 공공금융 RFP의 품질 이슈가 시스템 개발 분쟁의 핵심 원인
- 영문권엔 Paska (Veizaga 2021)·PURE 같은 도구·데이터셋 있으나 한국어 미지원
- 사용자 본인의 논문 [`Korean Public Financial RFP Quality Analysis Framework`] 초안이 KoFinRe-QA Framework 5단계를 제안
- 실증 도구·데이터셋 부재

### 5개 연구 질문 (논문)
- **RQ1** 한국 RFP에서 요구사항 후보를 신뢰성 있게 추출하는 기준은?
- **RQ2** Paska smell taxonomy + 한국 RFP 특성 반영 정의?
- **RQ3** 한국어 NLP 앙상블이 smell 탐지 성능을 향상시키는가?
- **RQ4** 한국 RFP에서 가장 빈번한 작성오류 유형은?
- **RQ5** LLM 기반 교정이 smell을 감소시키면서 의미를 보존하는가?

---

## 2. 시간순 여정 (13단계)

### Step 1. 데이터 수집 (D1)
- 12개 공공금융기관 RFP 56건 자동 다운로드
- HTML 55 + HWP 20 + PDF 5 + RTF 1
- 발견: 사이트 인증·차단으로 본문 추출 **14건 (25%)** 성공

### Step 2. Paska 영문 Docker 환경 구축
- Ubuntu 20.04 + JDK 8 + Python 3.8 + allennlp 2.10.1 + Stanford POS tagger
- Docker 이미지 5.9 GB
- PURE 영문 SRS 79건 (D3)으로 검증 — 1,200 reqs 처리, 영문 baseline 확보

### Step 3. v1.0 한국어 자체 도구 제작
- Paska가 Windows + 한국어 미지원 → 정규식·키워드 휴리스틱 기반 자체 구현
- **7종 smell** 정의 (Paska 9종 → 한국어 매핑 + 약한의무·미정의약어 신규)
- D1 56건 분석: 3,210 문장 → 정밀필터 75건 → Smell 65.3%

### Step 4. REQ_abstract 30건 (D2) 평가
- 사용자가 제공한 정형 CSV (3 프로젝트 × 30 req → sub-req 140건)
- v1.0 결과: 56.7% smell, P003(AML) 100% 검출 → 도메인 위험성 정량화

### Step 5. 논문 받고 v2.0 정렬 (대전환)
- 논문 `KoFinRe-QA Framework` 11p 검토 → **갭 분석**
- v1.0 7-smell × 단일 detector → 논문 10-smell × 5-detector + 앙상블 요구
- `FRAMEWORK_GAP_ANALYSIS.md` 작성
- v2.0: 10 smell (S2 Incomplete, S8 Coord Ambiguity, S10 Unverifiable 신규), 5 detector 골격, 6 표준 리포트, Stage 5 교정 인터페이스

### Step 6. v2.1 폴더 정리·패키지화
- 루트 17개 파일 → `kofinre/` 패키지 + `docs/` + `legacy/` + `scripts/` + `examples/` + `tests/`
- `pyproject.toml` PEP 621, `pip install -e .` 지원
- 단위 테스트 11/12 통과

### Step 7. 실기업 4모듈 평가 (D4) — 가장 큰 도전
- 사용자 제공 **실기업 정의서 4 xlsx** (FA 회계 / BG 예산 / CI 신용정보 / CM 공통, 257 req)
- **보안 처리**: 정규식 8종 익명화(회사·인명·사번·연락처·외부파트너사·일자·URL·이메일), `local-only` 분리, GitHub commit 0, 4회 leak 검사
- v2.1.1 평가: 93.4% smell 검출 (S2 91%, S5 81%)
- 모듈별 차별화 — FA 약한의무 44건, CI 미정의약어 19건, CM 가장 깨끗

### Step 8. 정밀화 사이클 (v2.2 → v2.3)
- D4 정성 분석 → ChunkDetector 3 fix (short bullet 스킵 / 목적조사 인정 / 양식 파이프 분리)
- **v2.2**: D4 93.4% → 77.0% (-16.4 ppt)
- 자동 likely-FP 26% → 3.9% (-22 ppt)
- **v2.3**: kiwipiepy(Kiwi C++) 본격 통합 → 세종 POS 태그셋 활용 → S4 약한의무 정확도 향상

### Step 9. LLM·문서·휴리스틱 (v2.4 → v2.5)
- **v2.4**: Anthropic Claude 어댑터 (`claude-opus-4-7`, API 키 없을 때 dry-run), PDF 번들 6 문서 통합 (2.7 MB)
- **v2.5**: LLM 없이 작동하는 휴리스틱 교정 (`[명세 필요: ...]` 마커), 4방식 baseline 비교

### Step 10. RQ3 결정적 답 도출
- R1_sim 50건 gold 기준 4 방식 비교
- **Rule-only가 최선** (Macro 0.28, Micro 0.84) — NLP·Ensemble은 과검출
- 한국 RFP 도메인은 휴리스틱이 효율적, NLP 통합 효과 제한적

### Step 11. v2.6 한국어 패턴 고도화 + 표준 갭 분석
- `kofinre/korean_patterns.py` 모듈 신설 — 종결 5분류 / 격조사 / 번역체 / 부사·접속 등 사전화
- MorphDetector (kiwipiepy) 정밀 활용, RegexDetector 한국어 특화 확장
- **`STANDARDS_COMPARISON.md`** (현재 `old/`) — IEEE 830 / ISO 29148 / INCOSE / EARS ↔ S1~S10 매핑
- 결과: KoFinRe S1~S10은 표준 18+ 기준의 **약 28%** 커버 → 8종 신규 smell 후보 도출

### Step 12. v2.7 Smell 10 → 15 확장 (ISO/INCOSE/EARS)
- **S11 구현편향** (ISO 29148 Implementation-free)
- **S12 부정문** (INCOSE Positive form)
- **S13 추측표현** (INCOSE Speculative)
- **S14 수혜자불명** (EARS / IEEE 830)
- **S15 지시어모호** (INCOSE Pronoun)
- 단위 테스트 16건 신규 — 모두 통과
- 표준 커버리지: 28% → **55%**

### Step 13. v2.8 Smell 15 → 19 확장 (CMMI + NCS)
- 사용자가 제공한 **CMMI 9 원칙** + **NCS 5 제약 카테고리** 표 검증·보완 요청
- `CMMI_NCS_COMPARISON.md` 11-섹션 분석 → 4종 신규 도출
- **S16 필요성불명확** (CMMI REQM Necessary)
- **S17 실현불가** (CMMI RD Feasible — 100% 가용성·0초·완벽한 등)
- **S18 추적ID부재** (CMMI REQM Traceable — 의무문 + ID/출처 동시 부재)
- **S19 제약카테고리불명** (NCS 5 카테고리 TECH/BIZ/COMP/OPS/SEC 분류 보조)
- 단위 테스트 18건 신규 — 모두 통과
- CMMI 5/9 → **8/9**, NCS 0/5 → **5/5**, 전체 커버리지 55% → **~70%**
- `PAPER_FINAL.md` v2.8 통합본 재작성, smell_taxonomy.yaml v2.0/10 → v2.8/19

---

## 3. 핵심 결과

### 3.1 Smell Taxonomy 진화

| 버전 | Smell 수 | 변화 | 표준 커버리지 |
|---|---:|---|---:|
| v1.0 | 7 | Paska 9 → 한국 매핑 | ~20% |
| v2.0 | **10** | S2 Incomplete, S8 Coord Amb 분리, S10 Unverifiable 신규 | ~28% |
| v2.6 | 10 | korean_patterns 모듈 (재구조화) | 28% |
| v2.7 | **15** | S11~S15 (ISO/INCOSE/EARS) | **55%** |
| **v2.8** | **19** | **S16~S19 (CMMI REQM/RD + NCS 5 카테고리)** | **~70%** |

### 3.2 Detector 아키텍처 진화

| 버전 | Detector | 비고 |
|---|---|---|
| v1.0 | RegexDetector 단독 | 정규식 |
| v2.0 | 5종 골격 | regex / morph / chunk / dictionary / llm |
| v2.3 | morph 본격 (kiwipiepy) | Kiwi C++ 엔진, Java 불필요 |
| v2.4 | LLM 실 어댑터 (Anthropic) | dry-run fallback |
| v2.5 | + 휴리스틱 교정 | LLM 없이도 작동 |
| v2.6 | korean_patterns 모듈화 | 종결·격조사·번역체 사전 |
| v2.7 | S11~S15 regex 확장 | ISO/INCOSE/EARS 정렬 |
| **v2.8** | **S16~S19 regex + NCS 사전** | **CMMI REQM/RD + NCS 5 카테고리** |

### 3.3 데이터셋 4종

| 코드 | 데이터셋 | 출처 | 결과 (v2.5) |
|---|---|---|---|
| **D1** | 공공금융 RFP 56건 (비정제) | 12개 기관 공식 게시판 | 94.1% smell |
| **D2** | REQ_abstract 30 (정형) | 사용자 제공 정제 CSV | 56.7% smell |
| **D3** | PURE 영문 79건 | 공개 데이터셋 | 46.6% smell (Paska 기준선) |
| **D4** | **실기업 4모듈 257건** | **익명화 — 로컬 only** | **77.0% (v2.2)·79.4% (v2.3)** |

### 3.4 D4 ablation study (v2.1.1 → v2.5)

| Smell | v2.1.1 | v2.2 | v2.3 | 누적 Δ |
|---|---:|---:|---:|---:|
| 전체 Smell 비율 | 93.4% | 77.0% | 79.4% | -14 ppt |
| **자동 likely FP** | **26%** | — | **3.9%** | **-22 ppt** ⭐ |
| S2 불완전 | 235 | 181 | 181 | -54 |
| S5 주체누락 | 209 | 159 | 161 | -48 |
| S4 약한의무 | 58 | 58 | 113 | +55 (정확도 ↑) |

### 3.5 4 방식 Baseline 비교 (R1_sim 50건 gold, v2.5)

| 방식 | Macro-F1 | Micro-F1 | 검출량 |
|---|---:|---:|---:|
| **Rule-only** | **0.278** | **0.837** | 21/50 (42%) |
| NLP-only (kiwipiepy + chunk) | 0.060 | 0.182 | 48/50 (96%) |
| LLM-assisted (Rule + LLM dry-run) | 0.278 | 0.837 | 21/50 (42%) |
| Ensemble (5 detector, rule-priority) | 0.244 | 0.254 | 50/50 (100%) |

→ **RQ3 답**: 한국 RFP 도메인에선 Rule-only 최선

---

## 4. 핵심 발견 (Insights)

### 4.1 언어·문화 차이
- 영문 SRS — Passive voice 27.5% 우세 (D3)
- 한국 RFP — **주체누락 31~81% / 약한의무 0~30% / 어휘모호 4~31%** 우세
- **한국어 SOV 어순 + 주어 생략 허용** 의 구조적 영향이 정량 확인됨

### 4.2 정제 효과의 정량화 (RQ4)
- D1 비정제 — 65.3% smell
- D2 정형 — 56.7% smell
- **D4 실기업 정제 양식 — 93.4% (S2 91%, S5 81%)**
- 잘 정비된 산출물도 한국 SI 관행적 작성 패턴 (주어 생략·평서형 종결) 그대로 따름
- **RQ4 결정적 답**: 한국 RFP 품질 이슈는 정제 수준이 아니라 **언어·문화적 작성 관행** 자체

### 4.3 도메인 특화 발견
- **FA(회계)** — 약한의무 44건 ("처리한다" 평서형 다수)
- **CI(신용정보)** — 미정의 약어 19건 (도메인 약어 다수)
- **CM(공통)** — 가장 깨끗 (표준 템플릿 효과)
- **AML(D2)** — 100% smell, 규제 컴플라이언스 위험 신호

### 4.4 "실시간" 함정
- 모호어 Top 1 — D2 8회, D4 다수
- RFP 표준 표현으로 자주 쓰이지만 응답시간 SLO 미명시
- 검수·납품 단계 분쟁 위험

### 4.5 휴리스틱의 효율성 (RQ3)
- 한국어 공공조달·실기업 RFP는 정형 표현이 명확
- 정규식 휴리스틱이 NLP·LLM·앙상블보다 균형 우수 (Macro 0.28)
- NLP/Ensemble의 OR 결합은 과검출 → 정밀도 손실
- 의미 분석이 진짜 필요한 영역은 도메인 외 일반화

### 4.6 보안·법적 처리의 일반화 가능성
- 익명화 정규식 8종 + LOCAL_ONLY 격리 + 4 leak 검사 + 통계만 외부
- 후속 한국어 요구공학 연구의 표준 워크플로우 제안

---

## 5. 산출물 카탈로그

### 5.1 코드 (59 파일, 1,900+ LoC)

| 영역 | 위치 |
|---|---|
| 핵심 패키지 | `kofinre/` (50 파일) |
| Detector | `kofinre/detectors/` (regex / morph / chunk / dictionary / llm) |
| 추출 파이프라인 | `kofinre/extraction/` (signatures / document / sentence / requirement) |
| 교정 | `kofinre/correction.py` (LLM) + `correction_heuristic.py` (정규식) |
| 평가·리포트·검증 | `kofinre/metrics.py` + `reporting.py` + `validation.py` |
| LLM 어댑터 | `kofinre/llm_adapters/anthropic_caller.py` |
| 앙상블 | `kofinre/ensemble.py` (3 voting) |
| 입출력 | `kofinre/io/` (csv_loader / excel_writer) |
| CLI | `scripts/` (extraction / detection / baselines / gold / pdf) |
| 예제 | `examples/` (basic / req_abstract / heuristic / llm / gold preview) |
| 단위 테스트 | `tests/` (detectors / metrics) |
| 레거시 | `legacy/` (v1 보관) |

### 5.2 문서 (활성 7종 + PDF 번들 + old 3종)

| 위치 | 문서 | 용도 | 시점 |
|---|---|---|---|
| `docs/` | `PAPER_FINAL.md` | MECE 학술 최종본 (19종) | **v2.8** |
| `docs/` | `CMMI_NCS_COMPARISON.md` | CMMI 9 원칙 + NCS 5 카테고리 분석 | v2.8 |
| `docs/` | `JOURNEY.md` | 본 문서 | v2.8 |
| `docs/` | `UPDATE.MD` | Changelog | v1.0~v2.8 |
| `docs/` | `EXTRACTION_RULES.md` | 추출·필터 규칙 | v2.x |
| `docs/` | `PASKA_KOREAN_ADAPTATION.md` | Paska 원본 대비 | v2.x |
| `docs/` | `IMPROVEMENT_RECOMMENDATIONS.md` | 3계층 권고 | v2.x |
| `old/` | `PAPER_DRAFT.md` | 초기 학술 정리본 (10종) | v2.1 시점 |
| `old/` | `FRAMEWORK_GAP_ANALYSIS.md` | 논문 vs 구현 갭 분석 | v2.0 시점 |
| `old/` | `STANDARDS_COMPARISON.md` | IEEE/ISO/INCOSE/EARS 갭 (S11~S18 제안) | v2.7 시점 |
| **PDF 번들** | `dist/KoFinRe_v2.8.pdf` | 활성 문서 통합 | v2.8 |

### 5.3 데이터셋 (D1~D4)

| 코드 | 위치 | 공개 가능성 |
|---|---|---|
| D1 RFP 56건 | `RFP_자료_56건.zip` 백업 | ⚠️ 공공 게시물 기반 |
| D2 REQ_abstract 30 | `assist_scripts_and_results.zip` | ✅ 정제·공개 가능 |
| D3 PURE 79건 | 공개 데이터셋 | ✅ |
| **D4 실기업 257건** | **`real_reqs_anonymized_LOCAL_ONLY.zip`** | 🔒 **로컬 only** |

### 5.4 백업 (3회)

| 시점 | 위치 | 크기 |
|---|---|---:|
| 10:55 | `KoFinRe_backup_20260612_105510/` | 178 MB |
| 16:11 | `KoFinRe_backup_20260612_161108/` | 274 KB |
| 16:19 | `KoFinRe_backup_20260612_161935/` | 5.6 MB |

---

## 6. GitHub 저장소 통계

- **URL**: <https://github.com/24nga/KoFinRe>
- **Commit**: 15+개 (v1.0 → v2.8)
- **트래킹 파일**: 70+
- **버전 이력**: 1.0 → 1.0.1 → 1.0.2 → 2.0 → 2.1 → 2.1.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.5.1 → 2.6 → 2.6.1 → 2.7 → **2.8**
- **leak 검사**: 7회+ 모두 통과 (실기업 식별자 0)

---

## 7. 배운 점·한계·향후

### 배운 점
1. **도메인 정형 표현이 명확한 영역은 휴리스틱이 효율** — NLP·LLM이 과한 도구일 수 있음
2. **익명화·격리 워크플로우**가 실기업 데이터 연구의 핵심 — 정규식 + LOCAL_ONLY + leak 검사 3중 안전망
3. **양식 자체에 대한 fix가 큰 효과** — D4 양식 `|` 구분자 인식만으로 -16 ppt
4. **kiwipiepy(Kiwi C++)** 는 KoNLPy 대안으로 가벼움 — Java 불필요·pip 한 줄

### 한계
- D4 표본 197건 → **실제 사람 평가자 200건 작성은 미완료**
- R1_sim 자체가 휴리스틱이라 Rule-only에 유리한 편향 가능
- LLM 어댑터는 dry-run만 검증 — 실제 ANTHROPIC_API_KEY로 Stage 5 교정 시연 미진행
- 4 데이터셋 모두 한국 금융 도메인 — 타 도메인 일반화 미검증
- 영문 약어 화이트리스트 edge case 1개 (단위 테스트 1/12 실패)

### 후속 (v2.9+)
- **v2.9 S20 Consistency** — 의미 임베딩 기반 요구사항 간 충돌 탐지 → CMMI 9/9 완전 충족
- **v3.0 S21 EARS Pattern Advisor** — Ubiquitous/Event/State/Optional/Unwanted 패턴 권장 → 전체 표준 ~80%
- 실제 사람 평가자 200건 작성 → Cohen's kappa + 진짜 P/R/F1
- ANTHROPIC_API_KEY 설정 후 Stage 5 LLM 교정 실제 호출
- confidence_weighted ensemble 시도
- DOCX 정의서 자동 처리, 도메인별 템플릿 권장 시스템
- Rimay 한국어 패턴 정립 (Paska 코어 기능 한국어화)
- 산업계 협력 기반 한국어 RFP 정답셋 1,000건+ 구축

---

## 8. 핵심 메시지

1. **영문 NLP 도구의 한국어 어댑테이션 가능성 입증** — NLP 의존성 제거하고도 같은 수준 분석 가능
2. **한국 RFP 특유 품질 패턴 정량 확인** — 주체누락·약한의무·어휘모호가 영문과 다른 우세 패턴
3. **잘 정비된 실기업 산출물도 작성 관행 한계 노출** — 도구가 아니라 **작성자 교육·표준화**가 핵심
4. **휴리스틱이 한국 도메인에선 효율적** — NLP·앙상블 통합 효과 제한적 (RQ3 답)
5. **실기업 데이터 윤리·법적 처리의 5단계 표준 워크플로우** 제안 (후속 연구 재사용 가능)

---

> 본 문서는 본 저장소의 history·UPDATE.MD·PAPER_FINAL.md 와 함께 봐주세요.
> 자세한 변경 이력: [`UPDATE.MD`](./UPDATE.MD)
> 학술 정리 (v2.8 19종 최종본): [`PAPER_FINAL.md`](./PAPER_FINAL.md)
> CMMI/NCS 표준 정렬 분석: [`CMMI_NCS_COMPARISON.md`](./CMMI_NCS_COMPARISON.md)
> 개선 권고: [`IMPROVEMENT_RECOMMENDATIONS.md`](./IMPROVEMENT_RECOMMENDATIONS.md)
> 시점별 historical 문서: [`../old/`](../old/)
