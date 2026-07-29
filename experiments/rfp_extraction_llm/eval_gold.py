"""정답셋 대비 추출 성능 — Claude 편향 제거판.

정답(gold):
  - 규칙==GPT-4o 일치 세그먼트(129): 두 독립 방법 합의를 정답으로 채택 (Claude 무관)
  - 불일치 세그먼트(71): adjudication.csv의 재판정 라벨
평가: 규칙 / GPT-4o / Claude 각각을 gold 대비 P/R/F1/Acc/Spec/BalAcc/MCC.
"""
import csv, json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
H=Path(__file__).resolve().parent

sample={r['seg_id']:r for r in csv.DictReader(open(H/'extraction_sample.csv',encoding='utf-8-sig'))}
rule={s:int(sample[s]['rule_label']) for s in sample}
gpt={r['seg_id']:int(r['llm_label']) for r in csv.DictReader(open(H/'llm_labels__gpt-4o.csv',encoding='utf-8-sig'))}
cla={r['seg_id']:int(r['llm_label']) for r in csv.DictReader(open(H/'llm_labels__claude-fable-5.csv',encoding='utf-8-sig'))}
adj={r['seg_id']:int(r['gold']) for r in csv.DictReader(open(H/'adjudication.csv',encoding='utf-8-sig'))}

ids=sorted(sample,key=lambda x:int(x[1:]))
gold={}
agree_n=adj_n=0
for s in ids:
    if rule[s]==gpt[s]:
        gold[s]=rule[s]; agree_n+=1
    else:
        gold[s]=adj[s]; adj_n+=1
print(f'gold: {agree_n} from rule==GPT consensus (Claude-independent) + {adj_n} adjudicated')
print(f'gold positives: {sum(gold.values())}/{len(gold)}')

def prf(pred, ref):
    tp=sum(1 for p,r in zip(pred,ref) if p==1 and r==1); fp=sum(1 for p,r in zip(pred,ref) if p==1 and r==0)
    fn=sum(1 for p,r in zip(pred,ref) if p==0 and r==1); tn=sum(1 for p,r in zip(pred,ref) if p==0 and r==0)
    pr=tp/(tp+fp) if tp+fp else 0; rc=tp/(tp+fn) if tp+fn else 0
    f1=2*pr*rc/(pr+rc) if pr+rc else 0; acc=(tp+tn)/len(pred); sp=tn/(tn+fp) if tn+fp else 0
    den=math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)); mcc=(tp*tn-fp*fn)/den if den else 0
    return dict(precision=round(pr,3),recall=round(rc,3),f1=round(f1,3),accuracy=round(acc,3),
                specificity=round(sp,3),balanced_acc=round((rc+sp)/2,3),mcc=round(mcc,3),tp=tp,fp=fp,fn=fn,tn=tn)

G=[gold[s] for s in ids]
res={'gold_source':{'consensus':agree_n,'adjudicated':adj_n},'gold_positives':sum(gold.values()),'vs_gold':{}}
print(f"\n{'method':<10}{'prec':>7}{'rec':>7}{'f1':>7}{'acc':>7}{'spec':>7}{'bacc':>7}{'mcc':>7}")
for name,lab in [('rule',rule),('gpt-4o',gpt),('claude',cla)]:
    m=prf([lab[s] for s in ids],G); res['vs_gold'][name]=m
    print(f"{name:<10}{m['precision']:>7}{m['recall']:>7}{m['f1']:>7}{m['accuracy']:>7}{m['specificity']:>7}{m['balanced_acc']:>7}{m['mcc']:>7}")

json.dump(res,open(H/'gold_eval.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('\nsaved: gold_eval.json')
