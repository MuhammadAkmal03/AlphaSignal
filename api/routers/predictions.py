"""
Predictions Router
Endpoints for price predictions
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import sys

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.gcs_data_loader import read_csv_from_gcs, read_text_from_gcs

router = APIRouter()

# GCS Paths
PREDICTION_LOG_GCS = "data/prediction/prediction_log.csv"
LATEST_PREDICTION_GCS = "data/prediction/latest_prediction.txt"


class PredictionResponse(BaseModel):
    date: str
    predicted_price: float
    timestamp: str


class PredictionHistoryResponse(BaseModel):
    predictions: list[PredictionResponse]
    count: int


@router.get("/latest", response_model=PredictionResponse)
async def get_latest_prediction():
    """Get the most recent prediction"""
    try:
        # Try to read from prediction log in GCS
        df = read_csv_from_gcs(PREDICTION_LOG_GCS)
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            return PredictionResponse(
                date=str(latest['date']),
                predicted_price=float(latest['predicted']),
                timestamp=datetime.now().isoformat()
            )
        
        # Fallback to latest_prediction.txt
        price_str = read_text_from_gcs(LATEST_PREDICTION_GCS)
        if price_str:
            price = float(price_str.strip())
            return PredictionResponse(
                date=datetime.now().strftime('%Y-%m-%d'),
                predicted_price=price,
                timestamp=datetime.now().isoformat()
            )
        
        raise HTTPException(status_code=404, detail="No predictions available")

    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading prediction: {str(e)}")


@router.get("/previous", response_model=PredictionResponse)
async def get_previous_prediction():
    """Get the second-to-last prediction (for comparison with latest)"""
    try:
        df = read_csv_from_gcs(PREDICTION_LOG_GCS)
        if df is None or len(df) < 2:
            # If we don't have 2 predictions yet, return the first one
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return PredictionResponse(
                    date=str(latest['date']),
                    predicted_price=float(latest['predicted']),
                    timestamp=datetime.now().isoformat()
                )
            raise HTTPException(status_code=404, detail="Not enough predictions available")
        
        # Get second-to-last prediction
        previous = df.iloc[-2]
        return PredictionResponse(
            date=str(previous['date']),
            predicted_price=float(previous['predicted']),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading previous prediction: {str(e)}")


@router.get("/history", response_model=PredictionHistoryResponse)
async def get_prediction_history(days: Optional[int] = 30):
    """Get historical predictions"""
    try:
        df = read_csv_from_gcs(PREDICTION_LOG_GCS)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Prediction log not found")
        # Handle mixed date formats (timestamps and dates)
        print(f"Loaded {len(df)} rows from prediction log")
        print(f"Columns: {df.columns.tolist()}")
        print(f"First few dates: {df['date'].head().tolist()}")
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['date'])
        print(f"After date parsing: {len(df)} valid rows")
        
        # Sort by date descending (most recent first)
        df = df.sort_values('date', ascending=False)
        
        # Get the most recent N predictions (where N = days parameter)
        # This works regardless of whether dates are in past or future
        df = df.head(days)
        
        # Handle NaNs in predicted column
        df['predicted'] = df['predicted'].fillna(0.0)
        
        predictions = []
        for _, row in df.iterrows():
            try:
                if pd.isna(row['date']):
                    continue
                    
                predictions.append(PredictionResponse(
                    date=row['date'].strftime('%Y-%m-%d'),
                    predicted_price=float(row['predicted']),
                    timestamp=row['date'].isoformat()
                ))
            except Exception as e:
                print(f"Skipping row due to error: {e}")
                continue
        
        print(f"Returning {len(predictions)} predictions")
        return PredictionHistoryResponse(
            predictions=predictions,
            count=len(predictions)
        )
    
    except Exception as e:
        import traceback
        print(f"Error in get_prediction_history: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error loading history: {str(e)}")


@router.get("/stats")
async def get_prediction_stats():
    """Get prediction statistics"""
    try:
        if not PREDICTION_LOG.exists():
            raise HTTPException(status_code=404, detail="Prediction log not found")
        
        df = pd.read_csv(PREDICTION_LOG)
        
        return {
            "total_predictions": len(df),
            "avg_predicted_price": float(df['predicted'].mean()),
            "min_predicted_price": float(df['predicted'].min()),
            "max_predicted_price": float(df['predicted'].max()),
            "date_range": {
                "start": str(df['date'].min()),
                "end": str(df['date'].max())
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")
