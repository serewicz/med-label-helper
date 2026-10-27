"""Check the dataset files are well formed. Run: python scripts/validate_data.py"""
import json, sys
bad = 0
for i, line in enumerate(open("data/train.jsonl"), 1):
    r = json.loads(line); m = r["messages"]
    if [x["role"] for x in m] != ["system", "user", "assistant"] or not all(x["content"].strip() for x in m):
        print("bad row", i); bad += 1
n = i
refer = sum(("pharmacist" in json.loads(l)["messages"][2]["content"] or "doctor" in json.loads(l)["messages"][2]["content"]) for l in open("data/train.jsonl"))
ev = [json.loads(l) for l in open("data/eval.jsonl")]
train_q = {json.loads(l)["messages"][1]["content"] for l in open("data/train.jsonl")}
overlap = sum(e["question"] in train_q for e in ev)
print(f"train rows: {n}, bad: {bad}, answers that point to a pharmacist/doctor: {refer}")
print(f"eval rows: {len(ev)}, eval questions also in train: {overlap}")
sys.exit(1 if bad or overlap else 0)
