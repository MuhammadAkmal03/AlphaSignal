"""
GCS Uploader Utility
Uploads prediction and news data to Google Cloud Storage
"""
import os
from pathlib import Path
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = "alphasignal-models"

def get_storage_client():
    """Get authenticated GCS client"""
    # Check for service account key file
    key_file = Path(__file__).resolve().parents[2] / "key.json"
    if key_file.exists():
        return storage.Client.from_service_account_json(str(key_file))
    # Fall back to default credentials (for Cloud Run)
    return storage.Client()

def upload_file_to_gcs(local_path: str, gcs_path: str) -> bool:
    """
    Upload a local file to GCS
    
    Args:
        local_path: Path to local file
        gcs_path: Destination path in GCS bucket (e.g., 'data/prediction/prediction_log.csv')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        
        blob.upload_from_filename(local_path)
        print(f" Uploaded {local_path} -> gs://{BUCKET_NAME}/{gcs_path}")
        return True
    except Exception as e:
        print(f" Error uploading {local_path}: {e}")
        return False

def upload_prediction_data():
    """Upload prediction log and latest prediction to GCS"""
    base = Path(__file__).resolve().parents[2]
    
    files = [
        (base / "data/final/prediction/prediction_log.csv", "data/prediction/prediction_log.csv"),
        (base / "data/final/prediction/latest_prediction.txt", "data/prediction/latest_prediction.txt"),
    ]
    
    for local, gcs in files:
        if local.exists():
            upload_file_to_gcs(str(local), gcs)
        else:
            print(f"File not found: {local}")

def upload_news_data():
    """Upload news sentiment data to GCS"""
    base = Path(__file__).resolve().parents[2]
    
    files = [
        (base / "data/raw/nlp/realtime_news_detailed.csv", "data/news/realtime_news_sentiment.csv"),
        (base / "data/raw/nlp/realtime_news_sentiment.csv", "data/news/daily_sentiment.csv"),
    ]
    
    for local, gcs in files:
        if local.exists():
            upload_file_to_gcs(str(local), gcs)
        else:
            print(f"File not found: {local}")

if __name__ == "__main__":
    print("=== Uploading Prediction Data ===")
    upload_prediction_data()
    print("\n=== Uploading News Data ===")
    upload_news_data()
