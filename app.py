"""A simple chat page to try the helper.  python app.py  then open the link it prints."""
import argparse, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
import gradio as gr
from helper import load, ask

p = argparse.ArgumentParser()
p.add_argument("--adapter", default="med-label-lora", help="folder from train.py, or 'none' for the base model")
p.add_argument("--share", action="store_true", help="make a temporary public link (needed in Colab)")
a = p.parse_args()
tok, model = load(adapter=None if a.adapter == "none" else a.adapter)

with gr.Blocks(title="Medicine Label Helper") as demo:
    gr.Markdown("# Medicine Label Helper\n**Teaching demo only. Not medical advice.** "
                "Always check with your pharmacist or doctor.")
    q = gr.Textbox(label="Type or paste the label text, and your question", lines=8)
    btn = gr.Button("Explain", variant="primary")
    out = gr.Textbox(label="Plain-language answer", lines=6)
    btn.click(lambda x: ask(tok, model, x), q, out)
demo.launch(share=a.share)
