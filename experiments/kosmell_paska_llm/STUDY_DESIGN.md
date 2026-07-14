# 연구 설계 — 한국어 요구사항 스멜 도출: Paska 변형 규칙과 상용 LLM의 비교 연구

> **KoSmell 실험** (2026-07 신규 설계)
> 상태: Stage 1 (규칙) 실행 / Stage 2 (LLM) 파이프라인 준비 / Stage 3 (비교) 도구 준비

---

## 1. 연구 배경

- **영미권**: Paska(Veizaga et al.)가 NLP 기반으로 요구사항 스멜 9종을 자동 검출하는 연구를 확립했다.
- **국내**: Paska에 상응하는 한국어 요구사항 스멜 도출 연구는 확인되지 않는다.
- **최근 동향**: AI·LLM을 이용한 요구사항 분석 연구가 활발하다.
- **본 연구**: Paska의 요구사항 스멜 9종과 ISO/IEC/IEEE 29148의 요구사항 작성 원칙을 차용하여
  **한국어 요구사항 스멜을 도출**한다.

## 2. 연구 방법 (3단계)

```
[데이터] 금융권 요구사항정의서 14,278건 (익명화, 공개 불가)
    │
    ├─ Stage 1. Paska 변형 규칙 기반 1차 도출
    │     Paska 9종 + ISO 29148 원칙 → 한국어 스멜 K1~K11 정의
    │     정규식·사전·형태소(kiwipiepy) 규칙으로 전수 검출
    │
    ├─ Stage 2. 상용 LLM 2차 평가
    │     층화 표본 (프로젝트 비례, seed=42)
    │     K-taxonomy 정의를 프롬프트로 제공, 행별 0/1 판정 (JSON)
    │     상용 LLM (Claude / GPT) + 로컬 LLM 대조
    │
    └─ Stage 3. 비교 분석
          스멜별 일치율, Cohen's kappa, McNemar,
          규칙-단독 검출 vs LLM-단독 검출 사례 정성 분석
```

## 3. 한국어 스멜 Taxonomy (K1~K11)

출처를 Paska 9종과 ISO 29148 작성 원칙으로 한정한다. 정의·매핑은 `taxonomy_k.yaml` 참조.

| 코드 | 한국어 스멜 | Paska 원천 | ISO 29148 원칙 |
|---|---|---|---|
| K1 | 복합 요구사항 | Non-atomic | Singular |
| K2 | 불완전 명세 | Incomplete requirement | Complete |
| K3 | 주체·시스템 응답 누락 | Incomplete system response | Complete |
| K4 | 불완전 조건 | Incomplete condition | Complete·Verifiable |
| K5 | 수동 표현 | Passive voice | Unambiguous |
| K6 | 약한 의무 (부정확 동사) | Not precise verb | Verifiable |
| K7 | 결합 범위 모호 | Coordination ambiguity | Unambiguous |
| K8 | 비요구사항 | Not requirement | Necessary·Appropriate |
| K9 | 모호어 | — | Unambiguous |
| K10 | 정량 부재 | — | Verifiable·Measurable |
| K11 | 미정의 약어 | — | Unambiguous·Complete |

> **Paska 'Incorrect order'는 제외**: 영어 Rimay 패턴의 절 순서 규칙(조건→시스템 응답)은
> 한국어 SOV 어순에서 통사적 등가가 성립하지 않아, 한국어 스멜로 재정의가 불가능함을 명시한다.
> K9~K11은 Paska에 직접 대응은 없으나 ISO 29148 원칙(모호성 배제·검증 가능성)에서 파생하며,
> 한국어 작성 관행(수식어 모호·수치 생략·영문 약어 혼용)에서 특히 빈발하는 유형이다.

## 4. 데이터셋

| 항목 | 내용 |
|---|---|
| 원천 | 국내 금융권 SI 프로젝트 9건(2011~2020)의 요구사항정의서 xls/xlsx 140파일 |
| 전처리 | 모듈당 최신 버전 116파일 → 요구사항 행 14,278건 |
| 익명화 | 프로젝트 P-A~P-H 코드화, 기관·인명·벤더 마스킹. 원문·매핑은 로컬 격리 |
| 공개 범위 | **원문 공개 불가** — 본 저장소에는 통계량만 게시 |

## 5. Stage 2 표본 설계

- 전수 14,278건은 LLM 비용·재현성 관점에서 비효율 → **층화 무작위 표본**
- 층화 기준: 프로젝트(P-A~P-H) 비례 배분, 최소 층당 10건 보장
- 표본 크기: 기본 300건 (seed=42) — kappa 추정 정밀도와 비용의 절충
- 동일 표본을 모든 LLM에 적용 (모델 간 비교 가능)

## 6. 비교 지표 (Stage 3)

| 지표 | 용도 |
|---|---|
| 스멜별 % agreement | 전반 일치 수준 |
| Cohen's kappa (스멜별) | 우연 보정 일치도 |
| McNemar 검정 | 규칙 vs LLM 검출 성향의 비대칭성 |
| Rule-only / LLM-only / Both / Neither 4분할 | 정성 분석 표본 추출 프레임 |

## 7. 기여

**한국어 요구사항 작성 시 발생하는 스멜을 Paska·ISO 29148 기반으로 도출**하고,
규칙 기반과 상용 LLM 기반 검출의 일치·불일치 구조를 실기업 대규모 데이터로 정량화한다.

## 8. 파일 구성

| 파일 | 역할 |
|---|---|
| `taxonomy_k.yaml` | K1~K11 정의 + Paska/ISO 매핑 + 구현 매핑 |
| `run_stage1.py` | 규칙 기반 1차 도출 (전수 14,278) |
| `llm_judge.py` | LLM 2차 평가 (층화 표본, 어댑터: Anthropic/OpenAI/Ollama) |
| `compare.py` | Stage 3 비교 (kappa/McNemar/4분할) |
| `stage1_stats.json` 등 | 통계 산출물 (원문 미포함분만 커밋) |
