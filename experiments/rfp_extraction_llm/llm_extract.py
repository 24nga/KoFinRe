"""RFP 요구사항 추출 — LLM 판정 (GPT-4o / Claude).

각 RFP 문장에 대해 '구조화 가능한 시스템 요구사항인가'를 판정한다(추출 식별).
작성 품질을 평가하지 않는다 — 순수 추출/식별 과제.

출력: is_requirement(0/1) + 구조화 필드(actor/action/object) 추출.
Usage:
    python llm_extract.py --backend openai --model gpt-4o
    python llm_extract.py --backend anthropic --model claude-sonnet-4-6
"""
import argparse, csv, json, os, re, sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent

SYSTEM = """당신은 요구공학 전문가이다. RFP(제안요청서) 문장 하나를 보고, 그것이
'구조화 가능한 시스템 기능/성능/제약 요구사항'인지 식별하라. 요구사항의 작성 품질은
평가하지 않는다 — 오직 추출 대상 여부만 판정한다.

요구사항이 아닌 것: 사업 개요·일정·예산, 입찰 안내, 평가 기준, 기관/담당자 정보,
목차·머리글, 제출 서식 안내, 일반 관리 조항.
요구사항인 것: 시스템이 제공/처리/관리해야 할 기능, 성능·용량 기준, 인터페이스, 제약.

요구사항이면 구조화 필드도 추출하라. 반드시 아래 JSON만 출력:
{"is_requirement": 0 또는 1, "actor": "<주체 또는 null>", "action": "<동작 또는 null>", "object": "<대상 또는 null>"}"""

def call(backend, model, sentence):
    user = f"RFP 문장:\n{sentence}\n\nJSON 판정:"
    if backend == 'openai':
        from openai import OpenAI
        c = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        r = c.chat.completions.create(model=model, temperature=0, max_tokens=200,
            messages=[{'role':'system','content':SYSTEM},{'role':'user','content':user}])
        return r.choices[0].message.content
    if backend == 'anthropic':
        import anthropic
        c = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
        r = c.messages.create(model=model, system=SYSTEM, max_tokens=200, temperature=0,
            messages=[{'role':'user','content':user}])
        return r.content[0].text

def parse(t):
    s, e = t.find('{'), t.rfind('}')
    if s < 0 or e < 0: return None
    try:
        d = json.loads(t[s:e+1])
        return {'is_requirement': int(d.get('is_requirement', 0)),
                'actor': d.get('actor'), 'action': d.get('action'), 'object': d.get('object')}
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', required=True, choices=['openai','anthropic'])
    ap.add_argument('--model', required=True)
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()
    tag = re.sub(r'[^A-Za-z0-9.-]','_',args.model)
    cache = HERE/'cache'/tag; cache.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(open(HERE/'extraction_sample.csv', encoding='utf-8-sig')))
    if args.limit: rows = rows[:args.limit]
    out, err = [], 0
    for i, r in enumerate(rows, 1):
        cf = cache/f"{r['seg_id']}.json"
        if cf.exists():
            raw = json.loads(cf.read_text(encoding='utf-8'))['raw']
        else:
            try:
                raw = call(args.backend, args.model, r['sentence'])
            except Exception as e:
                print(f"  [{r['seg_id']}] ERR {type(e).__name__}: {str(e)[:80]}"); err += 1
                if err >= 5 and i <= 10: print('연속 실패 중단'); sys.exit(1)
                continue
            cf.write_text(json.dumps({'raw':raw}, ensure_ascii=False), encoding='utf-8'); time.sleep(0.15)
        p = parse(raw)
        if p is None: err += 1; continue
        out.append({'seg_id':r['seg_id'],'rule_label':r['rule_label'],
                    'llm_label':p['is_requirement'],'actor':p['actor'] or '','action':p['action'] or '','object':p['object'] or ''})
        if i % 25 == 0: print(f'  {i}/{len(rows)}')
    op = HERE/f'llm_labels__{tag}.csv'
    with open(op,'w',encoding='utf-8-sig',newline='') as f:
        w = csv.DictWriter(f, fieldnames=['seg_id','rule_label','llm_label','actor','action','object'])
        w.writeheader(); w.writerows(out)
    print(f'done: {len(out)} labeled, {err} err -> {op.name}')

if __name__ == '__main__':
    main()
