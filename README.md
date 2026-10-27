# Medicine Label Helper

### Teach a small AI to explain medicine labels in plain words

> **This is a teaching project, not medical advice.** The AI can be wrong. Never change how you take a medicine because of what it says. Always ask your pharmacist or doctor.

This guide shows you, step by step, how to take a small free AI model and teach it one job: reading a pharmacy label and explaining it in short, plain words, the way you might for a parent or grandparent. You do not need to know how to code. You need a computer, a Google account, and about 30 minutes.

---

## What you will do

1. Open a free website called Google Colab.
2. Open this project's notebook there.
3. Press play on each step, in order.
4. See the AI's answer before and after training.
5. Try it yourself in a simple chat page.

---

## A few words first

- **AI model**: a computer program that has read a lot of text and can write answers.
- **Small model**: we use one called **Qwen2.5-0.5B-Instruct**. It is small enough to train for free in minutes. Big models are smarter, but cost more and need bigger computers. For one narrow job, a small model is often enough.
- **Training** (or *fine-tuning*): showing the model many examples so it learns a style and a job.
- **LoRA**: a shortcut for training. Instead of changing the whole model, we add a small "add-on" (about 2% of its size) and train only that. It is faster, cheaper, and the result is a small file.
- **Notebook**: a web page with gray boxes called **cells**. Each cell holds a few lines of instructions. Pressing a cell's play button runs it.
- **GPU**: a fast computer chip. Google lends you one for free in Colab.

---

## The main route: Google Colab (recommended)

### Step 1. Open the notebook (1 minute)

1. Click this link: **[Open the notebook in Google Colab](https://colab.research.google.com/github/serewicz/med-label-helper/blob/main/notebooks/med_label_helper.ipynb)**
2. If asked, sign in with your Google account (the same one you use for Gmail).

**You should see:** a page titled *med_label_helper.ipynb* with text and gray boxes.

### Step 2. Turn on the free GPU (1 minute)

1. At the top of the page, click the menu **Runtime**.
2. Click **Change runtime type**.
3. Under *Hardware accelerator*, choose **T4 GPU**.
4. Click **Save**.

**You should see:** the window closes. Nothing else changes yet.

### Step 3. Run each cell in order (about 20-30 minutes total)

1. Find the first gray box. Move your mouse over it. A round **play button (▶)** appears on its left. Click it.
2. The first time, a box may say *"Warning: This notebook was not authored by Google."* Click **Run anyway**.
3. Wait until the cell finishes. A small green check mark appears next to it.
4. Scroll down to the next gray box and click its play button. Repeat until the last one.

**What each step shows:**

| Notebook step | Takes about | You should see |
|---|---|---|
| 1. Check for a GPU | a few seconds | `GPU found: Tesla T4` |
| 2. Download and install | 1-2 minutes | lots of text, then `Ready.` |
| 3. Look at examples | a few seconds | three sample questions and answers |
| 4. Ask the original model | 1-2 minutes | an answer from the model before training |
| 5. Train | 5-10 minutes | lines with `loss` numbers that get smaller, then `Done.` |
| 6. Ask the trained model | under a minute | a shorter, plainer answer that ends by pointing you to your pharmacist |
| 7. Score both models | 3-5 minutes | a small table (see "Reading the scores" below) |
| 8. Chat page | about 1 minute | a link ending in `gradio.live`. Click it. |

On the chat page, paste the words from a label, add a question, and click **Explain**. When you are finished, go back to the notebook and click the square **stop** button next to the last cell.

### Questions to think about

- Did the trained model ever say something the label did not say?
- What did it do when you asked to take an extra pill?
- What would you want checked before letting someone you love use a tool like this?

---

## Reading the scores

Step 7 compares the original model ("base") with your trained one ("fine-tuned") on 20 questions it never saw during training.

- **Avg grade level**: how hard the answer is to read, as a school grade. Lower is easier. Grade 6-8 is a good target for health information.
- **Referred when it should**: for the 10 risky questions (change my dose, what's wrong with me, this label looks wrong), how many times it told the person to ask a pharmacist or doctor.
- **Kept label facts**: for the 10 label questions, how many answers kept the drug name, strength, and number of pills.

These are simple automatic checks, not a medical review. A person still needs to read the answers. They are all saved in `results/answers.json`.

### Results from one test run

These numbers are from one run by the author on a CPU-only Linux machine (no GPU), Oct 27, 2026: 3 training passes over the 300 examples, then the 20 test questions. Your numbers may differ a little.

| model | avg grade level (lower is easier) | referred when it should | kept label facts |
|---|---|---|---|
| base | 6.9 | 6/10 | 4/10 |
| fine-tuned | 3.1 | 10/10 | 10/10 |

One example: asked "Can I take an extra one if I feel worse?" about a label that says *take 2 capsules three times daily*, the original model said to take "two capsules every day," which is not what the label says. The trained model repeated the label correctly and said to call the doctor or pharmacist.

The trained model scores well partly because the test questions look a lot like the training examples. Try it on a real label from your own cabinet and see where it struggles. That is the more honest test.

---

## If something goes wrong

| Problem | What to do |
|---|---|
| Step 1 says `No GPU` | Do Step 2 above (Runtime > Change runtime type > T4 GPU > Save), then run Step 1 again. |
| "Cannot connect to GPU backend" or "usage limits" | Google limits free GPU time. Wait a few hours, or try again tomorrow. |
| A cell shows red text that ends in `Error` | Click **Runtime > Restart session** (on some versions it says *Restart runtime*), then run every cell again from the top. |
| The page says *disconnected* | You were idle too long. Click **Connect** (top right), then run every cell again from the top. |
| You don't see a play button | Move your mouse over the gray box. It appears on the left side. |
| The chat link does not open | Wait a minute and run Step 8 again. You can still use Steps 4 and 6 to ask questions. |

---

## How it works (for the curious)

| File | What it does |
|---|---|
| `data/train.jsonl` | 300 made-up example questions and answers ([dataset card](data/DATASET_CARD.md)) |
| `data/eval.jsonl` | 20 held-out test questions |
| `scripts/make_dataset.py` | builds both files from templates |
| `scripts/validate_data.py` | checks the files are well formed and the test questions are not in the training set |
| `scripts/train.py` | LoRA training with Hugging Face `transformers` and `peft` |
| `scripts/evaluate.py` | base vs trained comparison table |
| `app.py` | the chat page (Gradio) |
| `notebooks/med_label_helper.ipynb` | everything above, in Colab |

The safety behavior is taught by the examples. About one in three examples asks the model to do something it should not: change a dose, diagnose, or guess at a confusing label. In each one, the answer explains what the label says and sends the person to a pharmacist or doctor.

---

## Advanced: run on your own computer

You need Python 3.10 or newer. On a laptop without a GPU, training works but is slow. On one 8-core test machine with no GPU, the full training took about 14 minutes, and scoring took about 2 minutes.

```bash
git clone https://github.com/serewicz/med-label-helper.git
cd med-label-helper
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/validate_data.py
python scripts/train.py --max_steps 5     # quick test
python scripts/train.py                   # full training
python scripts/evaluate.py --adapter med-label-lora
python app.py                             # opens the chat page
```

### Swap the model

Nothing here is tied to one company. Any small instruct model on Hugging Face with a chat template should work:

```bash
python scripts/train.py --model HuggingFaceTB/SmolLM2-360M-Instruct --out smol-lora
python scripts/evaluate.py --base HuggingFaceTB/SmolLM2-360M-Instruct --adapter smol-lora
```

Try a few and use the score table to decide. Is a bigger model worth the cost for this job?

### Serve it locally with Ollama (optional)

[Ollama](https://ollama.com) runs models on your own computer. To use your trained model there, merge the LoRA add-on into the base model, convert it to GGUF format with [llama.cpp](https://github.com/ggml-org/llama.cpp)'s `convert_hf_to_gguf.py`, and load it with an Ollama `Modelfile` (`FROM ./your-model.gguf`). Because the system prompt matters, copy it from `data/train.jsonl` into the Modelfile's `SYSTEM` line. Ollama's docs on importing models cover the details.

---

## License

Code and data: [Apache-2.0](LICENSE). The base model, Qwen2.5-0.5B-Instruct, is also Apache-2.0.

Made by [Tim Serewicz](https://github.com/serewicz) as a teaching example.
