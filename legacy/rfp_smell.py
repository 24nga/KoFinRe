"""
한국어 RFP/요구사항 Smell Detector.
Paska(영문)의 9개 smell에 대응하는 한국어 점검 항목 7개를 정의:

  1. 모호어 (Vague terms)              - 정량성 결여 형용사/부사
  2. 수동태 (Passive voice)             - 행위 주체 흐릿
  3. 복합 의무 (Non-atomic)              - 한 문장에 둘 이상의 shall/must
  4. 정량 부재 (Missing quantification)  - 숫자/단위 없는 성능 요구
  5. 미정의 약어 (Undefined acronym)     - 영문 약어가 정의 없이 등장
  6. 주체 모호 (Subject ambiguity)       - 누가/무엇이 하는지 불명
  7. 약한 의무 (Weak modal)              - "해야 한다" 아닌 "한다/된다"

입력:
  /paska/work/extract/<n>_<org>_<proj>.txt  (혹은 호스트 경로)

출력:
  smell.csv          - 사업 × 문장 단위 검출
  per_project.csv    - 사업별 통계
  per_smell.csv      - smell 유형별 통계
"""
import os, re, csv, json, sys
from pathlib import Path
from collections import defaultdict, Counter

IN_DIR  = Path(os.environ.get('RFP_IN',  r'C:\Users\heen1\Desktop\assist\rfp_extract'))
OUT_DIR = Path(os.environ.get('RFP_OUT', r'C:\Users\heen1\Desktop\assist\rfp_report'))
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ────────────────────────────────────────────────────────────
# 패턴 정의
# ────────────────────────────────────────────────────────────

# 1. 모호어 — 정량성 결여
VAGUE_TERMS = [
    '필요한', '적절한', '적정한', '신속한', '신속히', '신속하게',
    '효율적', '효과적', '충분한', '충분히', '원활', '원활히', '원활한',
    '다양한', '다수의', '양호한', '우수한', '적합한', '가능한 한',
    '적시', '적시에', '안정적', '안정적인', '안정적으로',
    '편리한', '편리하게', '용이한', '용이하게', '간편한', '간편하게',
    '최적', '최적의', '최적화', '체계적', '체계적으로',
    '신뢰성', '신뢰성 있는', '유연한', '유연하게',
    '광범위', '광범위한', '폭넓은', '폭넓게', '포괄적', '포괄적으로',
    '대규모', '대량', '대용량', '소규모', '약간', '대체로',
    '추후', '향후', '주기적', '주기적으로', '정기적', '정기적으로',
    '실시간',
]

# 2. 수동태 어미
PASSIVE_RE = re.compile(
    r'(되어야|되어야 한다|되어야 함|될 수 있어야|지원되어야|구현되어야|'
    r'제공되어야|보장되어야|적용되어야|관리되어야|구축되어야|반영되어야|'
    r'표시되어야|저장되어야|처리되어야|확보되어야|수행되어야|배포되어야|'
    r'기록되어야|연계되어야|되도록|됨\.?$|된다\.?$)'
)

# 3. 복합 의무 (한 문장 내 의무 표현 2회 이상)
DUTY_RE = re.compile(r'(해야 한다|하여야 한다|되어야 한다|할 수 있어야|지원해야|구현해야|제공해야|보장해야)')

# 4. 정량 부재 검사용: 성능/규모 키워드 옆에 숫자가 없으면 의심
PERF_KEYWORDS = re.compile(r'(성능|속도|처리량|응답시간|동시접속|건수|TPS|처리율|용량|대수|초당|분당|시간당)')
NUMBER_RE     = re.compile(r'\d+\s*(개|건|초|분|시간|일|년|GB|MB|TB|만|억|명|건/초|TPS|%)')

# 5. 미정의 약어 — 모든 텍스트 스캔 후 정의되지 않은 영문 약어 후보
# 정의: "약어(원어)" 또는 "원어(약어)" 형태가 같은 문서에 등장
ACRONYM_RE = re.compile(r'\b[A-Z]{2,6}\b')
DEFINED_RE = re.compile(r'([A-Z]{2,6})\s*[:：]\s*[^,;\n]+|[\(（]\s*([A-Z]{2,6})\s*[\)）]|([A-Z]{2,6})\s*[\(（]')

# 6. 주체 모호 — "X가/이/은/는" 주어 없이 의무문 시작
SUBJECT_RE = re.compile(r'^[가-힣A-Za-z0-9\s\(\)\[\]\-_]+(가|이|은|는|에서|이|이며)\s')

# 7. 약한 의무 — 평서형 "한다/된다"인데 의무 표현 없음
WEAK_DUTY_RE = re.compile(r'(한다|된다|함|됨)[\s\.]*$')
STRONG_DUTY_RE = re.compile(r'(해야 한다|하여야 한다|되어야 한다|필수|반드시|의무)')

# 일반 노이즈 라인 패턴 — 분석에서 제외
NOISE_RE = re.compile(
    r'^(목\s*차|목차|작\s*성|개정\s*이력|개정이력|개\s*요|문\s*서\s*정\s*보|개정\s*사항|'
    r'^\d+\s*$|^[-·•▶▪○◇\s]+$|^\s*\d+(\.\d+)*\s*$|페\s*이\s*지|Page \d+|^[가-힣A-Za-z]\.\s|^\s*-\s|첨부)'
)

# ────────────────────────────────────────────────────────────
# 문장 분할 + 필터
# ────────────────────────────────────────────────────────────

def split_sentences(text: str):
    text = re.sub(r'-\s*\n\s*', '', text)              # 하이픈 줄바꿈 결합
    text = re.sub(r'\s+', ' ', text)
    # 한국어 문장 종결 + 영문 마침표
    parts = re.split(r'(?<=[\.!?。])\s+(?=[가-힣A-Z○●▶■◇\(\d])', text)
    return [s.strip() for s in parts if s.strip()]

def is_meaningful(s: str) -> bool:
    if not (10 <= len(s) <= 400): return False
    if NOISE_RE.search(s): return False
    # 한글 비율
    hangul = sum(1 for ch in s if '가' <= ch <= '힣')
    if hangul / len(s) < 0.25: return False  # 한국어 비율 너무 낮으면 제외
    return True

# ────────────────────────────────────────────────────────────
# 검사기
# ────────────────────────────────────────────────────────────

def find_vague(s: str):
    hits = []
    for term in VAGUE_TERMS:
        if term in s:
            hits.append(term)
    return hits

def is_passive(s: str):
    return PASSIVE_RE.search(s) is not None

def is_compound_duty(s: str):
    return len(DUTY_RE.findall(s)) >= 2

def missing_quant(s: str):
    if PERF_KEYWORDS.search(s):
        if not NUMBER_RE.search(s):
            return True
    return False

def is_weak_duty(s: str):
    # 평서형 종결이면서 의무 표현 없음, "shall/must" 류 없음
    if WEAK_DUTY_RE.search(s):
        if not STRONG_DUTY_RE.search(s) and not is_passive(s):
            return True
    return False

def is_subject_ambiguous(s: str):
    return SUBJECT_RE.match(s) is None and DUTY_RE.search(s) is not None

def collect_acronyms(text: str):
    """문서 단위 — 등장 약어 중 정의되지 않은 것 추출"""
    all_acrs = set(ACRONYM_RE.findall(text))
    defined = set()
    for m in DEFINED_RE.finditer(text):
        for g in m.groups():
            if g: defined.add(g)
    WHITELIST = {
        # 일반 ICT
        'RFP','ICT','IT','OS','PC','DB','API','UI','UX','AI','ML','ETL','DR','OK','URL','HTTP','HTTPS',
        'JSON','XML','HTML','CSS','JS','SQL','PDF','HWP','SMS','SSO','VPN','LDAP','WAS','WAF','PMO','SI',
        'SW','HW','LAN','WAN','GUI','CLI','CPU','RAM','SSD','HDD','USB','LTS','RPA','NLP','EAI','ESB','MQ',
        'MSA','MOU','SLA','KPI','EOL','EOS','EOD','SoC','GPS','TCP','UDP','IP','RFC','SDK','IDE','BMT','POC',
        # 기업
        'NHN','SK','KT','LG','MS','IBM','HP','AWS','GCP','HF','BOK','HUG','KRX','KIC','KIBO','KDIC','KODIT',
        'KAMCO','KFTC','KSD','PMO','VOC','ECOS','CBDC','ARS','SIEM','MES','LLM','GPU','CPU',
        # 페이지 메타에서 자주 등장 (URL/마크업 노이즈)
        'META','PROJECT','URL','PDF','HWP','HTML','CD','CI','CD','CO','KS','KR','KO','DO','OR','OF','BY',
        'NO','ID','VS','PM','AM','PL','TV','NO','UP','OK','IS','PER','HEX','MIN','MAX','SUM','AVG',
        # 한국 시스템
        'NPL','EVR','SRA','SRS','BSC','BCP','MFA','PKI','OAUTH','OAUTH2','JWT','REST','SOAP','GRPC','CRUD',
        'HF','HCS','MDM','EDI','HRMS','ERP','SCM','CRM','CMS','PMS','ITSM','ITIL','DEVOPS',
    }
    undefined = all_acrs - defined - WHITELIST
    # 너무 많이 등장하는 영문은 일반 단어 가능성 — 빈도 1-2회만
    counter = Counter(ACRONYM_RE.findall(text))
    return {a for a in undefined if 1 <= counter[a] <= 5}

# ────────────────────────────────────────────────────────────
# 메인
# ────────────────────────────────────────────────────────────

SMELL_COLS = ['모호어','수동태','복합의무','정량부재','미정의약어','주체모호','약한의무']

def main():
    txt_files = sorted(IN_DIR.glob('*.txt'))
    if not txt_files:
        print(f'입력 파일 없음: {IN_DIR}'); sys.exit(1)

    per_proj  = defaultdict(lambda: dict({'sentences': 0, 'with_smell': 0}, **{c: 0 for c in SMELL_COLS}))
    proj_meta = {}  # proj_id -> (org_name, proj_name)
    detail_rows = []  # 검출된 문장 상세
    all_rows = []    # 분석된 모든 문장 (검출 여부 포함) — 원문 보관용
    vague_counter = Counter()
    acr_counter   = Counter()

    for ti, p in enumerate(txt_files, 1):
        text = p.read_text(encoding='utf-8', errors='ignore')
        proj_id = p.stem
        # 첫 행에서 사업명 추출
        first = text.split('\n', 1)[0]
        m = re.match(r'### PROJECT:\s*(.+?)\s*/\s*(.+)', first)
        org_name = m.group(1) if m else ''
        proj_name = m.group(2) if m else proj_id
        proj_meta[proj_id] = (org_name, proj_name)

        undefined_acrs = collect_acronyms(text)
        acr_counter.update(undefined_acrs)

        sentences = split_sentences(text)
        sentences = [s for s in sentences if is_meaningful(s)]

        for s in sentences:
            flags = {c: 0 for c in SMELL_COLS}
            vague_hits = find_vague(s)
            if vague_hits:
                flags['모호어'] = 1
                vague_counter.update(vague_hits)
            if is_passive(s):           flags['수동태']     = 1
            if is_compound_duty(s):     flags['복합의무']   = 1
            if missing_quant(s):        flags['정량부재']   = 1
            # 미정의 약어가 이 문장에 포함되어 있으면
            if any(a in s for a in undefined_acrs):
                flags['미정의약어'] = 1
            if is_subject_ambiguous(s): flags['주체모호']   = 1
            if is_weak_duty(s):         flags['약한의무']   = 1

            per_proj[proj_id]['sentences'] += 1
            has_any = any(flags[c] for c in SMELL_COLS)
            # 모든 문장 기록 (원문 + 검출표시)
            all_rows.append({
                'project_id': proj_id, 'org': org_name, 'project': proj_name,
                'sentence': s,  # 원문 그대로 (자르지 않음)
                'has_smell': 1 if has_any else 0,
                **{c: flags[c] for c in SMELL_COLS},
                'vague_hits': '|'.join(vague_hits) if vague_hits else '',
            })
            if has_any:
                per_proj[proj_id]['with_smell'] += 1
                for c in SMELL_COLS:
                    per_proj[proj_id][c] += flags[c]
                detail_rows.append({
                    'project_id': proj_id, 'org': org_name, 'project': proj_name,
                    'sentence': s[:300],
                    **{c: flags[c] for c in SMELL_COLS},
                    'vague_hits': '|'.join(vague_hits) if vague_hits else '',
                })

        print(f'[{ti:02d}/{len(txt_files)}] {proj_id[:60]:<60} sent={len(sentences):>4} smell={per_proj[proj_id]["with_smell"]:>4}', flush=True)

    # ───── 출력 1: 사업별 통계 CSV ─────
    with open(OUT_DIR / 'per_project.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['project_id','org','project','sentences','with_smell','% smelly'] + SMELL_COLS)
        for pid in sorted(per_proj):
            d = per_proj[pid]
            org, name = proj_meta[pid]
            pct = round(100*d['with_smell']/d['sentences'], 1) if d['sentences'] else 0
            w.writerow([pid, org, name, d['sentences'], d['with_smell'], pct] + [d[c] for c in SMELL_COLS])

    # ───── 출력 2: 검출 문장 상세 CSV ─────
    with open(OUT_DIR / 'smell.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['project_id','org','project','sentence'] + SMELL_COLS + ['vague_hits'])
        w.writeheader()
        for r in detail_rows: w.writerow(r)

    # ───── 출력 2b: 모든 분석 문장 원문 CSV ─────
    with open(OUT_DIR / 'sentences_all.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['project_id','org','project','sentence','has_smell'] + SMELL_COLS + ['vague_hits'])
        w.writeheader()
        for r in all_rows: w.writerow(r)

    # ───── 출력 2c: 사업별 분리된 .md (원문 검토용) ─────
    md_dir = OUT_DIR / 'per_project_text'
    md_dir.mkdir(exist_ok=True)
    grouped = defaultdict(list)
    for r in all_rows: grouped[r['project_id']].append(r)
    for pid, lst in grouped.items():
        org, name = proj_meta[pid]
        with open(md_dir / f'{pid}.md', 'w', encoding='utf-8') as f:
            f.write(f'# {name}\n\n')
            f.write(f'- 기관: {org}\n')
            f.write(f'- 분석 문장: {len(lst)}건\n')
            f.write(f'- Smell 검출: {sum(1 for x in lst if x["has_smell"])}건\n\n')
            f.write('---\n\n')
            for i, r in enumerate(lst, 1):
                tags = [c for c in SMELL_COLS if r[c]]
                tag_str = f"  `[{', '.join(tags)}]`" if tags else ''
                f.write(f'{i}. {r["sentence"]}{tag_str}\n\n')

    # ───── 출력 3: smell 유형별 / 자주 등장하는 모호어·약어 ─────
    overall = {c: sum(d[c] for d in per_proj.values()) for c in SMELL_COLS}
    overall['total_sentences'] = sum(d['sentences'] for d in per_proj.values())
    overall['total_with_smell'] = sum(d['with_smell'] for d in per_proj.values())
    overall['vague_top'] = vague_counter.most_common(20)
    overall['undefined_acronym_top'] = acr_counter.most_common(20)

    with open(OUT_DIR / 'summary.json', 'w', encoding='utf-8') as f:
        json.dump(overall, f, ensure_ascii=False, indent=2)

    print()
    print('=== 전체 통계 ===')
    print(f"  분석 문장:      {overall['total_sentences']}")
    print(f"  smell 검출:     {overall['total_with_smell']} ({100*overall['total_with_smell']/max(overall['total_sentences'],1):.1f}%)")
    for c in SMELL_COLS:
        print(f"  {c:<12} {overall[c]:>5}")
    print()
    print('자주 등장하는 모호어 Top 10:')
    for t, n in vague_counter.most_common(10):
        print(f'  {t:<8} {n}')
    print()
    print('정의 없이 자주 등장하는 약어 Top 10:')
    for a, n in acr_counter.most_common(10):
        print(f'  {a:<10} {n}')

if __name__ == '__main__':
    main()
