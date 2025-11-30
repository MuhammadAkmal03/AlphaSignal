"""
Daily Report Scheduler
Runs the complete pipeline and generates daily report
"""
from pathlib import Path
import subprocess
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_daily_pipeline():
    """Run the complete daily pipeline"""
    print("=" * 60)
    print("AlphaSignal - Daily Automated Pipeline")
    print("=" * 60)
    
    scripts = [
        ("Fetching real-time news", "src/data_sources/nlp/realtime_oil_news.py"),
        ("Generating AI news summary", "src/data_sources/nlp/news_summarizer.py"),
        ("Running prediction", "src/orchestrator/run_phase3_predictionpipeline.py"),
        ("Generating daily report", "src/reporting/generate_daily_report.py"),
    ]
    
    for description, script in scripts:
        print(f"\n {description}...")
        try:
            result = subprocess.run(
                [sys.executable, script],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300  
            )
            
            if result.returncode == 0:
                print(f"    Success")
            else:
                print(f"    Failed")
                print(f"   Error: {result.stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            print(f" Timeout (5 minutes)")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Daily pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_daily_pipeline()
