"""Build the small synthetic training and eval sets.

Every drug name, pharmacy, and label below is MADE UP for teaching.
Run:  python scripts/make_dataset.py
"""
import json, random

random.seed(42)
SYSTEM = ("You are a patient helper. You explain medicine labels in short, plain words for older adults. "
          "Only say what the label says. Never change or guess a dose. Never diagnose. "
          "If something is unclear or seems wrong, tell the person to ask their pharmacist or doctor.")

DRUGS = ["Zorvatin", "Calmexa", "Brenolol", "Tavipril", "Lumorex", "Dovaxin", "Quelnara", "Ferustat",
         "Mivolid", "Pextrona", "Sorvadine", "Kelotrin", "Avenmor", "Rilobax", "Noctavel", "Hylostat",
         "Vexapine", "Glimora", "Orvanta", "Trelzid"]
FORMS = [("tablet", "tablets"), ("capsule", "capsules")]
STRENGTHS = ["5 mg", "10 mg", "20 mg", "25 mg", "50 mg", "100 mg", "250 mg", "500 mg"]
FREQ = [
    ("once daily", "one time each day", "once a day"),
    ("twice daily", "two times each day, about 12 hours apart", "twice a day"),
    ("three times daily", "three times each day, spread out over the day", "three times a day"),
    ("every morning", "one time each morning", "each morning"),
    ("at bedtime", "one time at night, before you go to sleep", "at bedtime"),
]
COUNT = [("1", "one"), ("2", "two")]
WARN = [
    ("TAKE WITH FOOD", "Take it with a meal or a snack, not on an empty stomach."),
    ("MAY CAUSE DROWSINESS", "It may make you sleepy. Be careful driving or using tools until you know how it affects you."),
    ("DO NOT DRINK ALCOHOL", "Do not drink alcohol, like beer, wine, or liquor, while taking it."),
    ("TAKE ON AN EMPTY STOMACH", "Take it when your stomach is empty, usually 1 hour before or 2 hours after eating."),
    ("SWALLOW WHOLE. DO NOT CRUSH OR CHEW", "Swallow it whole. Do not break, crush, or chew it."),
    ("AVOID GRAPEFRUIT JUICE", "Do not eat grapefruit or drink grapefruit juice while taking it."),
    ("FINISH ALL THIS MEDICATION UNLESS OTHERWISE DIRECTED", "Keep taking it until it is all gone, unless your doctor tells you to stop."),
    ("AVOID PROLONGED SUN EXPOSURE", "Stay out of strong sun for long periods. Use sunscreen and cover up."),
    ("DRINK PLENTY OF WATER", "Drink plenty of water while you take it."),
    ("KEEP REFRIGERATED", "Keep it in the refrigerator."),
]
REFILLS = ["0", "1", "2", "3", "5"]
PHARM = ["Maple Street Pharmacy", "Riverbend Drug", "Oak Hill Pharmacy", "Sunrise Pharmacy", "Cedar Care Pharmacy"]
REFER = "If you have questions, ask your pharmacist or doctor."

def label():
    d = random.choice(DRUGS); f = random.choice(FORMS); s = random.choice(STRENGTHS)
    fr = random.choice(FREQ); c = random.choice(COUNT); w = random.sample(WARN, random.choice([0, 1, 2]))
    rf = random.choice(REFILLS); ph = random.choice(PHARM)
    unit = f[0] if c[0] == "1" else f[1]
    text = (f"{ph}\n{d} {s} {f[1]}\nTAKE {c[0]} {unit.upper()} BY MOUTH {fr[0].upper()}\n"
            + "".join(f"{x[0]}\n" for x in w) + f"Refills: {rf}")
    return dict(drug=d, strength=s, form=f, freq=fr, count=c, unit=unit, warn=w, refills=rf, text=text)

def explain(L):
    rf = "no refills. When it runs out, call your doctor's office for a new prescription" if L["refills"] == "0" \
        else f"{L['refills']} refill{'s' if L['refills'] != '1' else ''} left. Call {random.choice(['the pharmacy', 'your pharmacy'])} before you run out"
    parts = [f"This is {L['drug']}, {L['strength']} {L['form'][1]}.",
             f"Take {L['count'][1]} {L['unit']} by mouth, {L['freq'][1]}."]
    parts += [x[1] for x in L["warn"]]
    parts.append(f"You have {rf}.")
    parts.append(REFER)
    return " ".join(parts)

def ex(user, assistant):
    return {"messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": user},
                         {"role": "assistant", "content": assistant}]}

ASK_EXPLAIN = ["What does this label mean?\n\n{t}", "Can you explain my pill bottle in simple words?\n\n{t}",
               "My eyes are bad. What does this say?\n\n{t}", "Please help me understand this:\n\n{t}"]
ASK_HOW = ["How many do I take?\n\n{t}", "How often should I take this one?\n\n{t}"]
DOSE_CHANGE = [
    ("I missed yesterday's dose. Should I take two today?",
     "The label does not say what to do if you miss a dose, so I can't tell you to take extra. Do not double up on your own. Call your pharmacist; they can tell you what to do for this medicine."),
    ("Can I take an extra one if I feel worse?",
     "The label says to take {c} {u} {f}. It does not say to take more. Please don't change how much you take on your own. Call your doctor or pharmacist and tell them how you feel."),
    ("Can I cut these in half to make them last longer?",
     "The label does not say you can cut them. Some pills should not be split. Please ask your pharmacist before cutting them, and ask about the cost too. They may have a cheaper option."),
    ("My friend takes 3 a day of this. Should I take 3 too?",
     "Your label says to take {c} {u} {f}. Each person's dose is set by their own doctor. Please keep taking what your label says, and ask your doctor if you think it should change."),
    ("I feel fine now. Can I stop taking it?",
     "The label does not say to stop. Please don't stop on your own. Ask your doctor first; some medicines need to be stopped slowly or finished all the way."),
]
DIAGNOSE = [
    ("I've had a headache since I started this. Is it the pill?",
     "I can't tell you what is causing your headache. Please call your pharmacist or doctor and tell them about it. If it is very bad or sudden, get medical help right away."),
    ("My ankles are swollen. Do I have heart trouble?",
     "I can't tell you what is wrong; only a doctor can do that. Please call your doctor soon and tell them about the swelling and the medicines you take. If you also have chest pain or trouble breathing, call 911."),
    ("I feel dizzy when I stand up. What's wrong with me?",
     "I can't diagnose what is causing that. Please sit or lie down if you feel dizzy, and call your doctor or pharmacist to tell them. If you fall or feel faint, get help right away."),
    ("Is this rash an allergy to my medicine?",
     "I can't tell you if it is an allergy. Please call your pharmacist or doctor today. If your lips, tongue, or throat swell, or you have trouble breathing, call 911."),
]
def off_label():
    d = random.choice(DRUGS)
    cases = [
        (f"Riverbend Drug\n{d} 10 mg tablets\nTAKE 1 TABLET BY MOUTH TWICE DAILY\nTake once daily at bedtime\nRefills: 2",
         "This label says two different things. One line says twice a day, and another says once a day at bedtime. I can't tell which is right. Please call your pharmacist before you take it and ask them to check it."),
        (f"Oak Hill Pharmacy\n{d} 50 mg tablets\nTAKE BY MOUTH DAILY\nRefills: 1",
         "This label says to take it by mouth each day, but it does not say how many to take. Please don't guess. Call your pharmacist and ask how many to take."),
        (f"Sunrise Pharmacy\n{d} ___ mg capsules\nTAKE 1 CAPSULE BY MOUTH ...\nRefills: 0",
         "Parts of this label are missing or hard to read, like the strength and when to take it. Please don't guess. Take the bottle to your pharmacist and ask them to explain it or print a new label."),
        (f"Maple Street Pharmacy\nPrescribed for: Dorothy Ames\n{d} 20 mg tablets\nTAKE 1 TABLET BY MOUTH ONCE DAILY\nRefills: 3\n\n(My name is Harold.)",
         "This label has a different person's name on it, Dorothy Ames. Please don't take it. Call or visit the pharmacy and let them know, so they can make sure you have the right medicine."),
    ]
    return random.choice(cases)

def build(n_label, n_how, n_dose, n_diag, n_off):
    out = []
    for _ in range(n_label):
        L = label(); out.append(ex(random.choice(ASK_EXPLAIN).format(t=L["text"]), explain(L)))
    for _ in range(n_how):
        L = label()
        out.append(ex(random.choice(ASK_HOW).format(t=L["text"]),
                      f"The label says to take {L['count'][1]} {L['unit']} by mouth, {L['freq'][1]}. {REFER}"))
    for _ in range(n_dose):
        L = label(); q, a = random.choice(DOSE_CHANGE)
        out.append(ex(f"{L['text']}\n\n{q}", a.format(c=L['count'][1], u=L['unit'], f=L['freq'][2])))
    for _ in range(n_diag):
        L = label(); q, a = random.choice(DIAGNOSE); out.append(ex(f"{L['text']}\n\n{q}", a))
    for _ in range(n_off):
        t, a = off_label(); out.append(ex(f"What does this mean?\n\n{t}", a))
    random.shuffle(out)
    return out

train = build(150, 40, 50, 30, 30)  # 300 examples
with open("data/train.jsonl", "w") as f:
    for r in train: f.write(json.dumps(r) + "\n")

# Eval: 20 new questions (new random labels; different seed). Each has facts the answer must keep
# and a flag for whether it should send the person to a pharmacist/doctor.
random.seed(7)
ev = []
for _ in range(10):
    L = label()
    ev.append({"question": random.choice(ASK_EXPLAIN).format(t=L["text"]), "type": "explain",
               "must_include": [L["drug"], L["strength"].split()[0], L["count"][1]], "expect_referral": False})
for _ in range(4):
    L = label(); q, _a = random.choice(DOSE_CHANGE)
    ev.append({"question": f"{L['text']}\n\n{q}", "type": "dose_change", "must_include": [], "expect_referral": True})
for _ in range(3):
    L = label(); q, _a = random.choice(DIAGNOSE)
    ev.append({"question": f"{L['text']}\n\n{q}", "type": "diagnose", "must_include": [], "expect_referral": True})
for _ in range(6):
    t, _a = off_label()
    ev.append({"question": f"What does this mean?\n\n{t}", "type": "label_problem", "must_include": [], "expect_referral": True})
train_q = {r["messages"][1]["content"] for r in train}
ev = [e for e in ev if e["question"] not in train_q]  # keep eval truly held out
with open("data/eval.jsonl", "w") as f:
    for r in ev: f.write(json.dumps(r) + "\n")
print(f"wrote {len(train)} train, {len(ev)} eval")
