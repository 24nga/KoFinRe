# 실험 — 2013 요구사항 상세화 발주 RFP 사례 (다도메인 공개)

> **D5 데이터셋 / KoFinRe v2.8 19종 평가 재현 패키지**
> 도메인 무관 한국어 요구사항 평가 루브릭의 다도메인 일반화 입증용 샘플.

---

## 데이터 출처

`2013년 요구사항상세화 적용 발주 RFP사례.zip` — 한국 공공 발주 RFP 사례 14건. 의료·법무·식약·교육·DB구축·U-City·유지보수·정보화전략·클라우드·조달 등 **단일 도메인이 아닌 다도메인** 구성. 공개 자료이므로 원본 텍스트도 익명화 불요 (단, 본 저장소에는 추출된 요구사항 후보·통계만 포함하며 원본 HWP/XLSX 바이너리는 제외).

## 데이터 구성 (14건)

| 분류 | 사례 | 포맷 |
|---|---|---|
| **DB구축** | 국가기록원 (2013 국가기록물 정리), 국가보훈처 (독립운동사료 DB) | HWP |
| **SW개발** | 근로복지공단 (통합의료정보), 법무부 인천공항 (바이오정보), 법제처 (국가입법지원), 식약청 (CDISC e-CTD), 한국고용정보원 (차세대 고용보험) | HWP |
| **SW개발** | **조달청 (홈페이지 재구축)** — 정형 요구사항 명세 | **XLSX** |
| **시스템운용** | 산업기술진흥원 (클라우드 시범) | HWP |
| **유지관리** | 대구교육정보연구원, 서울의료원 (통합의료정보 유지) | HWP |
| **정보화전략** | 경상북도개발공사 (U-City), 조달청 (공공조달 데이터) | HWP |

## 처리 결과 요약

| 단계 | 결과 |
|---|---:|
| Stage 1 추출 (HWP × 13 + XLSX × 1) | **문장 후보 10,899 / 요구사항 후보 4,075** (HWP 3,409 + XLSX 666) |
| Stage 3 평가 (RegexDetector v2.8 단독) | **smell 검출 3,567건 / 87.5%** |
| 미정의 영문 약어 | 135종 |

## 핵심 발견

### Top 5 검출 (19종 중)

| 순위 | Code | 한국어 | 건수 | 도입 |
|---|---|---|---:|:-:|
| 1 | **S18** | **추적ID부재** | **2,842 (69.7%)** | **v2.8 신규 (CMMI REQM Traceable)** |
| 2 | S2 | 불완전 | 1,068 (26.2%) | v2.0 한국 특화 |
| 3 | S5 | 주체누락 | 675 (16.6%) | v1.0 Paska |
| 4 | **S13** | **추측표현** | **470 (11.5%)** | **v2.7 (INCOSE Speculative)** |
| 5 | **S15** | **지시어모호** | **430 (10.6%)** | **v2.7 (INCOSE Pronoun)** |

### 양식 정형성 vs 도메인 — 핵심 인사이트

| 문서 유형 | Smell 비율 | 시사 |
|---|---:|---|
| **조달청 홈페이지 XLSX 기능요구** (정형 ID·컬럼 분리) | **17.3%** | 양식 정형성 효과 |
| HWP 본문 평면 텍스트 (13건) | 99~100% | ID·출처 추적 없음 |

→ **같은 D5 내부의 양식 차이가 D1~D5 도메인 간 차이보다 크다.**
   품질 핵심 인자는 도메인이 아니라 **양식 정형성 + ID/출처 추적**.

### Smell 동시 발생 패턴 Top 3

| 조합 | 건수 |
|---|---:|
| S2 불완전 + S13 추측표현 | 447 |
| S15 지시어모호 + S18 추적ID부재 | 421 |
| S2 불완전 + S18 추적ID부재 | 414 |

## 폴더 구조

```
experiments/rfp_2013_sample/
├── README.md                          ← 본 문서
├── stage1/                            ← 추출 단계 산출물
│   ├── extraction_log.json           — 13 HWP 추출 메타
│   ├── sentence_candidates.csv       — 10,899 문장 후보
│   ├── requirement_candidates.csv    — 3,409 요구사항 후보 (HWP)
│   └── xlsx_requirements.csv         — 666 요구사항 (XLSX 정형)
└── stage3/                            ← 평가 단계 산출물
    ├── all_detection.csv             — 4,075 행 × 19 smell 검출
    ├── smell_summary_by_doc.csv      — 문서별 통계
    └── report.md                     — 자동 생성 평가 리포트
```

## 재현 방법

```powershell
# 1. 원본 ZIP 풀기 (CP949 인코딩 주의 — Windows PowerShell 사용)
$dest = "data/rfp_2013"
New-Item -ItemType Directory -Force $dest | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open("<ZIP_경로>", "Read", [System.Text.Encoding]::GetEncoding(949))
foreach ($e in $zip.Entries) {
    $target = Join-Path $dest $e.FullName
    if ($e.FullName.EndsWith("/")) { New-Item -ItemType Directory -Force $target | Out-Null }
    else { [System.IO.Compression.ZipFileExtensions]::ExtractToFile($e, $target, $true) }
}
$zip.Dispose()

# 2. HWP 추출 (한컴오피스 + pywin32 필요)
python scripts/run_extraction.py --input data/rfp_2013/ --output results/rfp_2013/stage1/

# 3. XLSX 정형 요구사항 추출
python scripts/extract_rfp2013_xlsx.py results/rfp_2013/stage1/xlsx_requirements.csv

# 4. v2.8 19종 평가
python scripts/evaluate_rfp2013.py
```

## 의존성

- Python 3.10+
- Windows + 한컴오피스 (HWP 추출용)
- pywin32, openpyxl, kiwipiepy
- 본 KoFinRe 패키지 (`pip install -e .`)

## 평가 방식

- **Detector**: RegexDetector v2.8 단독 (Rule-only baseline — 본 논문 §6.3 RQ3 답 근거)
- **앙상블 미사용**: 단일 패스, 도메인별 별도 튜닝 없음
- **Smell taxonomy**: 19종 (Paska + IEEE 830 + ISO 29148 + INCOSE + EARS + CMMI + NCS)

## 인용

```bibtex
@misc{kofinre_d5_rfp2013,
  title={D5: Multi-domain Korean RFP Sample — 2013 Detailed Requirements Practices},
  author={KoFinRe Project},
  year={2026},
  note={Sample experiment package for the KoFinRe-QA Framework},
  url={https://github.com/24nga/KoFinRe/tree/main/experiments/rfp_2013_sample}
}
```

## 관련 문서

- 본 저장소 메인: [`../../README.md`](../../README.md)
- 학술 최종본 (v2.8 19종): [`../../docs/PAPER_FINAL.md`](../../docs/PAPER_FINAL.md)
- CMMI/NCS 표준 정렬: [`../../docs/CMMI_NCS_COMPARISON.md`](../../docs/CMMI_NCS_COMPARISON.md)
- 전체 여정: [`../../docs/JOURNEY.md`](../../docs/JOURNEY.md)
- 평가 스크립트: [`../../scripts/evaluate_rfp2013.py`](../../scripts/evaluate_rfp2013.py)
- 자동 리포트: [`stage3/report.md`](./stage3/report.md)
