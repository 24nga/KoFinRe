# 요구공학 표준 vs KoFinRe Smell Taxonomy 비교 분석

> KoFinRe S1~S10이 요구공학의 핵심 표준 4종을 얼마나 포괄하는지 매핑하고, **누락된 기준에서 도출한 신규 smell 후보 8종(S11~S18)** 을 제안한다.

대상 표준:
- **IEEE 830-1998** — Recommended Practice for SRS (8 특성)
- **ISO/IEC/IEEE 29148:2018** — 개별 요구사항 9 특성 + 집합 4 특성
- **INCOSE Guide to Writing Requirements (2020)** — 11+ 일반 결함
- **EARS** — Easy Approach to Requirements Syntax (Mavin 2009) 5 패턴

---

## 1. 표준별 정의 기준 정리

### 1.1 IEEE 830 — 좋은 SRS 8 특성
| 특성 | 정의 |
|---|---|
| Correct | 모든 요구사항이 실제 시스템 요구를 반영 |
| **Unambiguous** | 모든 요구사항이 단일 해석 |
| **Complete** | 외부·기능·NFR·제약 모두 포함 |
| **Consistent** | 요구사항 간 충돌 없음 |
| Ranked | 중요도·안정성 등급화 |
| **Verifiable** | 유한 비용으로 검증 가능 |
| Modifiable | 변경 영향도 명시·구조화 |
| **Traceable** | 출처·근거 추적 가능 |

### 1.2 ISO/IEC/IEEE 29148 — 개별 요구사항 9 특성
| 특성 | 정의 |
|---|---|
| **Necessary** | 불필요한 기능·중복 제거 |
| **Implementation-free** | "어떻게"가 아닌 "무엇" |
| **Unambiguous** | 단일 해석 |
| **Consistent** | 충돌 없음 |
| **Complete** | 5W1H 완비 |
| **Singular** | 1 요구사항 = 1 기능 (Atomicity) |
| **Feasible** | 기술·예산·일정 내 실현 가능 |
| **Traceable** | 양방향 추적 |
| **Verifiable** | 검증 방법 정의 가능 |

### 1.3 INCOSE — 일반적 결함 11종 (작성 시 피해야 할 패턴)
| 결함 | 정의 |
|---|---|
| **Ambiguity** | 모호한 단어 |
| **Optionality** | "may", "could" 같은 선택적 표현 |
| **Generality** | 일반화·추상화 표현 |
| **Vagueness** | 측정 불가 형용사 |
| **Subjectivity** | 주관적 평가어 |
| **Negative** | 부정문 ("shall not") |
| **Overspecification** | 구현 방법 명시 |
| **Compound** | 한 문장 다중 요구 |
| **Speculation** | "if possible", "as appropriate" |
| **Persona** | 사용자 페르소나 부재 |
| **Pronoun** | "it", "they" 대명사 모호 |

### 1.4 EARS — 5 패턴 (Mavin 2009)
| 패턴 | 양식 | 한국어 등가 |
|---|---|---|
| Ubiquitous | The `<system>` shall `<response>` | 시스템은 …해야 한다 |
| Event-driven | When `<trigger>`, the system shall `<response>` | …할 때, 시스템은 …해야 한다 |
| Unwanted behavior | If `<trigger>`, then the system shall `<response>` | …하면, 시스템은 …해야 한다 |
| State-driven | While `<state>`, the system shall `<response>` | …하는 동안, 시스템은 …해야 한다 |
| Optional features | Where `<feature included>`, the system shall `<response>` | …가 포함된 경우, … |

---

## 2. 표준별 기준 ↔ KoFinRe S1~S10 매핑표

| 표준 기준 | KoFinRe S1~S10 매핑 | 충족도 | 비고 |
|---|---|---|---|
| **IEEE 830 Unambiguous** | S3 모호어 + S8 범위모호 | ✅ 충족 | 어휘·범위 양쪽 검출 |
| IEEE 830 Complete | S2 불완전 (부분) | ⚠️ 부분 | 개별 문장 5W1H만, 집합 단위 검사 부재 |
| IEEE 830 Consistent | — | ❌ **부재** | 요구사항 간 충돌 검출 부재 |
| IEEE 830 Verifiable | S6 정량부재 + S10 검증불가 | ✅ 충족 | |
| IEEE 830 Modifiable | — | ❌ **부재** | 변경 영향도·구조화 미검사 |
| IEEE 830 Traceable | S7 미정의약어 (부분) | ⚠️ 부분 | 출처·근거 추적 부재 |
| **ISO 29148 Necessary** | — | ❌ **부재** | 중복·불필요 요구사항 식별 미검사 |
| **ISO 29148 Implementation-free** | — | ❌ **부재** | 구현 방법 명시 검출 미실시 |
| ISO 29148 Singular | S1 복합의무 | ✅ 충족 | |
| ISO 29148 Feasible | — | ❌ **부재** | 실현 가능성 평가 미실시 |
| **INCOSE Optionality** | S4 약한의무 (일부) | ⚠️ 부분 | "권장"은 잡으나 "may", "could" 한국어 등가 미정 |
| INCOSE Negative | — | ❌ **부재** | 부정문 검출 미실시 |
| INCOSE Overspecification | — | ❌ **부재** | = Implementation-bias |
| INCOSE Compound | S1 복합의무 | ✅ 충족 | |
| INCOSE Speculation | S3 모호어 (일부) | ⚠️ 부분 | "if possible" 한국어 등가 "가능하면" 미정 |
| INCOSE Persona | — | ❌ **부재** | 사용자·이해관계자 명시 검사 미실시 |
| INCOSE Pronoun | — | ❌ **부재** | 대명사 모호 검출 미실시 (한국어는 생략이 더 흔함) |
| **EARS Patterns** | — | ❌ **부재** | 권장 양식 제안 부재 (Rimay 한국어 등가 미정립) |

### 매핑 통계
- ✅ **충족** (5종): IEEE 830 Unambiguous·Verifiable, ISO Singular, INCOSE Compound, ISO Unambiguous(중복)
- ⚠️ **부분** (4종): Complete, Traceable, Optionality, Speculation
- ❌ **부재** (10종): **Consistent / Modifiable / Necessary / Implementation-free / Feasible / Negative / Overspec / Persona / Pronoun / EARS**

→ KoFinRe S1~S10은 **표준 18+ 기준 중 약 28%만 충족**, 50%+ 미커버

---

## 3. 갭 분석 — 누락된 영역 우선순위

### 카테고리 A: 도구로 검출 가능한 영역 (P0~P2)

| # | 표준 기준 | 한국 RFP 적용성 | 검출 가능성 | 우선순위 |
|---|---|---|---|---|
| 1 | INCOSE Overspecification (구현 명시) | **매우 높음** — Oracle/Java 명시 빈번 | 정규식 사전 매칭 | **P0** |
| 2 | INCOSE Negative (부정문) | 높음 — "차단" 권장이 "~하지 않다"로 작성 | 형태소 부정 | **P0** |
| 3 | INCOSE Speculation (추측) | 중 — "가능하면", "필요시" | 사전 매칭 | **P1** |
| 4 | INCOSE Persona (이해관계자 부재) | 중 — RFP는 발주처 명시 일반 | 사전 매칭 | **P1** |
| 5 | INCOSE Optionality (선택) | 중 — "권장", "권고" (S4 부분 겹침) | 사전 매칭 | **P2** |
| 6 | INCOSE Pronoun (대명사) | 낮음 — 한국어 생략이 더 흔함 (S5와 중복) | 형태소 | P3 |

### 카테고리 B: 문서·집합 단위 분석 필요 (P2~P3)

| # | 표준 기준 | 한국 RFP 적용성 | 검출 난이도 | 우선순위 |
|---|---|---|---|---|
| 7 | IEEE 830 Consistent (요구사항 간 충돌) | 높음 — 한 RFP 안 수백 건 | 의미 분석 필요 | P2 |
| 8 | ISO 29148 Necessary (중복 제거) | 높음 — 사이트 공통 외에도 다수 | 임베딩·클러스터링 | P3 |
| 9 | IEEE 830 Modifiable | 중 — 출처·근거 명시 | 구조 분석 | P3 |
| 10 | ISO 29148 Feasible | 중 — 도메인 지식 필요 | 전문가 검토 | P4 |

### 카테고리 C: 가이드·권장만 가능 (도구 외 영역)

| # | 표준 기준 | 비고 |
|---|---|---|
| EARS Patterns | 한국어 등가 패턴 정립 후 권장만 — 자동 검출 부적합 |

---

## 4. 도출된 신규 smell 후보 (S11~S18)

### S11 Implementation-bias (구현 편향) — **신규 P0**

**정의**: 요구사항이 "무엇"(What)이 아닌 "어떻게"(How)를 명시
**ISO 29148**: Implementation-free 위반 / **INCOSE**: Overspecification

| 검출 패턴 | 예시 |
|---|---|
| 특정 제품·벤더 명시 | "Oracle DB로 구축", "MySQL 사용", "React로 개발" |
| 특정 알고리즘·자료구조 | "B-Tree 인덱스 사용", "Quicksort로 정렬" |
| 특정 프레임워크 | "Spring Boot로 개발", "Django 사용" |

**예외**: 발주처가 표준화한 기술 스택은 제약사항으로 인정 (메타 정보에 명시 시)

### S12 Negative-statement (부정문 권장 회피) — **신규 P0**

**정의**: 긍정적 행동 명세를 권장. "차단", "허용 안 함" 등 능동 표현 권장
**INCOSE**: Negative

| 검출 패턴 | 권장 변환 |
|---|---|
| "~하지 않아야 한다" | "차단해야 한다" |
| "~지원하지 않는다" | "비활성화 상태로 둔다" |
| "사용할 수 없다" | "접근을 거부한다" |

### S13 Speculation (추측·조건부) — **신규 P1**

**정의**: "가능하면", "필요시", "여건이 되면" 같은 추측·조건부 표현
**INCOSE**: Speculation

| 검출 패턴 | 권장 변환 |
|---|---|
| "가능하면" | "다음 조건 시" (조건 명시) |
| "필요시" / "필요한 경우" | "[명세: 조건]" |
| "여건이 되면" | 제거 또는 조건 명시 |
| "if possible" | 동일 |

### S14 Missing-actor-persona (이해관계자 부재) — **신규 P1**

**정의**: 요구사항에 영향 받는 이해관계자(stakeholder) 명시 부재
**INCOSE**: Persona

| 검출 패턴 | 예시 |
|---|---|
| 의무 표현 + 시스템만 명시, 사용자·관리자·발주자 부재 | "시스템은 처리해야 한다" (누구를 위해?) |
| 외부 인터페이스 + 상대 기관 미명시 | "외부기관과 연계한다" (어떤 기관?) |

S5와 차이: S5는 "수행 주체" 부재, S14는 "수혜·이해관계자" 부재.

### S15 Pronoun-ambiguity (대명사·지시어 모호) — **신규 P2**

**정의**: "이", "그", "해당", "본 항목" 등 지시어가 가리키는 대상 모호
**INCOSE**: Pronoun

| 검출 패턴 | 예시 |
|---|---|
| 첫 등장 명사 없이 "해당 시스템" | "해당 시스템은 … 처리한다" |
| 인접 명사 없이 "이/그 기능" | "이 기능은 … 지원한다" |

한국어 특화: 영문 it/they보다 한국어 "해당", "당해", "본 항목" 패턴.

### S16 Modifiability (수정 가능성 부재) — **신규 P3**

**정의**: 변경 시 영향 받는 요구사항·관련 항목 명시 부재
**IEEE 830**: Modifiable

| 검출 패턴 | 권장 |
|---|---|
| 출처·근거 미명시 | "출처: [메뉴얼 §3.2]" 명시 |
| 관련 요구사항 ID 미참조 | "관련: REQ-001, REQ-005" |

### S17 Consistency (요구사항 간 일관성) — **신규 P3** (문서 단위)

**정의**: 한 RFP·정의서 내 요구사항 간 충돌 검출
**IEEE 830 / ISO 29148**: Consistent

| 검출 가능 충돌 |
|---|
| 동일 기능에 다른 정량값 ("응답시간 200ms" vs "500ms") |
| 모순 (필수 vs 선택) |
| 중복 (S11 Necessary와 일부 겹침) |

→ 의미 임베딩·클러스터링 필요. v3.0 후보.

### S18 EARS-non-conformance (EARS 양식 미준수) — **신규 P4** (권장 도구)

**정의**: 5 EARS 패턴 어느 것에도 해당하지 않음
**EARS Mavin 2009**

| 권장 양식 미준수 시 |
|---|
| Ubiquitous: "시스템은 …해야 한다" |
| Event-driven: "…할 때, 시스템은 …" |
| 양식 자동 매칭 — 부재 시 권장 양식 제시 |

검출 아닌 권장 — 작성자에게 EARS 한국어 패턴 추천.

---

## 5. 통합 확장 매트릭스 (현재 + 제안)

| Smell | Quality Attribute | 표준 | 구현 |
|---|---|---|---|
| S1 복합의무 | Atomicity / Singular | IEEE/ISO/INCOSE | ✅ v1.0 |
| S2 불완전 | Completeness | IEEE/ISO | ✅ v2.0 |
| S3 모호어 | Unambiguity | IEEE/ISO/INCOSE | ✅ v1.0 + v2.6 |
| S4 약한의무 | Verifiability | INCOSE Optionality | ✅ v1.0 |
| S5 주체누락 | Completeness | INCOSE Persona (부분) | ✅ v1.0 |
| S6 정량부재 | Testability | IEEE/ISO Verifiable | ✅ v1.0 |
| S7 미정의약어 | Traceability | IEEE/ISO | ✅ v1.0 |
| S8 범위모호 | Unambiguity | INCOSE Ambiguity | ✅ v2.0 |
| S9 수동표현 | Clarity | INCOSE Active voice | ✅ v1.0 |
| S10 검증불가 | Verifiability | IEEE/ISO | ✅ v2.0 |
| **S11 구현 편향** | Implementation-free | **ISO/INCOSE** | 🔜 v2.7 |
| **S12 부정문** | Active voice | **INCOSE Negative** | 🔜 v2.7 |
| **S13 추측 표현** | Necessity / Clarity | **INCOSE Speculation** | 🔜 v2.7 |
| **S14 이해관계자 부재** | Completeness | **INCOSE Persona** | 🔜 v2.7 |
| **S15 지시어 모호** | Unambiguity | **INCOSE Pronoun** | 🔜 v2.8 |
| **S16 수정가능성** | Modifiability | **IEEE 830** | 🔜 v2.8 |
| **S17 일관성** | Consistency | **IEEE/ISO** | 🔜 v3.0 (문서 단위) |
| **S18 EARS 양식** | Singular/Verifiable | **EARS** | 🔜 v3.0 (권장 도구) |

→ S11~S18 추가 시 **18종 smell, 표준 18+ 기준의 약 78% 커버 가능** (현재 28% → +50pp)

---

## 6. 구현 우선순위 매트릭스

| # | Smell | 검출 난이도 | 영향 | 우선순위 |
|---|---|---|---|---|
| S11 구현 편향 | 사전 매칭 (저) | 高 (한국 RFP 특히 빈번) | **P0** |
| S12 부정문 | 형태소 부정 (저) | 中 | **P0** |
| S13 추측 표현 | 사전 매칭 (저) | 中 | **P1** |
| S14 이해관계자 | 사전 매칭 (저) | 中 | **P1** |
| S15 지시어 모호 | 형태소 + 컨텍스트 (중) | 中 | **P2** |
| S16 수정가능성 | 출처 컬럼 검사 (저) | 低 | **P2** |
| S17 일관성 | 임베딩·클러스터링 (高) | 高 | **P3** (v3.0) |
| S18 EARS 양식 | 패턴 매칭 + 권장 (중) | 低 (권장만) | **P4** |

---

## 7. 신규 5종 (S11~S15) 검출 사전 (구현 가이드)

### S11 Implementation-bias 사전 (예시)

```python
IMPL_BIAS_DB = {'Oracle','MySQL','PostgreSQL','MongoDB','MS-SQL','MariaDB','DB2'}
IMPL_BIAS_FRAMEWORK = {'Spring','Django','React','Vue','Angular','Express'}
IMPL_BIAS_LANGUAGE = {'Java','Python','C#','Go','Rust','JavaScript'}
IMPL_BIAS_ALGO = {'B-Tree','Quicksort','MergeSort','RSA','AES','SHA-256'}
# 사용 예: "Oracle DB로 구축" → S11
```

### S12 Negative-statement 패턴

```python
NEG_PATTERN = re.compile(
    r'(?:'
    r'하지\s*않아야\s*한다|하지\s*않도록|지원하지\s*않는다|사용할\s*수\s*없다'
    r'|허용하지\s*않는다|제공하지\s*않는다|반영하지\s*않는다'
    r')'
)
```

### S13 Speculation 패턴

```python
SPECULATION = {
    '가능하면', '필요시', '필요한 경우', '여건이 되면', '여유가 있으면',
    '추후 검토', '추후 결정', '협의 후', '판단에 따라', '재량으로'
}
```

### S14 Missing-actor-persona

```python
# S5는 "수행 주체", S14는 "수혜·이해관계자"
# 의무 표현 + 시스템 주체 명시 + 이해관계자(사용자/고객/관리자/발주처) 부재
STAKEHOLDER = {'사용자', '고객', '관리자', '운영자', '발주처', '제안사', '이용자',
               '회원', '가입자', '담당자', '책임자'}
```

### S15 Pronoun-ambiguity

```python
PRONOUN_DEMONSTRATIVE = re.compile(
    r'(?:해당|당해|이|그|본\s*항목|이\s*기능|그\s*기능|동\s*시스템)\s+[가-힣]+'
)
# 단, 같은 문장 안에 가리키는 대상이 명확히 있으면 false
```

---

## 8. 결론

### 현 상태
- KoFinRe S1~S10은 IEEE 830·ISO 29148·INCOSE·EARS의 **약 28%** 커버
- 한국 RFP 특유 패턴(주체 생략·평서형 종결·번역체)은 잘 잡지만 **국제 표준의 절반 이상이 누락**

### 제안
**v2.7 단기 (P0~P1)**:
- S11 Implementation-bias (P0 — Oracle/Java 등 명시)
- S12 Negative-statement (P0 — 부정문 권장 변환)
- S13 Speculation (P1 — "가능하면" 등)
- S14 Missing-actor-persona (P1 — 이해관계자 명시)

**v2.8 중기 (P2)**:
- S15 Pronoun-ambiguity (한국어 "해당", "본 항목")
- S16 Modifiability (출처·근거 명시)

**v3.0 장기 (P3~P4, 문서 단위)**:
- S17 Consistency (의미 임베딩 기반)
- S18 EARS-non-conformance (권장 도구)

### 기대 효과
| 지표 | 현재 (S1~S10) | 제안 후 (S1~S18) |
|---|---:|---:|
| 표준 커버리지 | 28% | **78%** (+50 pp) |
| 검출 영역 수 | 10 | 18 |
| IEEE 830 8 특성 커버 | 5/8 | 7/8 (Modifiable 추가) |
| ISO 29148 9 특성 커버 | 5/9 | 8/9 (Necessary/Impl-free 추가) |
| INCOSE 11 결함 커버 | 4/11 | 9/11 |
| EARS 패턴 권장 | ❌ | ✅ 권장 도구 |

→ KoFinRe는 한국어 도메인 특화 도구에서 **국제 표준 준수 종합 평가 도구**로 격상 가능

---

## 9. 참고

- [`PAPER_FINAL.md`](./PAPER_FINAL.md) §3.3 현재 10종 smell 정의
- [`EXTRACTION_RULES.md`](./EXTRACTION_RULES.md) 현재 검출 규칙
- [`IMPROVEMENT_RECOMMENDATIONS.md`](./IMPROVEMENT_RECOMMENDATIONS.md) 작성자 가이드

표준 원문:
- IEEE Std 830-1998
- ISO/IEC/IEEE 29148:2018
- INCOSE Guide to Writing Requirements (2020)
- Mavin et al., "EARS — Easy Approach to Requirements Syntax" (2009)
