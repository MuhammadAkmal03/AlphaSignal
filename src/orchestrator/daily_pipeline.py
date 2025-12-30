"""
Daily Pipeline - Complete Orchestration
Runs all phases: data collection, training, prediction, and uploads to GCS

This script is designed to be run daily via GitHub Actions or Cloud Scheduler.
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

def run(script, description=""):
    """Run a Python script and track execution"""
    print(f"\n{'='*60}")
    print(f" {description or script.name}")
    print(f"{'='*60}")
    
    start = datetime.now()
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    duration = (datetime.now() - start).total_seconds()
    
    if result.returncode != 0:
        print(f" FAILED: {script}")
        print(f"   Error: {result.stderr[:500] if result.stderr else 'Unknown error'}")
        return False
    
    print(f" Completed in {duration:.1f}s")
    if result.stdout:
        # Print last 10 lines of output
        lines = result.stdout.strip().split('\n')
        for line in lines[-10:]:
            print(f"   {line}")
    return True

def run_phase1_data():
    """Phase 1: Fetch fresh data"""
    print("\n" + "="*70)
    print(" PHASE 1: DATA COLLECTION")
    print("="*70)
    
    steps = [
        (SRC / "data_sources" / "nlp" / "realtime_oil_news.py", "Fetching Oil News & Sentiment"),
        (SRC / "data_sources" / "uso" / "uso_fetcher.py", "Fetching USO Data"),
        (SRC / "data_sources" / "eia" / "eia_fetcher.py", "Fetching EIA Data"),
    ]
    
    success_count = 0
    for script, desc in steps:
        if script.exists():
            if run(script, desc):
                success_count += 1
        else:
            print(f" Skipped (not found): {script}")
    
    return success_count > 0

def run_phase2_training():
    """Phase 2: Retrain the model"""
    print("\n" + "="*70)
    print(" PHASE 2: MODEL TRAINING")
    print("="*70)
    
    steps = [
        (SRC / "final_data" / "01_build_master_dataset.py", "Building Master Dataset"),
        (SRC / "final_data" / "02_clean_master.py", "Cleaning Dataset"),
        (SRC / "final_data" / "03_merge_full_clean.py", "Merging Full Clean"),
        (SRC / "modelling" / "prepare_train_set.py", "Preparing Training Set"),
        (SRC / "modelling" / "train_model.py", "Training XGBoost Model"),
    ]
    
    for script, desc in steps:
        if script.exists():
            if not run(script, desc):
                print(f" Training phase had issues at {script.name}")
                return False
        else:
            print(f" Skipped (not found): {script}")
    
    return True

def run_phase3_prediction():
    """Phase 3: Generate predictions"""
    print("\n" + "="*70)
    print(" PHASE 3: PREDICTION")
    print("="*70)
    
    steps = [
        (SRC / "modelling" / "predict_and_log.py", "Generating Daily Prediction"),
    ]
    
    for script, desc in steps:
        if script.exists():
            if not run(script, desc):
                return False
        else:
            print(f" Skipped (not found): {script}")
    
    return True

def run_phase4_upload():
    """Phase 4: Upload to GCS"""
    print("\n" + "="*70)
    print(" PHASE 4: UPLOAD TO GCS")
    print("="*70)
    
    upload_script = SRC / "orchestrator" / "gcs_uploader.py"
    if upload_script.exists():
        return run(upload_script, "Uploading to GCS")
    else:
        print(" GCS uploader not found")
        return False

def main():
    print("\n" + "="*70)
    print(" ALPHASIGNAL DAILY PIPELINE")
    print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    start_time = datetime.now()
    
    # Run all phases
    phases = [
        ("Data Collection", run_phase1_data),
        ("Model Training", run_phase2_training),
        ("Prediction", run_phase3_prediction),
        ("GCS Upload", run_phase4_upload),
    ]
    
    results = {}
    for phase_name, phase_func in phases:
        try:
            results[phase_name] = phase_func()
        except Exception as e:
            print(f"{phase_name} failed with exception: {e}")
            results[phase_name] = False
    
    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "="*70)
    print(" PIPELINE SUMMARY")
    print("="*70)
    
    for phase, success in results.items():
        status = " Success" if success else " Failed"
        print(f"   {phase}: {status}")
    
    print(f"\n   Total Duration: {duration:.1f}s ({duration/60:.1f} minutes)")
    print("="*70)
    
    # Exit with error if any phase failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()
