"""Stage 2-3 entrypoint — sentence_candidates.csv 입력 → ensemble smell labels 출력.

Usage:
    python scripts/run_detection.py \
        --input results/stage1_extraction/sentence_candidates.csv \
        --output results/stage3_detection/ \
        [--use-llm]
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kofinre.detectors import RegexDetector
from kofinre.detectors.morph_detector import MorphDetector
from kofinre.detectors.chunk_detector import ChunkDetector
from kofinre.detectors.dictionary_detector import DictionaryDetector
from kofinre.detectors.llm_detector import LLMDetector
from kofinre.detectors.regex_detector import collect_undefined_acronyms
from kofinre.ensemble import ensemble, SMELL_CODES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--use-llm', action='store_true')
    ap.add_argument('--ensemble', default='rule_priority',
                   choices=['majority', 'rule_priority', 'confidence_weighted'])
    ap.add_argument('--category', default=None, choices=['rfp', 'spec'],
                   help="문서 카테고리 — rfp: S1 묶음구조 S18 귀속(v2.9.3), spec: 기존 로직")
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(open(args.input, encoding='utf-8-sig')))
    sentences = [r.get('sentence', '') for r in rows]
    doc_text = '\n'.join(sentences)
    ctx = {'undefined_acronyms': collect_undefined_acronyms(doc_text),
           'category': args.category}

    regex = RegexDetector()
    morph = MorphDetector()
    chunk = ChunkDetector()
    diction = DictionaryDetector()
    llm = LLMDetector(llm_caller=None)  # 어댑터는 추후 주입

    # 개별 detector 결과
    out_dir = args.output / 'detector_outputs'
    out_dir.mkdir(exist_ok=True)
    detectors = {
        'regex': regex, 'morph': morph, 'chunk': chunk,
        'dictionary': diction, 'llm': llm,
    }
    for name, det in detectors.items():
        with open(out_dir / f'{name}_detector.csv', 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['sentence'] + SMELL_CODES)
            for s in sentences:
                r = det.detect(s, ctx)
                w.writerow([s] + [r.flags.get(c, {}).get('detected', 0) for c in SMELL_CODES])

    # 앙상블
    ensemble_out = args.output / 'ensemble_smell_labels.csv'
    confidence_out = args.output / 'detector_confidence.csv'
    with open(ensemble_out, 'w', encoding='utf-8-sig', newline='') as fe, \
         open(confidence_out, 'w', encoding='utf-8-sig', newline='') as fc:
        we = csv.writer(fe); wc = csv.writer(fc)
        we.writerow(['sentence', 'has_smell'] + SMELL_CODES)
        wc.writerow(['sentence'] + SMELL_CODES)
        for s in sentences:
            results = [d.detect(s, ctx) for d in detectors.values()]
            ens = ensemble(results, method=args.ensemble)
            flags = [ens[c]['detected'] for c in SMELL_CODES]
            confs = [round(ens[c]['confidence'], 2) for c in SMELL_CODES]
            we.writerow([s, int(any(flags))] + flags)
            wc.writerow([s] + confs)

    print(f'detector outputs: {out_dir}')
    print(f'ensemble: {ensemble_out}')
    print(f'confidence: {confidence_out}')


if __name__ == '__main__':
    main()
