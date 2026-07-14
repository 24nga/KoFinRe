# BASELINE v1 — KoSmell (2026-07-12) 🔒 FROZEN

> **이 폴더는 동결 스냅샷이다. 수정 금지.**
> 이후 모든 개선(프롬프트 보강, API 재실행, 검출기 튜닝)은 `experiments/kosmell_paska_llm/`에서
> 진행하고, 본 baseline 수치와의 delta로 보고한다.

## 기준 커밋

- 소스 커밋: `dfee197` (main, 2026-07-12)
- 동결 대상: 설계·taxonomy·스크립트·전 산출물 (아래 목록)

## 실험 정의

| 요소 | 값 |
|---|---|
| Taxonomy | K1~K11 (Paska 9종 매핑 7 + ISO 29148 파생 3 + K8 비요구사항, Incorrect order 제외) |
| 데이터 | 금융권 요구사항정의서 14,278건 (익명화 P-A~P-H, 원문 비공개) |
| Stage 1 | KoFinRe v2.8 5-detector rule-priority 앙상블 (kiwipiepy 0.20.4) → S코드→K코드 매핑 + K8 휴리스틱 |
| Stage 2 표본 | 층화 무작위 n=300 (프로젝트 비례, seed=42) |
| 상용 LLM | ① Claude (Fable 5) — 대화형 세션 zero-shot ② GPT-4o — OpenAI API, temperature=0 |
| Stage 3 | % agreement, Cohen's kappa, exact McNemar, 2×2 분할 |

## Baseline 수치 요약

**Stage 1 (전수 14,278)**: any-smell **91.4%** — K2 74.4 / K3 59.0 / K11 30.4 / K6 24.0 / K8 21.3 / K9 10.3 / K10 6.4 / K5 6.3 / K7 6.1 / K4 3.8 / K1 1.7 (%)

**Stage 3 핵심**:
- 표층 수렴: 규칙-Claude K6 κ=**0.818**, K9 κ=0.654
- 의미 발산: K2/K3 규칙-LLM κ≈0 (agree ~58%)
- **LLM 간 수렴 (독립 재현)**: Claude-GPT K2 κ=**0.604**, K8 κ=0.602, K7 κ=0.533
- 비대칭: LLM 우세 K1·K7·K3 / 규칙 우세 K11·K10·K4 (McNemar p<.05)
- any-smell: 규칙 91.3% vs Claude 100% vs GPT 99.7%

## 알려진 한계 (v2에서 개선 대상)

1. Claude 판정이 대화형 세션 기반 (temperature 미고정) → API 재실행으로 확정
2. K4 불완전 조건 — 두 LLM 모두 ~0건 (프롬프트 정의 협소)
3. 단일 프롬프트(zero-shot) — few-shot/정의 보강 비교 없음
4. gold label 부재 — 규칙/LLM 어느 쪽이 '옳은지'는 미판정 (일치도만 보고)

## 파일 목록

설계: `STUDY_DESIGN.md`, `taxonomy_k.yaml` / 코드: `run_stage1.py`, `llm_judge.py`, `compare.py`
결과: `stage1_stats.json`, `stage1_labels.csv`, `stage2_labels__*.csv`, `comparison__*.json`, `RESULTS.md`
(원문 문장·표본·캐시는 LOCAL_ONLY — 저장소 미포함)
