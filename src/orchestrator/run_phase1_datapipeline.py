import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

def run(script):
    print(f"\n=== Running: {script} ===")
    result = subprocess.run([sys.executable, str(script)])
    if result.returncode != 0:
        raise RuntimeError(f" FAILED: {script}")

def run_phase1():
    print("\n PHASE 1: BUILD MASTER DATASET\n")

    steps = [

        # 1 — AIS
        SRC / "data_sources" / "ais" / "ais_stream.py",

        # 2 — NLP
        # SRC / "data_sources" / "nlp" / "nlp_demand_score.py",
        
        # 2b — Real-time News Sentiment (fetches latest oil news)
        SRC / "data_sources" / "nlp" / "realtime_oil_news.py",
        
        # 2c — Convert to daily and merge with news sentiment
        SRC / "data_sources" / "nlp" / "nlp_daily_converter.py",

        # 3 — USO
        SRC / "data_sources" / "uso" / "uso_fetcher.py",

        # 4 — EIA (your script fetches ALL)
        SRC / "data_sources" / "eia" / "eia_fetcher.py",

        # 5 — Sentinel & YOLO
        # SRC / "data_sources" / "sentinel" / "sentinel_refinery_fetcher.py",
        # SRC / "data_sources" / "sentinel" / "extract_sentinel_images.py",
        # SRC / "data_sources" / "sentinel" / "rename_by_date.py",
        # SRC / "cv" / "yolo_predict.py",

        SRC / "data_sources" / "past" / "past_inventory.py",
        # 6 — Master generation
        SRC / "final_data" / "01_build_master_dataset.py",
        SRC / "final_data" / "02_clean_master.py",
        SRC / "final_data" / "03_merge_full_clean.py",
    ]

    for step in steps:
        if step.exists():
            run(step)
        else:
            print(f" SKIPPED (not found): {step}")

    print("\n PHASE 1 COMPLETE — MASTER DATASET READY")

if __name__ == "__main__":
    run_phase1()
