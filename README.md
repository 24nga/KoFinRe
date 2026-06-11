# 한국어 RFP 요구사항 추출·평가 도구

공공금융기관 RFP 공고문에서 한국어 요구사항을 자동 추출하고 품질(Smell)을 평가합니다.
원본 [Paska](https://github.com/lu-cs-sv/Paska) (영문 전용)의 한국어 RFP 대응판.

## 무엇을 하나

1. **추출 (Extract)** — 공고 HTML / HWP / PDF / RTF에서 텍스트 뽑기
2. **필터 (Filter)** — 한국어 요구사항만 골라내기 (규칙 기반)
3. **검사 (Smell)** — 7가지 품질 문제 패턴 매칭
4. **리포트 (Report)** — CSV / Markdown / Excel 출력

규칙 본문: [`EXTRACTION_RULES.md`](./EXTRACTION_RULES.md)
변경 이력: [`UPDATE.MD`](./UPDATE.MD)
원본 Paska 대비 변경: [`PASKA_KOREAN_ADAPTATION.md`](./PASKA_KOREAN_ADAPTATION.md)
논문용 정리: [`PAPER_DRAFT.md`](./PAPER_DRAFT.md)

## 디렉토리

```
.
├── README.md                       # 이 파일
├── EXTRACTION_RULES.md             # 추출·평가 규칙 정의
├── UPDATE.MD                       # 변경 이력
├── requirements.txt                # Python 의존성
├── rfp_extract.py                  # 1) HTML/HWP/PDF/RTF 텍스트 추출
├── rfp_smell.py                    # 2) Smell 7종 검사
├── rfp_requirement_filter.py       # 3) 요구사항만 정밀 필터링
├── rfp_excel.py                    # 4) Excel 리포트 (전체 결과)
├── rfp_excel_sentences.py          #    Excel — 분석 문장 원문
├── rfp_excel_requirements.py       #    Excel — 정밀 필터 요구사항
├── req_abstract_eval.py            # 5) REQ_abstract.csv (정형 CSV) 평가
├── req_abstract_excel.py           #    Excel — 정형 CSV 결과
└── download_rfp.py                 # 0) RFP 56건 자동 다운로드 (사전 단계)
```

## 빠른 시작

### 사전 요구사항

- Windows + Python 3.10 이상
- (HWP 처리용) 한컴오피스 2024 설치 — `win32com` COM 자동화 사용
- 의존성:
  ```powershell
  pip install -r requirements.txt
  ```

### 비정형 RFP 공고문에서 추출

```powershell
# 0) RFP 56건 다운로드 (선택 — 새 자료셋이면)
python download_rfp.py

# 1) 텍스트 추출 — HTML/HWP/PDF/RTF 모두 처리
python rfp_extract.py
#  → rfp_extract/<NN>_<기관>_<사업>.txt (56개)

# 2) Smell 1차 (모든 문장에 적용)
python rfp_smell.py
#  → rfp_report/sentences_all.csv (분석된 모든 문장)
#  → rfp_report/smell.csv (검출 문장만)
#  → rfp_report/summary.json

# 3) 진짜 요구사항만 정밀 필터
python rfp_requirement_filter.py
#  → rfp_report/requirements_filtered.csv
#  → rfp_report/requirements_per_project.csv
#  → rfp_report/requirements_per_project_text/<사업>.md

# 4) Excel 리포트
python rfp_excel.py                # 56건 종합
python rfp_excel_sentences.py      # 분석 문장 원문 자동필터
python rfp_excel_requirements.py   # 정밀 필터 요구사항
```

### 정형 CSV(REQ_abstract.csv 형식) 평가

```powershell
python req_abstract_eval.py
#  → rfp_report/req_abstract_eval.csv (req_id 단위)
#  → rfp_report/req_abstract_eval_sub.csv (sub-req 단위)

python req_abstract_excel.py
#  → rfp_report/REQ_abstract_평가결과.xlsx (5시트)
```

## Smell 7종

| 코드 | 의미 | 예시 |
|---|---|---|
| 모호어 | 정량성 결여 | "**적절한** 응답시간을 보장한다" |
| 수동태 | 행위 주체 흐릿 | "보고서는 **생성되어야** 한다" |
| 복합의무 | 한 문장 다중 요구 | "A를 처리**해야 하고** B를 전송**해야** 한다" |
| 정량부재 | 성능 키워드인데 숫자 없음 | "**빠른 응답속도**를 보장한다" |
| 미정의약어 | 정의 없이 등장 | "**AML/CFT** 처리를 위해…" |
| 주체모호 | 주어 없이 의무문 | "매월 정기적으로 보고**한다**" |
| 약한의무 | "한다/된다" 평서형 | "이력 정보를 저장**한다**" |

## 검증 결과 (v1.0)

| 데이터셋 | 입력 | 추출 | Smell 비율 |
|---|---|---|---|
| RFP 56건 자체 추출 | 3,210 문장 | 75건 | 65.3% |
| REQ_abstract 30건 (정형) | 30 req / 140 sub | 30건 | 56.7% |

## 라이선스

MIT (단, 한컴오피스 COM 자동화는 한컴 라이선스 약관 준수 필요)

## 참고

- 원본 영문 도구: [Paska](https://github.com/lu-cs-sv/Paska)
- Stanford POS Tagger: <https://nlp.stanford.edu/software/tagger.shtml>
- 한국어 NLP 참고: [한국어 RFP 품질 평가에 대한 일반 논문](https://www.kci.go.kr) (예시 링크)
