from huggingface_hub import list_repo_files

repo_id = "Starry123/LHPR-VLN"

files = list_repo_files(repo_id, repo_type="dataset")

print(f"Total files: {len(files)}\n")

for i, f in enumerate(files):
    print(f"{i}: {f}")