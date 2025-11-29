import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

def run(script):
    print(f"\n=== Running: {script} ===")
    result = subprocess.run([sys.executable, str(script)])
    if result.returncode != 0:
        raise RuntimeError(f" FAILED: {script}")

def run_phase3():
    print("\n PHASE 3: DAILY PREDICTION + METRICS\n")

    steps = [
        SRC / "modelling" / "predict_and_log.py",
        SRC / "modelling" / "update_actuals.py",
        SRC / "modelling" / "metrics_tracker.py",
        SRC / "modelling" / "accuracy_plot.py",
    ]

    for s in steps:
        run(s)

    print("\n PHASE 3 COMPLETE — PREDICTION FINISHED\n")

if __name__ == "__main__":
    run_phase3()
