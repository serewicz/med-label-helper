"""Shared code: load base or fine-tuned model and answer one question."""
import json, os, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
SYSTEM = json.loads(open(os.path.join(os.path.dirname(__file__), "..", "data", "train.jsonl")).readline())["messages"][0]["content"]

def load(base="Qwen/Qwen2.5-0.5B-Instruct", adapter=None):
    if adapter and os.path.exists(f"{adapter}/base.json"):
        base = json.load(open(f"{adapter}/base.json"))["base_model"]
    gpu = torch.cuda.is_available()
    tok = AutoTokenizer.from_pretrained(base)
    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.float16 if gpu else torch.float32)
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    return tok, model.to("cuda" if gpu else "cpu").eval()

def ask(tok, model, question, max_new_tokens=160):
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    text = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    ids = tok(text, return_tensors="pt", add_special_tokens=False)["input_ids"].to(model.device)
    with torch.no_grad():
        out = model.generate(ids, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True).strip()
