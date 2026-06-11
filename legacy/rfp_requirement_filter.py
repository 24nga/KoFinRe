"""
sentences_all.csv 를 받아 진짜 한국어 요구사항만 골라낸다.
- 요구사항 종결어 / 시스템 명사 강제
- 사이트 푸터 · 메타 · 목차 · 약관 차단
- 중복(사이트 공통 텍스트) 제거
- Smell 분석 다시 적용
"""
import csv, re, json, os, sys
from pathlib import Path
from collections import defaultdict, Counter

ALL_CSV  = Path(r'C:\Users\heen1\Desktop\assist\rfp_report\sentences_all.csv')
OUT_DIR  = Path(r'C:\Users\heen1\Desktop\assist\rfp_report')

# ────────────────── 요구사항 종결어 (필수 중 하나) ──────────────────
# "~여야 한다 / ~여야 함" 형태를 일반화 (어떤 동사든 통과)
# 띄어쓰기 유연: 하여야한다 / 하여야 한다 모두
REQ_END = re.compile(
    r'(?:하|되|이|있)여야\s*(?:한다|함\b|됨\b)'
    r'|해야\s*(?:한다|함\b)'
    r'|할\s*수\s*있어야\s*(?:한다|함)'
    r'|반드시\s+[가-힣]+'
    r'|필수\s*(?:이다|로|적|항목)'
    r'|의무\s*(?:이다|적|로)'
    r'|[가-힣]+토록\s*한다'              # "~되도록 한다", "~지원되도록 한다"
)

# 평가기준 (요구사항 아님 — 제외)
EVAL_RE = re.compile(r'(?:을|를)\s*평가한다|점검한다(?:\s*\.|\s*$)|배점')

# ────────────────── 강한 노이즈 차단 (있으면 컷) ──────────────────
HARD_NOISE = re.compile(
    r'(패밀리사이트|COPYRIGHT|All Rights Reserved|사이트맵|'
    r'페이지로 이동|이전 페이지|다음 페이지|마지막 페이지|처음 페이지|'
    r'용어사전|약관|개인정보처리방침|이용약관|'
    r'부가가치세|부가세 포함|부가세|VAT|'
    r'대표전화|대표\s*FAX|대표\s*Tel|'
    r'사업자등록번호|사업자번호|'
    r'홈페이지\s*주소|이메일\s*주소)',
    re.IGNORECASE
)

# 조달/입찰 표준 문구 — 시스템 요구사항이 아님
BID_NOISE = re.compile(
    r'(입찰자|공동수급체|입찰서|낙찰|청렴계약|'
    r'입찰\s*보증금|하자보수\s*보증금|이행보증|계약보증금|'
    r'조달청|나라장터|수요기관|발주처|공고번호|예가범위|투찰|'
    r'사업자등록증|법인등기부등본|대리인|임직원|이의\s*제기|'
    r'국가계약법|지방계약법|조의\s*2|특수조건|기초금액|예정\s*금액|추정\s*금액|'
    r'적격심사|제안서평가|입찰\s*등록|입찰\s*참여|입찰\s*참가|입찰\s*공고|'
    r'전자입찰|구매결의|입찰\s*설명서|공고서|과업내용서|입찰\s*안내|'
    r'적격심사기준|평가관련|연락처는|휴대폰\s*번호|'
    r'재직증명서|참석자\s*전원|주민등록증|운전면허증|여권|신분증|'
    r'재무현황|당기순이익|자기자본순이익률|순\s*현금흐름|'
    r'법\s*제\s*\d+조|미래창조과학부고시|소프트웨어사업의\s*하도급)'
)

# 줄 시작이 글머리표·로마숫자·번호인 단편
LEADING_NOISE = re.compile(
    r'^(\s*[▶○●◇□■·\-•▪]\s*|'
    r'\s*[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]\s*\.?\s|'
    r'\s*[ㅇㅁ]\s+|'
    r'\s*\d+\s*[\.\)]\s*$|'
    r'\s*\d+\s*-\s*\d+\s*$|'
    r'\s*\[\s*양식|\s*\(\s*양식)'
)

# 문장 시작이 메타데이터 키
META_START = re.compile(
    r'^\s*(사업명|사업\s*기간|사업\s*예산|사업\s*목적|사업\s*개요|사업\s*범위|사업\s*요약|'
    r'추진\s*일정|주요\s*일정|입찰\s*일정|계약\s*방식|선정\s*방식|'
    r'발주\s*기관|발주처|문의처|담당자|연락처|연락\s*처|전화\s*번호|팩스|이메일|주소|'
    r'첨부|별첨|붙임|참고|참조|주\s*[\:\)]|※|'
    r'양식\s*\d|별표\s*\d|기타\s*사항|재무현황|재무\s*상태|구\s*분\s*M|'
    r'I+\s|II+\s|III+\s|IV\s|V\s|VI\s|VII\s|VIII\s|IX\s|X\s)'
)

# 시스템 도메인 명사
SYSTEM_NOUN = re.compile(
    r'(시스템|기능|서비스|모듈|화면|메뉴|데이터|보고서|성능|보안|장애|장비|인프라|'
    r'사용자|관리자|운영자|개발자|이용자|고객|업무\s*담당|발주자|수행사|'
    r'인터페이스|API|UI|UX|DB|네트워크|서버|클라이언트|소프트웨어|하드웨어|'
    r'요구사항|기준|조건|규격|항목|품질|운영|구축|개발|연계|이중화|백업|'
    r'제안사|제안서|용역|사업|구성|배포|아키텍처|클라우드|온프레미스)'
)

# 약관/제도 설명문 (요구사항 아님)
LEGAL_DOMAIN = re.compile(
    r'(임차인|임대인|보증금|채권|법원|배당|이자|손해배상|채무|보증보험|'
    r'상속|배우자|증여|이행청구|반환|소송|제소|민법|약관|규정|시행령)'
)

def normalize(s: str) -> str:
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def is_requirement(s: str) -> bool:
    s = s.strip()
    if not (20 <= len(s) <= 350): return False
    if HARD_NOISE.search(s):  return False
    if BID_NOISE.search(s):   return False  # 입찰·계약·조달 안내 컷
    if LEADING_NOISE.match(s): return False
    if META_START.match(s):   return False
    # 평가기준 — RFP 채점 룰은 요구사항 아님
    if EVAL_RE.search(s):     return False

    # 요구사항 종결어 통과
    if REQ_END.search(s):
        # 약관/제도 설명문은 시스템 명사도 함께 있어야 OK
        if LEGAL_DOMAIN.search(s) and not SYSTEM_NOUN.search(s):
            return False
        return True

    return False

def main():
    rows = list(csv.DictReader(open(ALL_CSV, encoding='utf-8-sig')))
    print(f'입력 문장: {len(rows)}')

    # 1차: 정밀 필터
    filtered = []
    for r in rows:
        s = normalize(r['sentence'])
        if is_requirement(s):
            r['sentence'] = s
            filtered.append(r)

    print(f'1차 필터 후: {len(filtered)}')

    # 2차: 사이트 공통 푸터 제거 (5+개 사업에서 등장하면 컷)
    proj_per_sent = defaultdict(set)
    for r in filtered:
        proj_per_sent[r['sentence']].add(r['project_id'])
    common = {s for s, ps in proj_per_sent.items() if len(ps) >= 5}
    filtered = [r for r in filtered if r['sentence'] not in common]
    print(f'사이트 공통 텍스트 컷 후: {len(filtered)}  (공통 문장 {len(common)}개 제거)')

    # 3차: 사업 내 중복 제거
    seen = set()
    unique = []
    for r in filtered:
        key = (r['project_id'], r['sentence'])
        if key in seen: continue
        seen.add(key); unique.append(r)
    print(f'사업 내 중복 제거 후: {len(unique)}')

    # ───── Smell 재집계 ─────
    SMELL_COLS = ['모호어','수동태','복합의무','정량부재','미정의약어','주체모호','약한의무']
    overall = {c: 0 for c in SMELL_COLS}
    overall_smelly = 0
    per_proj = defaultdict(lambda: dict({'sentences': 0, 'with_smell': 0}, **{c: 0 for c in SMELL_COLS}))
    proj_meta = {}
    for r in unique:
        pid = r['project_id']
        proj_meta[pid] = (r['org'], r['project'])
        per_proj[pid]['sentences'] += 1
        smelly = False
        for c in SMELL_COLS:
            v = int(r[c])
            per_proj[pid][c] += v
            overall[c] += v
            if v: smelly = True
        if smelly:
            per_proj[pid]['with_smell'] += 1
            overall_smelly += 1

    # ───── 출력 ─────
    # 1) 필터된 요구사항 CSV
    out_csv = OUT_DIR / 'requirements_filtered.csv'
    with open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['project_id','org','project','sentence','has_smell'] + SMELL_COLS + ['vague_hits']
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in unique: w.writerow({k: r.get(k, '') for k in fieldnames})

    # 2) 사업별 통계
    out_pp = OUT_DIR / 'requirements_per_project.csv'
    with open(out_pp, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['project_id','org','project','요구사항','Smell검출','%']+SMELL_COLS)
        for pid in sorted(per_proj):
            d = per_proj[pid]
            org, name = proj_meta[pid]
            pct = round(100*d['with_smell']/d['sentences'],1) if d['sentences'] else 0
            w.writerow([pid, org, name, d['sentences'], d['with_smell'], pct]+[d[c] for c in SMELL_COLS])

    # 3) 사업별 md
    md_dir = OUT_DIR / 'requirements_per_project_text'
    md_dir.mkdir(exist_ok=True)
    grouped = defaultdict(list)
    for r in unique: grouped[r['project_id']].append(r)
    for pid, lst in grouped.items():
        org, name = proj_meta[pid]
        with open(md_dir / f'{pid}.md', 'w', encoding='utf-8') as f:
            f.write(f'# {name}\n\n- 기관: {org}\n- 추출 요구사항: {len(lst)}건\n- Smell 검출: {sum(1 for x in lst if any(int(x[c]) for c in SMELL_COLS))}건\n\n---\n\n')
            for i, r in enumerate(lst, 1):
                tags = [c for c in SMELL_COLS if int(r[c])]
                tag_str = f"  `[{', '.join(tags)}]`" if tags else ''
                f.write(f'{i}. {r["sentence"]}{tag_str}\n\n')

    # 4) summary
    overall['total_requirements'] = len(unique)
    overall['total_with_smell']   = overall_smelly
    overall['filtered_from']      = len(rows)
    overall['projects_with_reqs'] = len([p for p in per_proj if per_proj[p]['sentences']>0])
    with open(OUT_DIR / 'requirements_summary.json', 'w', encoding='utf-8') as f:
        json.dump(overall, f, ensure_ascii=False, indent=2)

    print()
    print('=== 결과 요약 ===')
    print(f'  입력 문장: {len(rows)}')
    print(f'  최종 요구사항: {len(unique)} ({100*len(unique)/len(rows):.1f}%)')
    print(f'  Smell 검출: {overall_smelly} ({100*overall_smelly/max(len(unique),1):.1f}%)')
    print(f'  사업 (요구사항 ≥1건): {overall["projects_with_reqs"]} / 56')
    print()
    for c in SMELL_COLS:
        print(f'  {c:<8}  {overall[c]:>4}')

if __name__ == '__main__':
    main()
