"""Fine-tune a small model with LoRA on data/train.jsonl.

Free Colab T4 GPU: about 5-10 minutes for 3 epochs.
CPU only: works, but slow (use --max_steps 5 just to test).

  python scripts/train.py                       # full run
  python scripts/train.py --max_steps 5         # quick smoke test
  python scripts/train.py --model HuggingFaceTB/SmolLM2-360M-Instruct   # swap models
"""
import argparse, json, torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from peft import LoraConfig, get_peft_model

p = argparse.ArgumentParser()
p.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
p.add_argument("--data", default="data/train.jsonl")
p.add_argument("--out", default="med-label-lora")
p.add_argument("--epochs", type=float, default=3)
p.add_argument("--max_steps", type=int, default=-1)
p.add_argument("--lr", type=float, default=2e-4)
a = p.parse_args()

gpu = torch.cuda.is_available()
print("GPU found" if gpu else "No GPU found: running on CPU (slow)")
tok = AutoTokenizer.from_pretrained(a.model)
if tok.pad_token is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.float16 if gpu else torch.float32)

# LoRA: train small add-on matrices instead of the whole model.
model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                                         target_modules="all-linear"))
model.print_trainable_parameters()

def encode(row):
    msgs = row["messages"]
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True)
    full = prompt + msgs[-1]["content"] + tok.eos_token
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    ids = tok(full, add_special_tokens=False, truncation=True, max_length=512)["input_ids"]
    labels = [-100] * len(p_ids) + ids[len(p_ids):]  # only learn the answer part
    return {"input_ids": ids, "attention_mask": [1] * len(ids), "labels": labels[:len(ids)]}

ds = load_dataset("json", data_files=a.data)["train"].map(encode, remove_columns=["messages"])
args = TrainingArguments(output_dir=a.out, num_train_epochs=a.epochs, max_steps=a.max_steps,
                         per_device_train_batch_size=4, gradient_accumulation_steps=2, learning_rate=a.lr,
                         logging_steps=1 if a.max_steps > 0 else 10, save_strategy="no", report_to=[],
                         fp16=gpu, lr_scheduler_type="cosine", warmup_steps=5)
Trainer(model=model, args=args, train_dataset=ds,
        data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100)).train()
model.save_pretrained(a.out); tok.save_pretrained(a.out)
json.dump({"base_model": a.model}, open(f"{a.out}/base.json", "w"))
print(f"Done. Saved the LoRA adapter to ./{a.out}")
