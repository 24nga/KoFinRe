"""Stage 2 — 상용 LLM 2차 평가.

층화 표본(stage2_sample.csv)의 각 요구사항 행에 대해 K1~K11을 0/1 판정한다.
어댑터: anthropic / openai / ollama (로컬 대조용).
응답은 요구사항별 JSON으로 파싱하여 캐싱한다 (재실행 시 캐시 재사용).

Usage:
    python llm_judge.py --backend anthropic --model claude-sonnet-4-6
    python llm_judge.py --backend openai   --model gpt-5.2-low
    python llm_judge.py --backend ollama   --model gemma4:12b

출력:
    stage2_labels__<model>.csv   — segment_id × K1~K11 (sentence 미포함 → 커밋 가능)
    cache/<model>/<segment_id>.json — 원응답 캐시 (로컬 전용)
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent

K_CODES = ["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9", "K10", "K11"]

SYSTEM_PROMPT = """당신은 요구공학 품질 평가 전문가이다. 한국어 요구사항 문장 하나에 대해
아래 11종 스멜(K1~K11)의 존재 여부를 각각 0(없음) 또는 1(있음)로 판정하라.

K1 복합 요구사항 — 둘 이상의 독립 기능·의무가 한 행에 결합 (Paska Non-atomic / ISO Singular)
K2 불완전 명세 — 행위·대상·결과 중 하나 이상 생략, 문장이 자립적으로 완결되지 않음 (Incomplete requirement / Complete)
K3 주체·시스템 응답 누락 — 수행 주체 또는 시스템 응답 미명시 (Incomplete system response / Complete)
K4 불완전 조건 — 조건절만 있고 결과·판정 기준 없음 (Incomplete condition)
K5 수동 표현 — '~되어야 한다' 등 피동 표현으로 행위 주체가 흐려짐 (Passive voice)
K6 약한 의무 — '한다/된다/함' 평서형 종결로 의무 강도 불명확 (Not precise verb / Verifiable)
K7 결합 범위 모호 — '및/또는', '등' 열거로 적용 범위 불명확 (Coordination ambiguity)
K8 비요구사항 — 요구사항이 아닌 서술(목차·안내·배경 등) (Not requirement / Necessary)
K9 모호어 — '적절한', '필요한', '실시간' 등 판정 기준 없는 수식어 (ISO Unambiguous)
K10 정량 부재 — 성능·용량·시간 속성에 수치 기준 없음 (ISO Verifiable·Measurable)
K11 미정의 약어 — 영문 약어가 정의 없이 사용 (ISO Unambiguous·Complete)

반드시 아래 JSON 형식만 출력하라 (설명 금지):
{"K1":0,"K2":0,"K3":0,"K4":0,"K5":0,"K6":0,"K7":0,"K8":0,"K9":0,"K10":0,"K11":0}"""


def call_llm(backend: str, model: str, sentence: str) -> str:
    user = f"요구사항 문장:\n{sentence}\n\nJSON 판정:"
    if backend == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        r = client.messages.create(model=model, system=SYSTEM_PROMPT, max_tokens=200,
                                   temperature=0.0,
                                   messages=[{"role": "user", "content": user}])
        return r.content[0].text
    if backend == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        r = client.chat.completions.create(model=model, temperature=0.0, max_tokens=200,
                                           messages=[{"role": "system", "content": SYSTEM_PROMPT},
                                                     {"role": "user", "content": user}])
        return r.choices[0].message.content
    if backend == "ollama":
        import requests
        payload = {"model": model,
                   "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": user}],
                   "options": {"temperature": 0.0, "num_ctx": 4096},
                   "stream": False}
        r = requests.post("http://localhost:11434/api/chat", json=payload, timeout=1800)
        r.raise_for_status()
        return r.json()["message"]["content"]
    raise ValueError(backend)


def parse_flags(text: str) -> dict[str, int] | None:
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        data = json.loads(text[s:e + 1])
    except json.JSONDecodeError:
        return None
    try:
        return {k: int(data.get(k, 0)) for k in K_CODES}
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, choices=["anthropic", "openai", "ollama"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--sample", type=Path, default=HERE / "stage2_sample.csv")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    model_tag = re.sub(r"[^A-Za-z0-9.-]", "_", args.model)
    cache_dir = HERE / "cache" / model_tag
    cache_dir.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(open(args.sample, encoding="utf-8-sig")))
    if args.limit:
        rows = rows[: args.limit]
    print(f"{len(rows)} rows -> {args.backend}/{args.model}")

    out_rows, n_err = [], 0
    for i, r in enumerate(rows, 1):
        cache_f = cache_dir / f"{r['segment_id']}.json"
        if cache_f.exists():
            raw = json.loads(cache_f.read_text(encoding="utf-8"))["raw"]
        else:
            try:
                raw = call_llm(args.backend, args.model, r["sentence"])
            except Exception as exc:  # noqa: BLE001
                print(f"  [{r['segment_id']}] ERROR {type(exc).__name__}: {exc}")
                n_err += 1
                if n_err >= 5 and i <= 10:
                    print("연속 실패 — 중단 (키/크레딧 확인)")
                    sys.exit(1)
                continue
            cache_f.write_text(json.dumps({"raw": raw}, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.2)

        flags = parse_flags(raw)
        if flags is None:
            print(f"  [{r['segment_id']}] parse fail")
            n_err += 1
            continue
        out_rows.append({"segment_id": r["segment_id"], "project": r["project"], **flags})
        if i % 25 == 0:
            print(f"  {i}/{len(rows)}")

    out_path = HERE / f"stage2_labels__{model_tag}.csv"
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["segment_id", "project"] + K_CODES)
        w.writeheader()
        w.writerows(out_rows)
    print(f"done: {len(out_rows)} labeled, {n_err} errors -> {out_path.name}")


if __name__ == "__main__":
    main()
