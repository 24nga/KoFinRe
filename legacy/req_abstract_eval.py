"""
REQ_abstract.csv (구조화된 30건 RFP 요구사항) 평가.
- req_details 안의 세미콜론으로 분리된 sub-requirement 단위로 smell 검사
- req_id 단위로 집계 + 전체 통계
- 결과: req_abstract_eval_result.csv + Excel
"""
import csv, re, sys, json
from pathlib import Path
from collections import defaultdict, Counter

SRC = Path(r'C:\Users\heen1\Downloads\RFP요구사항  - REQ_abstract.csv')
OUT_DIR = Path(r'C:\Users\heen1\Desktop\assist\rfp_report')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ───────── Smell 검사기 (기존 rfp_smell.py와 동일 로직) ─────────
SMELL_COLS = ['모호어','수동태','복합의무','정량부재','미정의약어','주체모호','약한의무']

VAGUE_TERMS = [
    '필요한','적절한','적정한','신속한','신속히','신속하게','효율적','효과적','충분한','충분히',
    '원활','원활히','원활한','다양한','다수의','양호한','우수한','적합한','가능한 한',
    '적시','적시에','안정적','안정적인','안정적으로','편리한','편리하게','용이한','용이하게',
    '간편한','간편하게','최적','최적의','최적화','체계적','체계적으로','신뢰성','신뢰성 있는',
    '유연한','유연하게','광범위','광범위한','폭넓은','폭넓게','포괄적','포괄적으로','대규모','대량',
    '대용량','소규모','약간','대체로','추후','향후','주기적','주기적으로','정기적','정기적으로','실시간',
]
PASSIVE_RE  = re.compile(r'(되어야|되어야 한다|되어야 함|될 수 있어야|지원되어야|구현되어야|제공되어야|보장되어야|적용되어야|관리되어야|구축되어야|반영되어야|표시되어야|저장되어야|처리되어야|확보되어야|수행되어야|배포되어야|기록되어야|연계되어야|되도록|됨\.?$|된다\.?$)')
DUTY_RE     = re.compile(r'(해야 한다|하여야 한다|되어야 한다|할 수 있어야|지원해야|구현해야|제공해야|보장해야)')
PERF_KEYS   = re.compile(r'(성능|속도|처리량|응답시간|동시접속|건수|TPS|처리율|용량|대수|초당|분당|시간당)')
NUMBER_RE   = re.compile(r'\d+\s*(개|건|초|분|시간|일|년|GB|MB|TB|만|억|명|건/초|TPS|%)')
ACRONYM_RE  = re.compile(r'\b[A-Z]{2,6}\b')
DEFINED_RE  = re.compile(r'([A-Z]{2,6})\s*[:：]\s*[^,;\n]+|[\(（]\s*([A-Z]{2,6})\s*[\)）]|([A-Z]{2,6})\s*[\(（]')
SUBJECT_RE  = re.compile(r'^[가-힣A-Za-z0-9\s\(\)\[\]\-_]+(가|이|은|는|에서|이며)\s')
WEAK_DUTY_RE   = re.compile(r'(한다|된다|함|됨)[\s\.]*$')
STRONG_DUTY_RE = re.compile(r'(해야 한다|하여야 한다|되어야 한다|필수|반드시|의무)')

WHITELIST = {
    'RFP','ICT','IT','OS','PC','DB','API','UI','UX','AI','ML','ETL','DR','OK','URL','HTTP','HTTPS',
    'JSON','XML','HTML','CSS','JS','SQL','PDF','HWP','SMS','SSO','VPN','LDAP','WAS','WAF','PMO','SI',
    'SW','HW','LAN','WAN','GUI','CLI','CPU','RAM','SSD','HDD','USB','LTS','RPA','NLP','EAI','ESB','MQ',
    'MSA','MOU','SLA','KPI','EOL','EOS','EOD','SoC','GPS','TCP','UDP','IP','RFC','SDK','IDE','BMT','POC',
    'NHN','SK','KT','LG','MS','IBM','HP','AWS','GCP','HF','BOK','HUG','KRX','KIC','KIBO','KDIC','KODIT',
    'KAMCO','KFTC','KSD','VOC','ECOS','CBDC','ARS','SIEM','MES','LLM','GPU',
    'META','PROJECT','CD','CI','CO','KS','KR','KO','DO','OR','OF','BY','NO','ID','VS','PM','AM','PL',
    'TV','UP','PER','HEX','MIN','MAX','SUM','AVG','NPL','EVR','SRA','SRS','BSC','BCP','MFA','PKI',
    'OAUTH','OAUTH2','JWT','REST','SOAP','GRPC','CRUD','HCS','MDM','EDI','HRMS','ERP','SCM','CRM','CMS',
    'PMS','ITSM','ITIL','DEVOPS',
    # 금융 특화
    'CB','NICE','KCB','DSR','DTI','VIN','CMS','PEP','EDD','KYC','STR','CTR','FATF','KOFIU','AML','PB','RM',
    'AUC','KS','ROC','AES','AES256','ETF','ELS','MLOPS','ECOS',
}

def find_vague(s):  return [t for t in VAGUE_TERMS if t in s]
def is_passive(s):  return PASSIVE_RE.search(s) is not None
def is_compound(s): return len(DUTY_RE.findall(s)) >= 2
def missing_quant(s):
    return PERF_KEYS.search(s) is not None and NUMBER_RE.search(s) is None
def is_subject_amb(s):
    return SUBJECT_RE.match(s) is None and DUTY_RE.search(s) is not None
def is_weak_duty(s):
    if WEAK_DUTY_RE.search(s):
        return STRONG_DUTY_RE.search(s) is None and not is_passive(s)
    return False
def undefined_acrs(full_text):
    all_a = set(ACRONYM_RE.findall(full_text))
    defined = set()
    for m in DEFINED_RE.finditer(full_text):
        for g in m.groups():
            if g: defined.add(g)
    return all_a - defined - WHITELIST

# ───────── 데이터 로드 ─────────
rows = list(csv.DictReader(open(SRC, encoding='utf-8-sig')))
print(f'요구사항 행: {len(rows)}')

# req_id 단위 결과
result_rows = []           # 행별(=req_id별) 집계
sub_rows = []              # sub-requirement 별 상세
proj_agg = defaultdict(lambda: dict({'reqs':0,'sub_reqs':0,'with_smell':0}, **{c:0 for c in SMELL_COLS}))
vague_counter = Counter()
acr_counter = Counter()

for r in rows:
    pid = r['project_id']
    pname = r['project_name']
    sname = r['system_name']
    rid = r['req_id']
    title = r['req_title']
    details = r['req_details'] or ''

    # 미정의 약어 — req_details 단위로 추출
    undef = undefined_acrs(details + ' ' + title)
    acr_counter.update(undef)

    # ; 로 분리하여 sub-requirement 단위 검사
    subs = [s.strip() for s in re.split(r'[;；]', details) if s.strip()]
    if not subs:
        subs = [details.strip()]

    req_flags = {c: 0 for c in SMELL_COLS}
    req_smelly_count = 0
    for idx, sub in enumerate(subs, 1):
        flags = {c: 0 for c in SMELL_COLS}
        vh = find_vague(sub)
        if vh:
            flags['모호어'] = 1; vague_counter.update(vh)
        if is_passive(sub):     flags['수동태']   = 1
        if is_compound(sub):    flags['복합의무'] = 1
        if missing_quant(sub):  flags['정량부재'] = 1
        if any(a in sub for a in undef):
            flags['미정의약어'] = 1
        if is_subject_amb(sub): flags['주체모호'] = 1
        if is_weak_duty(sub):   flags['약한의무'] = 1

        any_smell = any(flags[c] for c in SMELL_COLS)
        if any_smell: req_smelly_count += 1
        for c in SMELL_COLS:
            if flags[c]: req_flags[c] = 1  # 요구사항 수준에서 OR 집계

        sub_rows.append({
            'project_id': pid, 'project_name': pname, 'system_name': sname,
            'req_id': rid, 'req_title': title,
            'sub_idx': idx, 'sub_text': sub,
            'has_smell': 1 if any_smell else 0,
            **flags,
            'vague_hits': '|'.join(vh) if vh else '',
        })

    has_any = any(req_flags[c] for c in SMELL_COLS)
    result_rows.append({
        'project_id': pid, 'project_name': pname, 'system_name': sname,
        'req_id': rid, 'req_title': title,
        'sub_count': len(subs), 'sub_smelly_count': req_smelly_count,
        'has_smell': 1 if has_any else 0,
        **req_flags,
        'undefined_acronyms': '|'.join(sorted(undef)) if undef else '',
        'req_details': details,
    })

    # 프로젝트 집계
    proj_agg[pid]['reqs'] += 1
    proj_agg[pid]['sub_reqs'] += len(subs)
    if has_any: proj_agg[pid]['with_smell'] += 1
    for c in SMELL_COLS:
        proj_agg[pid][c] += req_flags[c]

# ───────── 출력 ─────────
# 1) 요구사항 단위 결과 CSV
out1 = OUT_DIR / 'req_abstract_eval.csv'
with open(out1, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(result_rows[0].keys()))
    w.writeheader()
    for r in result_rows: w.writerow(r)

# 2) sub-req 단위
out2 = OUT_DIR / 'req_abstract_eval_sub.csv'
with open(out2, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(sub_rows[0].keys()))
    w.writeheader()
    for r in sub_rows: w.writerow(r)

# 3) 프로젝트별
out3 = OUT_DIR / 'req_abstract_eval_per_project.csv'
with open(out3, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['project_id','요구사항','세부항목','Smell검출','% smelly']+SMELL_COLS)
    for pid, d in sorted(proj_agg.items()):
        pct = round(100*d['with_smell']/d['reqs'],1) if d['reqs'] else 0
        w.writerow([pid, d['reqs'], d['sub_reqs'], d['with_smell'], pct]+[d[c] for c in SMELL_COLS])

# 4) 전체 통계
overall = {c: sum(r[c] for r in result_rows) for c in SMELL_COLS}
overall['total_reqs'] = len(result_rows)
overall['total_sub_reqs'] = len(sub_rows)
overall['total_with_smell'] = sum(1 for r in result_rows if r['has_smell'])
overall['vague_top'] = vague_counter.most_common(20)
overall['undefined_acronym_top'] = acr_counter.most_common(20)
with open(OUT_DIR / 'req_abstract_summary.json', 'w', encoding='utf-8') as f:
    json.dump(overall, f, ensure_ascii=False, indent=2)

# ───────── 콘솔 ─────────
print()
print('=== 전체 통계 ===')
print(f"  요구사항(req_id): {overall['total_reqs']}")
print(f"  세부 항목(sub-req): {overall['total_sub_reqs']}")
print(f"  Smell 있는 요구사항: {overall['total_with_smell']} ({100*overall['total_with_smell']/overall['total_reqs']:.1f}%)")
for c in SMELL_COLS:
    print(f"  {c:<8}  {overall[c]:>3}")

print('\n자주 등장 모호어 Top 10:')
for t,n in vague_counter.most_common(10):
    print(f'  {t:<8} {n}')

print('\n정의 없는 약어 Top 10:')
for t,n in acr_counter.most_common(10):
    print(f'  {t:<10} {n}')

print('\n프로젝트별:')
for pid, d in sorted(proj_agg.items()):
    print(f"  {pid}  reqs={d['reqs']:>2}  sub={d['sub_reqs']:>3}  smell={d['with_smell']:>2}")
