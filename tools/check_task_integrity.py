#!/usr/bin/env python3
"""Check basic LHPR task folder integrity."""

from pathlib import Path


def main():
    root = Path("data/lhpr_extracted/task/batch_6")
    configs = list(root.rglob("config.json"))
    trials = list(root.rglob("success/trial_1"))
    print(f"Config files: {len(configs)}")
    print(f"Trial folders: {len(trials)}")


if __name__ == "__main__":
    main()

