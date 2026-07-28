"""RFP 요구사항 추출 — 3자(규칙/GPT-4o/Claude) 일치도 및 성능 비교.

과제: 각 방법이 문장을 '추출 대상 요구사항'으로 판정(0/1).
지표:
  - 쌍별 일치율, Cohen's kappa, McNemar
  - 다수결(2/3 이상) 합의를 참조표준으로 한 각 방법의 P/R/F1/Accuracy/MCC
  - 추가 지표: Specificity, Balanced Accuracy, Krippendorff-style 3자 일치율(만장일치 비율)
"""
import csv, json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent

def load(fn, key):
    d = {}
    for r in csv.DictReader(open(HERE/fn, encoding='utf-8-sig')):
        d[r['seg_id']] = int(r[key])
    return d

rule = load('extraction_sample.csv', 'rule_label')
gpt = load('llm_labels__gpt-4o.csv', 'llm_label')
cla = load('llm_labels__claude-fable-5.csv', 'llm_label')
ids = sorted(set(rule) & set(gpt) & set(cla), key=lambda x:int(x[1:]))
print(f'paired: {len(ids)}')

def kappa(a, b):
    n=len(a); po=sum(1 for x,y in zip(a,b) if x==y)/n
    pa=sum(a)/n; pb=sum(b)/n; pe=pa*pb+(1-pa)*(1-pb)
    return (po-pe)/(1-pe) if pe!=1 else float('nan')

def mcnemar(a, b):
    bb=sum(1 for x,y in zip(a,b) if x==1 and y==0)
    cc=sum(1 for x,y in zip(a,b) if x==0 and y==1)
    n=bb+cc
    if n==0: return 1.0,bb,cc
    k=min(bb,cc); p=min(1.0,sum(math.comb(n,i) for i in range(k+1))/(2**n)*2)
    return p,bb,cc

def prf(pred, ref):
    tp=sum(1 for p,r in zip(pred,ref) if p==1 and r==1)
    fp=sum(1 for p,r in zip(pred,ref) if p==1 and r==0)
    fn=sum(1 for p,r in zip(pred,ref) if p==0 and r==1)
    tn=sum(1 for p,r in zip(pred,ref) if p==0 and r==0)
    prec=tp/(tp+fp) if tp+fp else 0; rec=tp/(tp+fn) if tp+fn else 0
    f1=2*prec*rec/(prec+rec) if prec+rec else 0
    acc=(tp+tn)/len(pred); spec=tn/(tn+fp) if tn+fp else 0
    bacc=(rec+spec)/2
    den=math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))
    mcc=(tp*tn-fp*fn)/den if den else 0
    return dict(precision=round(prec,3),recall=round(rec,3),f1=round(f1,3),
                accuracy=round(acc,3),specificity=round(spec,3),
                balanced_acc=round(bacc,3),mcc=round(mcc,3),tp=tp,fp=fp,fn=fn,tn=tn)

R=[rule[i] for i in ids]; G=[gpt[i] for i in ids]; C=[cla[i] for i in ids]
# 다수결 합의 참조표준
ref=[1 if (rule[i]+gpt[i]+cla[i])>=2 else 0 for i in ids]

pairs={'rule_vs_gpt':(R,G),'rule_vs_claude':(R,C),'gpt_vs_claude':(G,C)}
result={'n':len(ids),'pairwise':{},'vs_majority':{},'agreement':{}}
print('\n=== 쌍별 일치 ===')
print(f"{'pair':<18}{'agree%':>8}{'kappa':>8}{'McNemar_p':>11}")
for name,(a,b) in pairs.items():
    ag=sum(1 for x,y in zip(a,b) if x==y)/len(a)*100
    kp=kappa(a,b); p,bb,cc=mcnemar(a,b)
    result['pairwise'][name]={'agreement_pct':round(ag,1),'kappa':round(kp,3),'mcnemar_p':round(p,4),'b':bb,'c':cc}
    print(f"{name:<18}{ag:>7.1f}%{kp:>8.3f}{p:>11.4f}")

print('\n=== 다수결 합의 대비 성능 ===')
print(f"{'method':<10}{'prec':>7}{'rec':>7}{'f1':>7}{'acc':>7}{'spec':>7}{'bacc':>7}{'mcc':>7}")
for name,pred in [('rule',R),('gpt-4o',G),('claude',C)]:
    m=prf(pred,ref); result['vs_majority'][name]=m
    print(f"{name:<10}{m['precision']:>7}{m['recall']:>7}{m['f1']:>7}{m['accuracy']:>7}{m['specificity']:>7}{m['balanced_acc']:>7}{m['mcc']:>7}")

# 3자 만장일치 / 다수결 분포
unan=sum(1 for i in ids if rule[i]==gpt[i]==cla[i])
result['agreement']['unanimous_pct']=round(100*unan/len(ids),1)
result['agreement']['majority_positive']=sum(ref)
result['agreement']['rule_pos']=sum(R); result['agreement']['gpt_pos']=sum(G); result['agreement']['claude_pos']=sum(C)
print(f"\n3자 만장일치: {unan}/{len(ids)} ({result['agreement']['unanimous_pct']}%)")
print(f"양성 판정 수 — 규칙 {sum(R)} / GPT-4o {sum(G)} / Claude {sum(C)} / 다수결 {sum(ref)}")

json.dump(result, open(HERE/'comparison.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('\nsaved: comparison.json')
