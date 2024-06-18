import sys
from huggingface_hub import snapshot_download

model_url = sys.argv[0] 

print(f"Starting download of {model_url}")

#hf_hub_download(repo_id=model_url,filename=model_path, repo_type="model")
snapshot_download(repo_id=model_url)

print(f"Model downloaded to {model_url}")