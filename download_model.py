import sys
from huggingface_hub import hf_hub_download

model_url = sys.argv[1]
model_path = sys.argv[2]

hf_hub_download(repo_id=model_url, filename=model_path, local_dir="/app/repo")

print(f"Model downloaded to {model_path}")