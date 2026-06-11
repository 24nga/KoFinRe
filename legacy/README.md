# Legacy Scripts (v1.x)

이 폴더의 스크립트는 **v1 시절 사용된 단일 파일 스크립트**입니다.
v2 에서 `kofinre/` 패키지로 재구성되었으니 새 코드는 패키지 사용을 권장합니다.

## 파일별 v2 대응

| v1 스크립트 | v2 위치 |
|---|---|
| `rfp_extract.py` | `kofinre/extraction/document_extractor.py` + `scripts/run_extraction.py` |
| `rfp_smell.py` | `kofinre/detectors/regex_detector.py` |
| `rfp_requirement_filter.py` | `kofinre/extraction/requirement_filter.py` |
| `rfp_excel.py`, `rfp_excel_sentences.py`, `rfp_excel_requirements.py` | `kofinre/io/excel_writer.py` |
| `req_abstract_eval.py` | `examples/req_abstract_demo.py` |
| `req_abstract_excel.py` | `kofinre/io/excel_writer.py` (통합) |
| `download_rfp.py` | (v2.2 예정 — 사이트별 다운로더 분리) |
| `rfp_list.json` | (v2 외부 데이터로 이동) |

## 주의

- v1 스크립트는 **참고용 보존**으로 남깁니다. 신규 작업은 `kofinre/` 사용.
- 새 7→10종 smell taxonomy는 v1에 반영되지 않았습니다.
- v1 산출물 디렉토리 명명(`rfp_extract/`, `rfp_report/`)은 v2 표준(`stage1_extraction/`, `stage3_detection/` 등)으로 바뀌었습니다.
- v1 호환이 필요하면 그대로 실행 가능하지만, 새 기능(앙상블·LLM 교정·평가 지표)은 미지원.
