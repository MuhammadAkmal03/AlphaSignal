"""
Model Loader Service
Loads ML models from Google Cloud Storage
"""
from google.cloud import storage
import pickle
import json
from pathlib import Path
import os

BUCKET_NAME = "alphasignal-models"
LOCAL_CACHE = Path("/tmp/models")

def download_from_gcs(blob_path: str, local_path: Path):
    """Download a file from GCS to local cache"""
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_path)
        
        # Create parent directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        blob.download_to_filename(str(local_path))
        print(f"Downloaded {blob_path} from GCS")
        return True
    except Exception as e:
        print(f"Error downloading {blob_path}: {e}")
        return False

def load_model():
    """Load XGBoost model from GCS or local cache"""
    model_path = LOCAL_CACHE / "xgb_model.pkl"
    
    # Download from GCS if not in cache
    if not model_path.exists():
        print("Model not in cache, downloading from GCS...")
        download_from_gcs("models/xgb_model.pkl", model_path)
    
    # Load model
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        print("Model loaded successfully")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def load_scaler():
    """Load scaler from GCS or local cache"""
    scaler_path = LOCAL_CACHE / "scaler.pkl"
    
    # Download from GCS if not in cache
    if not scaler_path.exists():
        print("Scaler not in cache, downloading from GCS...")
        download_from_gcs("models/scaler.pkl", scaler_path)
    
    # Load scaler
    try:
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        print("Scaler loaded successfully")
        return scaler
    except Exception as e:
        print(f"Error loading scaler: {e}")
        return None

def load_feature_names():
    """Load feature names from GCS or local cache"""
    feature_names_path = LOCAL_CACHE / "feature_names.json"
    
    # Download from GCS if not in cache
    if not feature_names_path.exists():
        print("Feature names not in cache, downloading from GCS...")
        download_from_gcs("models/feature_names.json", feature_names_path)
    
    # Load feature names
    try:
        with open(feature_names_path, "r") as f:
            feature_names = json.load(f)
        print("Feature names loaded successfully")
        return feature_names
    except Exception as e:
        print(f"Error loading feature names: {e}")
        return None

# Initialize models on module import
print("Initializing models from Google Cloud Storage...")
xgb_model = load_model()
scaler = load_scaler()
feature_names = load_feature_names()

if xgb_model and scaler:
    print("✅ All models loaded successfully from GCS!")
else:
    print("⚠️ Warning: Some models failed to load from GCS")
