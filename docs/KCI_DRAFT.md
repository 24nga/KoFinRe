# [KCI 초안] Paska와 ISO/IEC/IEEE 29148 기반 한국어 요구사항 스멜 평가 메트릭 설계 및 공공부문 RFP 적용 검증

> **Design of a Korean Requirement Smell Evaluation Metric Based on Paska and ISO/IEC/IEEE 29148 and Its Application to Public-Sector RFPs**
>
> **문서 상태**: KCI 제출용 초안 v0.1 (2026-07-08)
> **구조 방침**: 메트릭 설계 = 주 기여 / 공공 RFP 적용 = 검증 (주종 구조)
> **⬜ 표시**: 골드라벨링 완료 후 기입할 자리 — 총 7곳. 라벨링 시트는 `scripts/build_gold_rfp2013.py`로 생성.
> **분량 목표**: KCI 10~12쪽 (본 초안은 표 위주 — 산문 전개 시 자연 축약)

---

## 요약 (국문)

자연어로 작성된 요구사항의 품질 결함(requirement smell)을 자동 검출하는 연구는 영문권에서 Paska, PURE 등을 중심으로 발전해 왔으나, 한국어 요구사항에 대해서는 공개 데이터셋·자동 평가 도구·한국어 작성 관행을 반영한 스멜 정의가 모두 부재하다. 본 연구는 Paska의 스멜 분류와 ISO/IEC/IEEE 29148의 요구사항 작성 원칙·제약사항 분류를 한국어 작성 관행(주어 생략, 평서형 종결, 명사 결합 등)에 맞게 통합하여 **19종 한국어 요구사항 스멜 평가 메트릭**을 설계하고, 규칙 기반 자동 검출기로 구현하였다. 제안 메트릭의 타당성은 전문가 골드라벨 200건 대비 검출 성능(⬜ Macro-F1 기입)으로 검증하였고, 유용성은 공공부문 다도메인 RFP 14건에서 추출한 요구사항 4,075건에 적용하여 확인하였다. 적용 결과 추적 ID 부재(69.7%), 불완전(26.2%), 주체 누락(16.6%)이 우세 패턴으로 나타났으며, 특히 동일 데이터 내에서 **문서 형태(정형 XLSX 17.3% vs 비정형 HWP 99~100%)에 따른 차이가 도메인 간 차이보다 3.7배 크다**는 사실을 정량 확인하였다. 본 도구와 공개 데이터셋 실험은 오픈소스로 공개한다.

**주제어**: 요구공학, 요구사항 스멜, 한국어 자연어 처리, ISO/IEC/IEEE 29148, RFP 품질 평가

## Abstract (영문)

Research on automatically detecting quality defects (requirement smells) in natural-language requirements has advanced primarily for English, centered on Paska and PURE; for Korean requirements, however, public datasets, automated assessment tools, and smell definitions reflecting Korean writing conventions are all absent. This study designs a **19-smell evaluation metric for Korean requirements** by integrating Paska's smell taxonomy with the requirement-writing principles and constraint classification of ISO/IEC/IEEE 29148, adapted to Korean writing conventions (subject omission, declarative endings, noun compounding), and implements it as a rule-based automatic detector. The metric's validity is verified against 200 expert gold labels (⬜ report Macro-F1), and its utility is demonstrated by applying it to 4,075 requirements extracted from 14 multi-domain public-sector RFPs. The dominant patterns were Missing Traceability ID (69.7%), Incompleteness (26.2%), and Missing Actor (16.6%); notably, within the same dataset, **the difference by document form (structured XLSX 17.3% vs. unstructured HWP 99–100%) was 3.7 times larger than the difference across domains**. The tool and the public-dataset experiment are released as open source.

**Keywords**: Requirements Engineering, Requirement Smell, Korean NLP, ISO/IEC/IEEE 29148, RFP Quality Assessment

---

## I. 서론

### 1.1 연구 배경 및 문제

SW/IT 사업에서 RFP 단계 요구사항의 품질은 사업 성패와 직결되며, 모호한 표현·불완전한 명세·추적 불가능한 서술은 검수·분쟁의 핵심 원인이다. 영문권에서는 Paska[2]가 9종 요구사항 스멜의 자동 검출을, PURE[1]가 공개 데이터셋을 제공해 왔으나, 이를 한국어에 직접 적용하는 데는 다음 장벽이 있다.

| # | 장벽 | 영향 |
|---|---|---|
| 1 | Paska의 allennlp 의존 — 한국어 미지원 | 도구 작동 불가 |
| 2 | 한국어 SOV 어순·주어 생략 허용 | 영문 검출 규칙 부적합 |
| 3 | 한국 SI 작성 관행 (평서형 "한다", 명사 결합) | 영문 스멜 패턴과 불일치 |
| 4 | HWP 등 한국 고유 문서 포맷 | 표준 추출 도구 부재 |
| 5 | 한국어 요구사항 공개 데이터셋 부재 | 재현·비교 불가 |

### 1.2 연구 질문

- **RQ1 (설계)**: Paska 스멜 분류와 ISO/IEC/IEEE 29148 작성 원칙·제약사항 분류를 한국어 작성 관행에 맞게 어떻게 통합 정의할 수 있는가?
- **RQ2 (타당성)**: 제안 메트릭의 자동 검출기는 전문가 골드라벨 대비 어느 수준의 검출 성능(Precision/Recall/F1)을 보이는가?
- **RQ3 (적용)**: 공공부문 RFP에 적용할 때 어떤 품질 패턴이 나타나며, 문서 형태(정형/비정형)에 따라 어떻게 달라지는가?

### 1.3 기여

1. Paska + ISO 29148 기반 **19종 한국어 요구사항 스멜 평가 메트릭** 정의 (RQ1)
2. 규칙 기반 자동 검출기 구현 및 **전문가 골드라벨 200건 검증** (RQ2)
3. 공공 다도메인 RFP 4,075건 적용 — **문서 형태가 도메인보다 품질에 3.7배 큰 영향**임을 정량 발견 (RQ3)
4. 도구·공개 데이터셋 실험의 오픈소스 공개 (<https://github.com/24nga/KoFinRe>)

---

## II. 관련 연구

### 2.1 요구사항 스멜 자동 검출 (1차 근거 ①)

Paska[2]는 자연어 요구사항에서 9종 스멜(Non-atomic, Incomplete system response, Coordination ambiguity, Passive voice 등)을 constituency parsing 기반으로 검출하고 Rimay 패턴[3]으로 재작성을 권고한다. PURE[1]는 79건의 공개 SRS를 제공하여 영문 연구의 재현 기반이 되었다. 본 연구는 Paska의 스멜 분류를 출발점으로 삼되, 구문 분석 의존을 제거하고 한국어 형태·관행 기반 규칙으로 재정의한다.

### 2.2 ISO/IEC/IEEE 29148 (1차 근거 ②)

ISO/IEC/IEEE 29148:2018[5]은 개별 요구사항의 품질 특성으로 Necessary, Implementation-free, Unambiguous, Consistent, Complete, Singular, Feasible, Traceable, Verifiable의 9특성을 제시하고, 요구사항 유형으로 기능·성능·인터페이스와 함께 **제약사항(constraints)** 을 규정한다. 본 연구 메트릭의 각 스멜은 이 9특성 중 하나 이상의 위반으로 정의된다.

### 2.3 보완 참조 표준

INCOSE 작성 가이드[6]의 결함 항목(Speculative, Pronoun 등), EARS[7]의 작성 패턴, CMMI REQM/RD[8]의 관리 원칙, 그리고 한국 NCS[9]의 제약 분류(기술/사업/법규/운영/보안)를 스멜 유도의 보조 근거로 활용한다.

### 2.4 한국어 요구공학 연구

한국어 NLP 기반 요구사항 분류[10], 생성형 AI 기반 모델 변환[11] 등이 보고되었으나, 한국어 요구사항 스멜의 정의·자동 검출·공개 데이터셋 실험을 통합한 연구는 확인되지 않는다.

---

## III. 한국어 요구사항 스멜 평가 메트릭 (제안)

### 3.1 설계 원칙

1. **표준 유도(standards-derived)**: 모든 스멜은 Paska 스멜 또는 ISO 29148 9특성 위반으로 소급 가능해야 한다
2. **한국어 관행 반영**: 주어 생략·평서형 종결·전각 글머리표·영문 약어 혼용 등 한국 SI 문서 특성을 검출 규칙에 반영한다
3. **형태 기반 검출 가능성**: 구문 분석기 없이 형태소·정규식 수준에서 판정 가능해야 한다 (재현성·속도)

### 3.2 19종 스멜 정의

| Code | 명칭 | ISO 29148 위반 특성 | 1차 근거 | 검출 규칙 요지 |
|---|---|---|---|---|
| S1 | 복합의무 | Singular | Paska Non-atomic | 의무 표현 2회 이상 |
| S2 | 불완전 | Complete | ISO 29148 (한국 SI 양식 특화) | 의무 표현 + 행위·대상 부재 |
| S3 | 모호어 | Unambiguous | Paska + ISO 29148 | 모호어 사전 30+ 매칭 |
| S4 | 약한의무 | Verifiable | ISO 29148 (한국어 평서형 특화) | 평서형 종결 + 의무 표현 부재 |
| S5 | 주체누락 | Complete | Paska Incomplete sys. resp. | 의무문 + 주어/행위자 부재 |
| S6 | 정량부재 | Verifiable | Paska + ISO 29148 | 성능 키워드 + 수치 부재 |
| S7 | 미정의약어 | Traceable | ISO 29148 (한국 약어 관행 특화) | 약어 - 정의 - 화이트리스트 |
| S8 | 범위모호 | Unambiguous | Paska Coord. ambiguity | "및/또는, 등" + 열거 |
| S9 | 수동표현 | Unambiguous | Paska Passive voice | "~되어야 한다" 어미 |
| S10 | 검증불가 | Verifiable | ISO 29148 | 정성 표현 + 측정 기준 부재 |
| S11 | 구현편향 | Implementation-free | ISO 29148 | 특정 기술/제품 강제 |
| S12 | 부정문 | Verifiable | INCOSE (보조) | 부정형 의무 표현 |
| S13 | 추측표현 | Feasible/Verifiable | INCOSE Speculative (보조) | "가능하다면/추후 결정" |
| S14 | 수혜자불명 | Complete | EARS (보조) | 의무문 + 이해관계자 부재 |
| S15 | 지시어모호 | Unambiguous | INCOSE Pronoun (보조) | "해당/상기/그것" 선행어 부재 |
| S16 | 필요성불명확 | Necessary | ISO 29148 + CMMI (보조) | 선호·임의·강제 표지어 |
| S17 | 실현불가 | Feasible | ISO 29148 + CMMI (보조) | "100%/0초/완벽한" 절대치 |
| S18 | 추적ID부재 | Traceable | ISO 29148 + CMMI (보조) | 의무문 + ID·출처 동시 부재 |
| S19 | 제약분류불명 | (제약사항 분류) | ISO 29148 constraints + NCS (보조) | 제약 시그널 + 5분류 사전 0매칭 |

> 19종 전체가 ISO 29148 9특성 또는 제약사항 분류의 위반으로 소급되며, 이 중 10종(S1·S3·S5·S6·S8·S9 직접, S2·S4·S7·S10 변형)은 Paska와 대응된다. 상세 정의·양성/음성 예문은 공개 저장소의 `kofinre/smell_taxonomy.yaml` 참조.

### 3.3 자동 검출기

검출기는 정규식·사전·형태소(kiwipiepy) 기반 규칙으로 구현하였다. 예비 실험에서 규칙 단독(Rule-only)이 형태소·청크 분석기 결합(NLP-only Macro-F1 0.060) 및 5-검출기 앙상블(0.244)보다 우수(0.278)하여, 본 논문의 모든 실험은 Rule-only 구성을 사용한다. 한국어 요구사항의 정형적 표현 관행이 규칙 기반 접근에 유리하게 작용한 것으로 해석된다.

### 3.4 평가 산출물

문장별 19종 스멜 플래그(0/1), 문서별 스멜 밀도, 스멜 유형 분포, 동시 발생 조합을 산출하며, 검출 스멜별 교정 권고 마커(예: S18 → `[ID·출처 필요]`)를 자동 삽입한다.

---

## IV. 실험 설계

### 4.1 데이터셋

| 코드 | 데이터 | 크기 | 역할 | 공개 여부 |
|---|---|---:|---|---|
| **D-MAIN** | 공공부문 다도메인 RFP 사례 (2013 요구사항 상세화 적용 발주) — 의료·법무·식약·U-City·교육·DB구축·조달 등 | 14건 / **4,075 요구사항** (HWP 13 + XLSX 1) | **주 실험** (RQ2 골드라벨 모집단 + RQ3 적용) | ✅ 공개 (`experiments/rfp_2013_sample/`) |
| D-BASE | PURE 영문 SRS | 79건 / 1,200 req 표본 | 영문 대조 기준선 | ✅ 공개 |
| D-PRIV | 국내 금융권 실기업 요구사항정의서 4모듈 | 257 req | 보조 검증 (민간·정형 양식) | 🔒 비공개* |

> \* **D-PRIV 비공개 사유**: 계약상 비밀유지 의무 및 영업비밀 보호 대상 문서로, 8종 식별자(회사·인명·사번·연락처·이메일·URL·일자·협력사) 정규식 익명화를 적용한 후에도 도메인 용어 조합에 의한 재식별 위험이 존재한다. 이에 원문·익명화본 모두 저장소 외부에 격리하고 논문에는 통계량만 제시한다. 연구 재현성은 공개 데이터셋 D-MAIN으로 보장한다.

### 4.2 골드라벨 구축 (RQ2) — ⬜ 진행 예정

| 항목 | 설계 |
|---|---|
| 표본 | D-MAIN 4,075건에서 **층화 무작위 200건** (문서 형태 비례: HWP 167 + XLSX 33, seed=42) |
| 평가자 | 저자 1인 (요구공학 실무 경력 ⬜년 — 기입) |
| 절차 | **블라인드 라벨링** — 도구 판정을 보지 않은 상태에서 19종 각 0/1 판정. 라벨링 가이드(정의·양성/음성 예문) 기반 |
| 평가자 내 신뢰도 | 1차 라벨링 후 **최소 2주 간격**을 두고 200건 중 무작위 50건(seed=43)을 재라벨 → **intra-rater Cohen's kappa** 산출 |
| 산출 지표 | 스멜별 Precision / Recall / F1 + Macro-F1 / Micro-F1 |
| 도구 지원 | `scripts/build_gold_rfp2013.py` — 라벨링 가이드 시트 + 본라벨 200건 + 재라벨 50건 3-시트 Excel 자동 생성 |

**단일 평가자 한계와 방어**: 평가자 간(inter-rater) 신뢰도는 산출 불가하므로, (i) 시차 재라벨에 의한 평가자 내 일관성으로 대체하고, (ii) 라벨링 가이드를 공개하여 제3자 재현이 가능하게 하며, (iii) 제2 평가자 확보를 향후 연구로 명시한다.

### 4.3 적용 실험 (RQ3)

D-MAIN 전체 4,075건에 검출기를 단일 패스로 적용하고, (i) 스멜 유형 분포, (ii) 문서 형태별(정형 XLSX vs 비정형 HWP) 차이, (iii) 도메인 간 차이 대비 형태 간 차이의 상대 크기, (iv) 동시 발생 조합을 분석한다. D-PRIV는 동일 검출기로 평가하여 민간·정형 양식에서의 일관성을 보조 확인한다.

---

## V. 실험 결과

### 5.1 골드라벨 검증 (RQ2) — ⬜ 골드라벨 완료 후 기입

**⬜ 표 V-1. 골드라벨 200건 대비 검출 성능**

| Smell | Precision | Recall | F1 | 비고 |
|---|---:|---:|---:|---|
| S1~S19 각 행 | ⬜ | ⬜ | ⬜ | |
| **Macro-F1** | | | **⬜** | |
| **Micro-F1** | | | **⬜** | |

**⬜ 표 V-2. 평가자 내 신뢰도**

| 항목 | 값 |
|---|---:|
| 재라벨 50건 intra-rater kappa (19종 평균) | ⬜ |
| kappa ≥ 0.61 (substantial) 충족 스멜 수 | ⬜ / 19 |

**⬜ 해석 기입 가이드** (라벨 완료 후):
- F1이 높은 스멜군(예상: S1·S4·S9 등 표층 패턴)과 낮은 스멜군(예상: S2·S5 등 의미 판단 개입)의 구분 → 규칙 기반의 적용 한계선 논의
- Precision 대비 Recall 열세/우세 패턴 → 검출기 보수/공격 성향 진단
- kappa가 낮은 스멜 → 정의 자체의 모호성 재검토 필요 신호

### 5.2 공공부문 RFP 적용 (RQ3)

D-MAIN 4,075건 중 3,567건(**87.5%**)에서 1개 이상 스멜이 검출되었다.

**표 V-3. 스멜 유형 상위 5**

| 순위 | Code | 명칭 | 건수 (비율) | ISO 29148 위반 특성 |
|---|---|---|---:|---|
| 1 | S18 | 추적ID부재 | 2,842 (69.7%) | Traceable |
| 2 | S2 | 불완전 | 1,068 (26.2%) | Complete |
| 3 | S5 | 주체누락 | 675 (16.6%) | Complete |
| 4 | S13 | 추측표현 | 470 (11.5%) | Feasible/Verifiable |
| 5 | S15 | 지시어모호 | 430 (10.6%) | Unambiguous |

영문 기준선(D-BASE)의 우세 스멜이 수동태(27.5%)인 것과 달리, 한국어 공공 RFP에서는 추적성·완전성 계열이 우세하다 — 한국어 SOV 어순·주어 생략 관행과 평면 서술형 문서 작성 관행의 결과로 해석된다.

**표 V-4. 동시 발생 조합 상위 3**

| 조합 | 건수 |
|---|---:|
| S2 불완전 + S13 추측표현 | 447 |
| S15 지시어모호 + S18 추적ID부재 | 421 |
| S2 불완전 + S18 추적ID부재 | 414 |

### 5.3 문서 형태별 차이 (RQ3 핵심)

**표 V-5. 문서 형태별 스멜 비율**

| 문서 형태 | 스멜 비율 |
|---|---:|
| 정형 XLSX (ID·분류·명칭·내용 컬럼 분리) | **17.3%** |
| 비정형 HWP (평면 서술) | 99~100% |

**표 V-6. 효과 크기 비교**

| 비교 축 | 스멜 비율 변화 |
|---|---:|
| 문서 형태 변경 (동일 데이터 내 HWP→XLSX) | **-82pp** |
| 도메인 변경 (금융 비정제→공공 다도메인) | +22pp |
| **형태 효과 / 도메인 효과** | **3.7배** |

→ 한국어 요구사항 품질의 핵심 결정 인자는 도메인이 아니라 **문서 양식의 정형성**이다. 실무 시사점: 발주기관의 품질 개선 1순위 조치는 도메인 특화 검토가 아니라 **ID·분류 체계를 갖춘 정형 양식의 의무화**이다.

### 5.4 비공개 데이터 보조 검증 (D-PRIV)

민간 금융권 정형 양식 257건에서도 완전성 계열(불완전 91%, 주체누락 81%)이 우세하여, 공공 데이터와 일관된 패턴을 보였다(비공개 사유로 통계량만 제시). 정형 양식임에도 셀 내부 서술이 불완전한 사례가 다수로, **양식 정형화는 필요조건이지 충분조건이 아님**을 시사한다.

---

## VI. 논의

### 6.1 RQ별 답

- **RQ1**: Paska 9종 + ISO 29148 9특성·제약분류를 한국어 관행 4특화(평서형·주어생략·약어·양식)와 통합하여 19종 메트릭으로 정의 가능함을 보였다 (§III)
- **RQ2**: ⬜ 골드라벨 검증 결과 요약 기입 — "Macro-F1 ⬜, 표층 패턴 스멜군에서 F1 ⬜ 이상, 의미 판단 스멜군은 ⬜ 수준으로 규칙 기반의 한계선 확인"
- **RQ3**: 추적성·완전성 계열 우세 + 형태 효과가 도메인 효과의 3.7배 — 품질 개선의 지렛대는 양식 정형화

### 6.2 한계

1. **단일 평가자 골드라벨** — intra-rater 일관성으로 대체했으나 inter-rater 신뢰도는 후속 과제
2. D-MAIN이 2013년 발주 사례 — 최신 작성 관행과의 시차 존재 (요구사항 상세화 제도 도입기 사례 분석으로 시점 한정)
3. 스멜 비율의 모수가 데이터셋마다 상이 (필터 통과 후보 기준) — 절대 비교에 주의
4. S14(수혜자불명)의 D-MAIN 0% 검출은 검출기 보정 이슈로 의심 — 정직하게 보고하며 개선 예정

## VII. 결론 및 향후 연구

본 연구는 Paska와 ISO/IEC/IEEE 29148을 1차 근거로 한국어 요구사항 스멜 19종을 정의하고 규칙 기반 검출기로 구현하여, 전문가 골드라벨(⬜ 결과)로 타당성을, 공공 다도메인 RFP 4,075건 적용으로 유용성을 검증하였다. 핵심 발견은 (i) 한국어 요구사항의 우세 결함이 추적성·완전성 계열이라는 점, (ii) 문서 양식 정형성이 도메인보다 3.7배 큰 품질 결정 인자라는 점이다.

향후 연구: ① 제2 평가자 확보 및 inter-rater 신뢰도 산출, ② 스멜 분포를 보존한 **합성 요구사항 데이터셋 구축**(대규모 프로파일링·학습 데이터 확보), ③ 최신(2020년대) 공공 RFP와의 시점 비교, ④ 의미 기반 스멜(요구사항 간 일관성)로의 확장.

---

## 참고문헌 (초안 — 최종 시 KCI 양식 정렬)

[1] A. Ferrari, G. O. Spagnolo, and S. Gnesi, "PURE: A Dataset of Public Requirements Documents," *IEEE RE*, 2017.
[2] A. Veizaga, S. Y. Shin, and L. C. Briand, "Automated Smell Detection and Recommendation in Natural Language Requirements," *IEEE TSE*, 2024.
[3] A. Veizaga et al., "On Systematically Building a Controlled Natural Language for Functional Requirements," *EMSE*, 2021.
[4] IEEE Std 830-1998, "IEEE Recommended Practice for Software Requirements Specifications."
[5] ISO/IEC/IEEE 29148:2018, "Systems and Software Engineering — Requirements Engineering."
[6] INCOSE, "Guide to Writing Requirements," v4.
[7] A. Mavin et al., "Easy Approach to Requirements Syntax (EARS)," *IEEE RE*, 2009.
[8] CMMI Institute, "CMMI for Development V2.0 — REQM/RD," ISACA, 2018.
[9] 한국산업인력공단, "NCS 정보기술 — 요구사항 분석," 2024.
[10] B. S. Cho and S. W. Lee, "A Comparative Study on Requirements Analysis Techniques using NLP and ML," *JKSCI*, 2020.
[11] E. S. Cho, "A Technique for UML-based System Development Using Generative AI," *JKSCI*, 2024.

---

## [부록 — 투고 전 체크리스트 (본문 아님)]

| # | 항목 | 상태 |
|---|---|---|
| 1 | 골드라벨 200건 1차 라벨링 | ⬜ (시트: `results/rfp_2013/gold/gold_labeling_sheet.xlsx`) |
| 2 | 2주 후 재라벨 50건 | ⬜ |
| 3 | P/R/F1 + kappa 산출 → 표 V-1, V-2 기입 | ⬜ (산출 스크립트는 라벨 완료 후 작성) |
| 4 | §5.1 해석·§6.1 RQ2·요약/Abstract의 ⬜ 기입 | ⬜ |
| 5 | 저자 경력 ⬜년 기입 | ⬜ |
| 6 | 대상 학술지 투고 규정(분량·양식·참고문헌 스타일) 정렬 | ⬜ |
| 7 | S14 보정 여부 결정 (보정 시 D-MAIN 재실행 → 표 V-3 갱신) | ⬜ |
