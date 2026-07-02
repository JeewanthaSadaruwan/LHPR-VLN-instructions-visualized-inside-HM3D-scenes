import json
from pathlib import Path

root = Path("data/lhpr_extracted/task/batch_6")

total_tasks = 0
expected_total = 0
actual_total = 0
mismatches = []

for cfg_path in sorted(root.rglob("config.json")):
    task_dir = cfg_path.parent
    total_tasks += 1

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    subtask_list = cfg.get("Subtask list", [])

    # Count only navigation subtasks
    expected_nav = sum(1 for s in subtask_list if s.startswith("Move_to"))

    trial_dir = task_dir / "success" / "trial_1"

    if trial_dir.exists():
        # Count navigation step-task jsons, excluding full trajectory task.json
        actual_jsons = [
            p for p in trial_dir.glob("*.json")
            if p.name != "task.json"
        ]
        actual_nav = len(actual_jsons)
    else:
        actual_nav = 0

    expected_total += expected_nav
    actual_total += actual_nav

    if expected_nav != actual_nav:
        mismatches.append((task_dir, expected_nav, actual_nav))

print("Batch 6 subtask count check")
print("=" * 50)
print(f"Total tasks: {total_tasks}")
print(f"Expected Move_to subtasks from config.json: {expected_total}")
print(f"Actual step-task JSONs inside success/trial_1: {actual_total}")
print(f"Mismatched tasks: {len(mismatches)}")

print("\nMismatches:")
for task_dir, expected, actual in mismatches[:50]:
    print("-" * 80)
    print(task_dir)
    print(f"Expected Move_to subtasks: {expected}")
    print(f"Actual JSONs in trial_1: {actual}")