import sys
from huggingface_hub import hf_hub_download

model_url = sys.argv[1]
model_path = sys.argv[2]

print(f"Starting download of {model_url} and {model_path}")

hf_hub_download(repo_id=model_url,filename=model_path, repo_type="model", local_dir="/app/repo")

print(f"Model downloaded to {model_path}")