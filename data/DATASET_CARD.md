# Dataset card: med-label-helper

## What it is
- `train.jsonl`: 300 chat examples. Each has a system message, a question with a medicine label, and a plain-language answer.
- `eval.jsonl`: 20 held-out questions used only for scoring. None of them appear in the training file.

## Where it came from
**All of it is synthetic (made up).** `scripts/make_dataset.py` builds it from templates. The drug names (Zorvatin, Brenolol, and so on), pharmacies, and people are invented. The label wording copies the style of real US pharmacy labels and common warning stickers. No real patient data is used.

## What it teaches
| Kind of example | Count | What the answer does |
|---|---|---|
| Explain a label | 150 | Restates the drug, strength, how many, how often, warnings, refills, in plain words |
| "How many / how often?" | 40 | Repeats the label's directions only |
| Asks to change a dose | 50 | Will not change or guess a dose; sends to pharmacist or doctor |
| Asks for a diagnosis | 30 | Will not diagnose; sends to doctor; says when to call 911 |
| Label looks wrong | 30 | Points out the problem (missing dose, conflicting lines, someone else's name); says not to guess |

## Limits
- Small and repetitive on purpose, so it trains in minutes. It is a teaching set, not a product.
- US-style labels in English only.
- The "label looks wrong" group uses only 4 patterns.

## Not medical advice
This data and any model trained on it must not be used to make health decisions. Always ask a pharmacist or doctor.
