import os
from transformers import AutoTokenizer, AutoModel


os.environ["HF_TOKEN"] = "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"

model_name = "Qwen/Qwen2.5-1.5B-Instruct"
save_path = "./Qwen2.5-1.5B-Instruct"


tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print(f"Saved model to {save_path}")