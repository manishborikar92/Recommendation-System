import torch
from transformers import AutoTokenizer

print("PyTorch version:", torch.__version__)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
print("Tokenizer loaded successfully!")