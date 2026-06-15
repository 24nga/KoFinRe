# old/ — 시점별 historical 문서 보관소

본 폴더는 **이전 버전 시점에서 정확했던 문서**를 그대로 보존합니다. v2.8 활성 문서는 [`../docs/`](../docs/)에 있습니다.

## 보관 문서

| 파일 | 기준 시점 | 후속 (v2.8 활성) |
|---|---|---|
| `PAPER_DRAFT.md` | v2.1 시점 학술 정리본 (10종) | [`../docs/PAPER_FINAL.md`](../docs/PAPER_FINAL.md) — v2.8 MECE 최종본 (19종) |
| `FRAMEWORK_GAP_ANALYSIS.md` | v2.0 시점 논문 vs 구현 갭 (7종 → 10종 전환) | (반영 완료 — 별도 후속 없음) |
| `STANDARDS_COMPARISON.md` | v2.7 시점 IEEE/ISO/INCOSE/EARS 갭 분석 (S1~S10 → S11~S18 제안) | [`../docs/CMMI_NCS_COMPARISON.md`](../docs/CMMI_NCS_COMPARISON.md) — v2.8 CMMI/NCS 후속 |

## 왜 삭제하지 않는가

- **재현성**: 과거 commit 시점의 분석 결과를 인용한 문서와의 정합성 유지
- **여정 추적**: [`../docs/JOURNEY.md`](../docs/JOURNEY.md)에서 시점별 분석을 그대로 인용 가능
- **연구 윤리**: 발표·심사 과정에서 시점별 매핑이 변경되었다는 사실을 투명하게 노출

## 사용 주의

- 본 폴더 문서의 **smell 수·표준 커버리지·로드맵 표는 모두 이전 시점의 정보**입니다
- 현재 상태가 궁금하면 항상 [`../docs/PAPER_FINAL.md`](../docs/PAPER_FINAL.md)를 우선 참조하세요
- 본 폴더 문서를 인용할 땐 반드시 "v2.x 시점" 명시 필요
