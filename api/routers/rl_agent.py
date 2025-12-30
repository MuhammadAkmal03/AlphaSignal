"""
RL Agent Router
Endpoints for RL agent recommendations and performance
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
from services.gcs_data_loader import read_csv_from_gcs

router = APIRouter()

RL_TRADES_LOG_GCS = "data/rl/trades_log.csv"
RL_EVAL_SUMMARY_GCS = "data/rl/evaluation_summary.csv"
RL_BACKTEST_GCS = "data/rl/backtest_full.csv"


class RLRecommendation(BaseModel):
    action: str
    confidence: float
    reasoning: str


class RLPerformance(BaseModel):
    net_total_return: float
    gross_total_return: float
    sharpe_ratio: float
    max_drawdown: float
    total_costs: float


@router.get("/recommendation", response_model=RLRecommendation)
async def get_rl_recommendation():
    """Get current RL agent recommendation"""
    try:
        # Load latest evaluation results
        df = read_csv_from_gcs(RL_TRADES_LOG_GCS)
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=404, 
                detail="RL evaluation not found. Run evaluation first."
            )
        
        # Get latest action
        latest = df.iloc[-1]
        action_map = {0: "HOLD", 1: "LONG", 2: "SHORT"}
        action = action_map.get(int(latest['action']), "UNKNOWN")
        
        # Calculate confidence based on recent performance
        recent_returns = df.tail(10)['net_return'].mean()
        confidence = min(abs(recent_returns) * 100, 100.0)
        
        # Generate reasoning
        position_map = {0: "neutral", 1: "long", -1: "short"}
        position = position_map.get(int(latest['position']), "unknown")
        
        reasoning = f"Agent is currently {position}. "
        if action == "LONG":
            reasoning += "Model predicts upward price movement."
        elif action == "SHORT":
            reasoning += "Model predicts downward price movement."
        else:
            reasoning += "Holding current position for optimal timing."
        
        return RLRecommendation(
            action=action,
            confidence=float(confidence),
            reasoning=reasoning
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendation: {str(e)}")


@router.get("/performance", response_model=RLPerformance)
async def get_rl_performance():
    """Get RL agent performance metrics"""
    try:
        df = read_csv_from_gcs(RL_EVAL_SUMMARY_GCS)
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail="Performance data not found. Run evaluation first."
            )
        
        metrics = df.iloc[0]
        
        return RLPerformance(
            net_total_return=float(metrics['net_total_return']),
            gross_total_return=float(metrics['gross_total_return']),
            sharpe_ratio=float(metrics['net_sharpe']),
            max_drawdown=float(metrics['net_max_drawdown']),
            total_costs=float(metrics['total_costs'])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading performance: {str(e)}")


@router.get("/equity-curve")
async def get_equity_curve():
    """Get RL agent equity curve data"""
    try:
        df = read_csv_from_gcs(RL_BACKTEST_GCS)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Equity curve data not found")
        
        # Return simplified data for charting
        return {
            "data": df[['step', 'net_equity', 'gross_equity']].to_dict(orient='records'),
            "summary": {
                "initial_equity": 1.0,
                "final_equity": float(df['net_equity'].iloc[-1]),
                "peak_equity": float(df['net_equity'].max()),
                "data_points": len(df)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading equity curve: {str(e)}")
