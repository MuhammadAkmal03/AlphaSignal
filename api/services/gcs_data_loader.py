"""
GCS Data Loader
Helper functions to read data files from Google Cloud Storage
"""
from google.cloud import storage
import pandas as pd
import pickle
from pathlib import Path
from typing import Optional

BUCKET_NAME = "alphasignal-models"
LOCAL_CACHE = Path("/tmp/data")

def download_file_from_gcs(gcs_path: str, local_path: Path) -> bool:
    """Download a file from GCS to local cache"""
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        
        # Create parent directory
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download
        blob.download_to_filename(str(local_path))
        print(f"✅ Downloaded {gcs_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading {gcs_path}: {e}")
        return False

def read_csv_from_gcs(gcs_path: str) -> Optional[pd.DataFrame]:
    """Read CSV file from GCS"""
    local_path = LOCAL_CACHE / gcs_path.replace("/", "_")
    
    # Download if not cached
    if not local_path.exists():
        if not download_file_from_gcs(gcs_path, local_path):
            return None
    
    try:
        df = pd.read_csv(local_path)
        return df
    except Exception as e:
        print(f"Error reading CSV {gcs_path}: {e}")
        return None

def read_pickle_from_gcs(gcs_path: str) -> Optional[any]:
    """Read pickle file from GCS"""
    local_path = LOCAL_CACHE / gcs_path.replace("/", "_")
    
    # Download if not cached
    if not local_path.exists():
        if not download_file_from_gcs(gcs_path, local_path):
            return None
    
    try:
        with open(local_path, "rb") as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        print(f"Error reading pickle {gcs_path}: {e}")
        return None

def read_text_from_gcs(gcs_path: str) -> Optional[str]:
    """Read text file from GCS"""
    local_path = LOCAL_CACHE / gcs_path.replace("/", "_")
    
    # Download if not cached
    if not local_path.exists():
        if not download_file_from_gcs(gcs_path, local_path):
            return None
    
    try:
        with open(local_path, "r") as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading text {gcs_path}: {e}")
        return None
