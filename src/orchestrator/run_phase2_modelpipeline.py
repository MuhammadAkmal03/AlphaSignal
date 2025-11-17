import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

def run(script):
    print(f"\n=== Running: {script} ===")
    result = subprocess.run([sys.executable, str(script)])
    if result.returncode != 0:
        raise RuntimeError(f" FAILED: {script}")

def run_phase2():
    print("\n PHASE 2: FEATURE ENGINEERING + MODEL TRAINING\n")

    steps = [
        SRC / "features" / "feature_engineering.py",
        SRC / "features" / "feature_selection.py",
        SRC / "modelling" / "prepare_train_set.py",
        SRC / "modelling" / "train_model.py",
    ]

    for s in steps:
        run(s)

    print("\n✔ PHASE 2 COMPLETE — MODEL TRAINED\n")

if __name__ == "__main__":
    run_phase2()
