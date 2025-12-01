"""
RL Agent Router
Endpoints for RL agent recommendations and performance
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

router = APIRouter()

RL_EVAL_DIR = Path("data/final/rl_eval_momentum")


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
        trades_log = RL_EVAL_DIR / "trades_log.csv"
        
        if not trades_log.exists():
            raise HTTPException(
                status_code=404, 
                detail="RL evaluation not found. Run evaluation first."
            )
        
        df = pd.read_csv(trades_log)
        if df.empty:
            raise HTTPException(status_code=404, detail="No RL data available")
        
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
        summary_file = RL_EVAL_DIR / "evaluation_summary.csv"
        
        if not summary_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Performance data not found. Run evaluation first."
            )
        
        df = pd.read_csv(summary_file)
        if df.empty:
            raise HTTPException(status_code=404, detail="No performance data available")
        
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
        backtest_file = RL_EVAL_DIR / "backtest_full.csv"
        
        if not backtest_file.exists():
            raise HTTPException(status_code=404, detail="Equity curve data not found")
        
        df = pd.read_csv(backtest_file)
        
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
