# final/ — 논문 최종 제출 패키지 (Frozen Snapshot)

> **동결일**: 2026-07-06 · **버전**: v2.8.1
> 본 폴더는 제출·심사용 **동결본**입니다. 이후 수정은 `docs/`의 living document에만 반영되며, 본 폴더 파일은 제출 시점 상태를 보존합니다.

## 구성

| 파일 | 역할 |
|---|---|
| **`KoFinRe_Paper_v2.8.1_FINAL.md`** | ⭐ 논문 최종본 (한국어 원본) — 한국어 SW/IT 요구사항 품질 자동 평가 프레임워크 (19종 smell · 5 데이터셋 · 6대 표준 정렬 · 다도메인 검증) |
| **`KoFinRe_Paper_v2.8.1_FINAL_EN.md`** | 🌐 논문 최종본 영문판 (English translation) — 국제 학회/저널 제출용. 한국어 예문은 원문 유지 + 영문 gloss 병기 |
| `DOMAIN_COMPARISON.md` | 보조 자료 A — 금융(D1·D2·D4) vs 공공 다도메인(D5) 직접 비교 (9 섹션) |
| `CMMI_NCS_COMPARISON.md` | 보조 자료 B — CMMI 9 원칙 + NCS 5 제약 카테고리 표준 정렬 분석 (11 섹션) |

## 논문 핵심 요약

- **제안**: 도메인 무관(domain-agnostic) 한국어 요구사항 평가 루브릭 — 19종 smell taxonomy
- **표준 정렬**: IEEE 830 / ISO 29148 / INCOSE / EARS / CMMI REQM·RD / NCS — 커버리지 ~20% → **~70%**
- **검증**: 5 데이터셋 (공공금융 비정제·정형 + 영문 기준선 + 실기업 익명화 + **공공 다도메인 4,075 req**)
- **핵심 발견 1**: 한국어 SI 작성 관행(S5 주체누락 등)은 도메인 무관 일관 — 4/4 데이터셋 Top 3
- **핵심 발견 2**: **양식 정형성 효과(-82pp)가 도메인 변경 효과(+22pp)의 3.7배** — 품질 개선 ROI 1순위는 양식 정형화
- **핵심 발견 3**: Rule-only가 Macro-F1 0.278로 최선 — 한국어 정형 표현엔 휴리스틱이 효율적

## 재현성

- 코드·데이터: <https://github.com/24nga/KoFinRe>
- D5 재현 실험: [`../experiments/rfp_2013_sample/`](../experiments/rfp_2013_sample/)
- 검증: `python -m unittest discover tests` (60/61)

## v2.8.1 검수 이력 (v2.8 통합본 → 최종본)

정합성 검수에서 발견된 12건 반영:
- 사실 오류 5건 — 표준 커버리지 기점(~20%) 통일, taxonomy 산술(6+4+5+4=19) 정정, LLM-assisted dry-run 동률 명시, D1 문장 수 각주, 테스트 수 60/61 갱신
- 문서 부패 4건 — Appendix 트리/링크 갱신, XLSX 포맷 행 추가, Future Work 도메인 갱신
- 분석 보강 3건 — D2 추출 행, S14=0% detector 이슈 정직 보고, D4 버전 명시
