from huggingface_hub import HfApi

repo_id = "Starry123/LHPR-VLN"
api = HfApi()

items = api.list_repo_tree(
    repo_id=repo_id,
    repo_type="dataset",
    recursive=False,
    expand=True,
)

zip_files = []

for item in items:
    if item.path.endswith(".zip"):
        size_gb = item.size / (1024 ** 3)
        zip_files.append((item.path, size_gb))

zip_files.sort(key=lambda x: x[1])

print("LHPR-VLN zip file sizes:\n")
for name, size_gb in zip_files:
    print(f"{name:20s} {size_gb:.2f} GB")

print("\nSmallest batch file:")
batch_files = [(n, s) for n, s in zip_files if n.startswith("batch_")]
batch_files.sort(key=lambda x: x[1])

if batch_files:
    print(f"{batch_files[0][0]}  {batch_files[0][1]:.2f} GB")