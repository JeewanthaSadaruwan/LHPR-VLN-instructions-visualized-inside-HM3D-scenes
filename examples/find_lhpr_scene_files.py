from huggingface_hub import list_repo_files

repo_id = "Starry123/LHPR-VLN"
scene_id = "TEEsavR23oF"

print("Listing LHPR-VLN dataset files from Hugging Face...")
files = list_repo_files(repo_id, repo_type="dataset")

matches = [f for f in files if scene_id in f]

print(f"\nTotal files found in repo: {len(files)}")
print(f"Files matching scene ID '{scene_id}': {len(matches)}\n")

if matches:
    print("Matching files:")
    for f in matches[:100]:
        print(f)
else:
    print("No matching file paths found.")
    print("This may mean the scene ID is stored inside JSON files, not in the file names.")