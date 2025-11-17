import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

PHASE2_STEPS = [
    ("Feature Engineering", SRC / "features" / "feature_engineering.py"),
    ("Feature Selection", SRC / "features" / "feature_selection.py"),
    ("Prepare Training Dataset", SRC / "modelling" / "prepare_train_set.py"),
    ("Train Model", SRC / "modelling" / "train_model.py"),
    ("Run Inference", SRC / "modelling" / "inference.py"),
    ("Evaluate Prediction", SRC / "modelling" / "evaluate_prediction.py"),
    ("Update Metrics", SRC / "modelling" / "metrics_tracker.py"),
    ("Generate Accuracy Plot", SRC / "modelling" / "accuracy_plot.py"),
]

def run_script(name, path):
    print(f"\n=== {name} ===")
    result = subprocess.run([sys.executable, str(path)], text=True)
    if result.returncode != 0:
        raise RuntimeError(f" Error at: {name}")

def run_phase2():
    print("\n RUNNING PHASE 2: MODELLING PIPELINE\n")

    for name, script in PHASE2_STEPS:
        run_script(name, script)

    print("\n PHASE 2 COMPLETE! Model updated.\n")

if __name__ == "__main__":
    run_phase2()
