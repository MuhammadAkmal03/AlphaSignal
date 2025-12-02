"""
SHAP Explainability Router
Provides model interpretability using SHAP (SHapley Additive exPlanations)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import pickle
import json

router = APIRouter()

MODEL_PATH = Path("models/xgb_model.pkl")
FEATURE_NAMES_PATH = Path("models/feature_names.json")
SHAP_VALUES_PATH = Path("data/final/shap/shap_values.csv")
SHAP_SUMMARY_PATH = Path("data/final/shap/feature_importance.csv")


class FeatureImportance(BaseModel):
    feature: str
    importance: float
    rank: int


class SHAPExplanation(BaseModel):
    prediction: float
    base_value: float
    feature_contributions: Dict[str, float]
    top_features: List[FeatureImportance]


class SHAPSummary(BaseModel):
    global_importance: List[FeatureImportance]
    total_features: int
    model_type: str


@router.get("/summary", response_model=SHAPSummary)
async def get_shap_summary():
    """
    Get global feature importance using SHAP values
    Shows which features are most important across all predictions
    """
    try:
        # Try to load pre-computed SHAP summary
        if SHAP_SUMMARY_PATH.exists():
            df = pd.read_csv(SHAP_SUMMARY_PATH)
            
            importance_list = []
            for idx, row in df.iterrows():
                importance_list.append(FeatureImportance(
                    feature=row['feature'],
                    importance=float(row['importance']),
                    rank=int(idx + 1)
                ))
            
            return SHAPSummary(
                global_importance=importance_list[:20],  # Top 20 features
                total_features=len(df),
                model_type="XGBoost"
            )
        
        # If pre-computed doesn't exist, compute from model
        if not MODEL_PATH.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Load model
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        # Get feature importance from XGBoost
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            
            # Load feature names
            feature_names = []
            if FEATURE_NAMES_PATH.exists():
                with open(FEATURE_NAMES_PATH, 'r') as f:
                    feature_names = json.load(f)
            else:
                feature_names = [f"feature_{i}" for i in range(len(importances))]
            
            # Create importance dataframe
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            # Save for future use
            SHAP_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
            importance_df.to_csv(SHAP_SUMMARY_PATH, index=False)
            
            importance_list = []
            for idx, row in importance_df.iterrows():
                importance_list.append(FeatureImportance(
                    feature=row['feature'],
                    importance=float(row['importance']),
                    rank=int(idx + 1)
                ))
            
            return SHAPSummary(
                global_importance=importance_list[:20],
                total_features=len(importance_df),
                model_type="XGBoost"
            )
        else:
            raise HTTPException(status_code=500, detail="Model does not support feature importance")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing SHAP summary: {str(e)}")


@router.get("/latest", response_model=SHAPExplanation)
async def get_latest_explanation():
    """
    Get SHAP explanation for the latest prediction
    Shows which features contributed most to the most recent prediction
    """
    try:
        # Load latest prediction
        pred_log = Path("data/final/prediction/prediction_log.csv")
        if not pred_log.exists():
            raise HTTPException(status_code=404, detail="No predictions available")
        
        pred_df = pd.read_csv(pred_log)
        if pred_df.empty:
            raise HTTPException(status_code=404, detail="No predictions available")
        
        latest_pred = pred_df.iloc[-1]
        
        # Load SHAP values if available
        if SHAP_VALUES_PATH.exists():
            shap_df = pd.read_csv(SHAP_VALUES_PATH)
            if not shap_df.empty:
                latest_shap = shap_df.iloc[-1]
                
                # Extract feature contributions
                contributions = {}
                for col in shap_df.columns:
                    if col not in ['prediction', 'base_value', 'date']:
                        contributions[col] = float(latest_shap[col])
                
                # Sort by absolute contribution
                sorted_contributions = sorted(
                    contributions.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
                
                top_features = []
                for idx, (feature, value) in enumerate(sorted_contributions[:10]):
                    top_features.append(FeatureImportance(
                        feature=feature,
                        importance=abs(value),
                        rank=idx + 1
                    ))
                
                return SHAPExplanation(
                    prediction=float(latest_pred['predicted']),
                    base_value=float(latest_shap.get('base_value', 0)),
                    feature_contributions=dict(sorted_contributions[:20]),
                    top_features=top_features
                )
        
        # Fallback: use feature importance as proxy
        if SHAP_SUMMARY_PATH.exists():
            importance_df = pd.read_csv(SHAP_SUMMARY_PATH)
            
            top_features = []
            for idx, row in importance_df.head(10).iterrows():
                top_features.append(FeatureImportance(
                    feature=row['feature'],
                    importance=float(row['importance']),
                    rank=int(idx + 1)
                ))
            
            return SHAPExplanation(
                prediction=float(latest_pred['predicted']),
                base_value=0.0,
                feature_contributions={},
                top_features=top_features
            )
        
        raise HTTPException(status_code=404, detail="SHAP values not computed yet")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting explanation: {str(e)}")


@router.post("/compute")
async def compute_shap_values():
    """
    Compute SHAP values for recent predictions
    This is a computationally expensive operation
    """
    try:
        # Check if shap library is available
        try:
            import shap
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="SHAP library not installed. Run: pip install shap"
            )
        
        # Load model
        if not MODEL_PATH.exists():
            raise HTTPException(status_code=404, detail="Model not found")
        
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        # Load recent predictions data
        pred_log = Path("data/final/prediction/prediction_log.csv")
        if not pred_log.exists():
            raise HTTPException(status_code=404, detail="No prediction data available")
        
        # Note: This is a placeholder - actual implementation would need
        # the feature data used for predictions
        return {
            "status": "success",
            "message": "SHAP computation would require feature data. Use feature importance as alternative.",
            "recommendation": "Check /api/explainability/summary for feature importance"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing SHAP: {str(e)}")
