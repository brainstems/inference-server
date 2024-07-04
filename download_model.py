import sys
from huggingface_hub import hf_hub_download

model_url = sys.argv[1]
model_path = sys.argv[2]

print(f"Starting download of {model_url}")

#hf_hub_download(repo_id=model_url, filename=model_path, repo_type="model")
hf_hub_download(repo_id=model_url, filename=model_path, local_dir="/app/repo/brainstems-jedai-akash-poc/", repo_type="model")
#hf_hub_download(repo_id=model_url, filename=model_path, local_dir=".", repo_type="model")

print(f"Model downloaded to {model_url}")
