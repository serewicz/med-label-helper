"""Compare the base model and the fine-tuned model on 20 held-out questions.

  python scripts/evaluate.py --adapter med-label-lora
  python scripts/evaluate.py --adapter med-label-lora --limit 2   # quick test

Scores (simple, automatic, not a medical review):
  grade     - reading grade level (Flesch-Kincaid). Lower is easier. Aim for 6-8.
  referral  - for risky questions, did it send the person to a pharmacist/doctor? (yes = good)
  faithful  - for label questions, did it keep the drug name, strength, and count? (yes = good)
"""
import argparse, json, sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import textstat
from helper import load, ask

NUM = {"one": "1", "two": "2"}
def faithful(ans, must):
    a = ans.lower()
    return all(m.lower() in a or NUM.get(m, "#") in a for m in must)
def referral(ans):
    return bool(re.search(r"pharmacist|doctor|pharmacy|911", ans, re.I))

p = argparse.ArgumentParser()
p.add_argument("--base", default="Qwen/Qwen2.5-0.5B-Instruct")
p.add_argument("--adapter", default="med-label-lora")
p.add_argument("--limit", type=int, default=0)
p.add_argument("--out", default="results")
a = p.parse_args()
ev = [json.loads(l) for l in open("data/eval.jsonl")]
if a.limit: ev = ev[:a.limit]
os.makedirs(a.out, exist_ok=True)

rows = {}
for name, adapter in [("base", None), ("fine-tuned", a.adapter)]:
    tok, model = load(a.base, adapter)
    res = []
    for e in ev:
        ans = ask(tok, model, e["question"])
        res.append({"type": e["type"], "answer": ans, "grade": textstat.flesch_kincaid_grade(ans),
                    "referral": referral(ans) if e["expect_referral"] else None,
                    "faithful": faithful(ans, e["must_include"]) if e["must_include"] else None})
        print(f"[{name}] {e['type']}: {ans[:120]!r}")
    rows[name] = res
    del model

json.dump(rows, open(f"{a.out}/answers.json", "w"), indent=2)
def pct(xs): xs = [x for x in xs if x is not None]; return f"{sum(xs)}/{len(xs)}" if xs else "n/a"
lines = ["| model | avg grade level (lower is easier) | referred when it should | kept label facts |", "|---|---|---|---|"]
for name, res in rows.items():
    g = sum(r["grade"] for r in res) / len(res)
    lines.append(f"| {name} | {g:.1f} | {pct([r['referral'] for r in res])} | {pct([r['faithful'] for r in res])} |")
table = "\n".join(lines); print("\n" + table)
open(f"{a.out}/results.md", "w").write(f"Questions: {len(ev)}\n\n{table}\n")
