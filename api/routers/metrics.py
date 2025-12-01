"""
Metrics Router
Endpoints for system and model performance metrics
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

router = APIRouter()

PERFORMANCE_METRICS = Path("data/final/prediction/performance_metrics.csv")
PREDICTION_LOG = Path("data/final/prediction/prediction_log.csv")


class ModelMetrics(BaseModel):
    mae: float
    mape: float
    total_predictions: int
    last_updated: str


class SystemHealth(BaseModel):
    status: str
    components: dict
    last_prediction: str


@router.get("/model", response_model=ModelMetrics)
async def get_model_metrics():
    """Get model performance metrics"""
    try:
        if not PERFORMANCE_METRICS.exists():
            raise HTTPException(status_code=404, detail="Performance metrics not found")
        
        df = pd.read_csv(PERFORMANCE_METRICS)
        if df.empty:
            raise HTTPException(status_code=404, detail="No metrics available")
        
        metrics = df.iloc[-1]
        
        # Get total predictions count (unique dates only)
        pred_count = 0
        if PREDICTION_LOG.exists():
            pred_df = pd.read_csv(PREDICTION_LOG)
            # Count unique dates instead of total rows
            pred_df['date'] = pd.to_datetime(pred_df['date'], errors='coerce').dt.normalize()
            pred_count = pred_df['date'].nunique()  # nunique() = number of unique values
        
        return ModelMetrics(
            mae=float(metrics['MAE']),
            mape=float(metrics['MAPE']),
            total_predictions=pred_count,
            last_updated=pd.Timestamp.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading metrics: {str(e)}")


@router.get("/system", response_model=SystemHealth)
async def get_system_health():
    """Get system health status"""
    try:
        components = {
            "predictions": PREDICTION_LOG.exists(),
            "performance_metrics": PERFORMANCE_METRICS.exists(),
            "backtest_results": Path("backtest_results/backtest_data.csv").exists(),
            "rl_evaluation": Path("data/final/rl_eval_momentum/evaluation_summary.csv").exists(),
            "news_data": Path("data/processed/realtime_news_sentiment.csv").exists()
        }
        
        # Get last prediction date
        last_pred = "Unknown"
        if PREDICTION_LOG.exists():
            df = pd.read_csv(PREDICTION_LOG)
            if not df.empty:
                last_pred = str(df.iloc[-1]['date'])
        
        # Determine overall status
        status = "healthy" if all(components.values()) else "degraded"
        
        return SystemHealth(
            status=status,
            components=components,
            last_prediction=last_pred
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking health: {str(e)}")


@router.get("/overview")
async def get_metrics_overview():
    """Get comprehensive metrics overview"""
    try:
        overview = {}
        
        # Model metrics
        if PERFORMANCE_METRICS.exists():
            perf_df = pd.read_csv(PERFORMANCE_METRICS)
            if not perf_df.empty:
                overview['model'] = {
                    "mae": float(perf_df.iloc[-1]['MAE']),
                    "mape": float(perf_df.iloc[-1]['MAPE'])
                }
        
        # Prediction stats
        if PREDICTION_LOG.exists():
            pred_df = pd.read_csv(PREDICTION_LOG)
            overview['predictions'] = {
                "total": len(pred_df),
                "avg_price": float(pred_df['predicted'].mean()),
                "date_range": {
                    "start": str(pred_df['date'].min()),
                    "end": str(pred_df['date'].max())
                }
            }
        
        # Backtest stats
        backtest_file = Path("backtest_results/backtest_data.csv")
        if backtest_file.exists():
            bt_df = pd.read_csv(backtest_file)
            overview['backtest'] = {
                "data_points": len(bt_df),
                "avg_error": float((bt_df['prediction'] - bt_df['actual']).abs().mean())
            }
        
        return overview
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating overview: {str(e)}")
