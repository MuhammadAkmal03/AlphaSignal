"""
Backtesting Router
Endpoints for running and retrieving backtest results
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import pandas as pd
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backtesting.backtest_accuracy import run_accuracy_backtest
from src.backtesting.backtest_trading import run_trading_backtest, calculate_buy_and_hold

router = APIRouter()

BACKTEST_DIR = Path("backtest_results")


class BacktestRequest(BaseModel):
    lookback_days: int = 180
    initial_capital: float = 10000.0


class BacktestResponse(BaseModel):
    accuracy_metrics: dict
    trading_metrics: dict
    buy_hold_metrics: dict
    equity_curve: list
    trades: list
    data_points: int
    timestamp: str


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """Run a complete backtest"""
    try:
        # Run accuracy backtest
        accuracy_metrics, accuracy_df = run_accuracy_backtest(request.lookback_days)
        
        if accuracy_df.empty:
            raise HTTPException(status_code=404, detail="No data available for backtesting")
        
        # Run trading backtest
        strategy_metrics, bnh_metrics, trading_df = run_trading_backtest(
            accuracy_df, 
            request.initial_capital
        )
        
        # Calculate drawdown for equity curve
        # Note: daily_return is already calculated in calculate_trading_metrics but not in trading_df returned
        trading_df['daily_return'] = trading_df['portfolio_value'].pct_change()
        cumulative_returns = (1 + trading_df['daily_return']).cumprod()
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / running_max * 100
        trading_df['drawdown'] = drawdown.fillna(0)
        
        # Prepare equity curve data
        equity_curve = trading_df[['date', 'portfolio_value', 'drawdown']].rename(
            columns={'portfolio_value': 'value'}
        ).to_dict(orient='records')
        
        # Prepare trades data (filter for active trades)
        trades_df = trading_df[trading_df['action'].isin(['BUY', 'SELL'])].copy()
        trades = trades_df[['date', 'action', 'price', 'return_pct']].rename(
            columns={'return_pct': 'return'}
        ).to_dict(orient='records')
        
        return BacktestResponse(
            accuracy_metrics=accuracy_metrics,
            trading_metrics=strategy_metrics,
            buy_hold_metrics=bnh_metrics,
            equity_curve=equity_curve,
            trades=trades,
            data_points=len(accuracy_df),
            timestamp=pd.Timestamp.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/results/latest")
async def get_latest_results():
    """Get the most recent backtest results"""
    try:
        # Check for latest backtest data
        backtest_data = BACKTEST_DIR / "backtest_data.csv"
        trading_data = BACKTEST_DIR / "trading_results.csv"
        
        if not backtest_data.exists() or not trading_data.exists():
            raise HTTPException(status_code=404, detail="No backtest results found. Run a backtest first.")
        
        # Load data
        df_accuracy = pd.read_csv(backtest_data)
        df_trading = pd.read_csv(trading_data)
        
        return {
            "accuracy_data": df_accuracy.to_dict(orient='records'),
            "trading_data": df_trading.to_dict(orient='records'),
            "summary": {
                "total_predictions": len(df_accuracy),
                "total_trades": len(df_trading),
                "date_range": {
                    "start": str(df_accuracy['date'].min()),
                    "end": str(df_accuracy['date'].max())
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading results: {str(e)}")


@router.get("/charts")
async def get_backtest_charts():
    """Get paths to backtest visualization charts"""
    try:
        charts = {
            "predictions_vs_actual": str(BACKTEST_DIR / "predictions_vs_actual.png"),
            "error_distribution": str(BACKTEST_DIR / "error_distribution.png"),
            "equity_curve": str(BACKTEST_DIR / "equity_curve.png"),
            "drawdown": str(BACKTEST_DIR / "drawdown.png")
        }
        
        # Check which charts exist
        available_charts = {
            name: path for name, path in charts.items()
            if Path(path).exists()
        }
        
        if not available_charts:
            raise HTTPException(status_code=404, detail="No charts available. Run a backtest first.")
        
        return {"charts": available_charts}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading charts: {str(e)}")
