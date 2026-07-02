from huggingface_hub import hf_hub_download
from pathlib import Path

repo_id = "Starry123/LHPR-VLN"

files_to_download = [
    "batch_6.zip",       # smallest trajectory/image batch
    "step_task.zip",     # step-level task JSONs
    "task.zip",          # updated task/config JSONs
    "episode_task.zip",  # very small, useful later
]

output_dir = Path("data/lhpr_raw")
output_dir.mkdir(parents=True, exist_ok=True)

for file_name in files_to_download:
    print(f"\nDownloading: {file_name}")

    path = hf_hub_download(
        repo_id=repo_id,
        repo_type="dataset",
        filename=file_name,
        local_dir=str(output_dir),
    )

    print(f"Saved to: {path}")

print("\nDownload complete.")