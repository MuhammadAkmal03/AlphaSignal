"""
Complete Backtesting Framework Runner
Runs both accuracy and trading backtests and generates comprehensive report
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backtesting.backtest_accuracy import run_accuracy_backtest, load_data
from src.backtesting.backtest_trading import run_trading_backtest
from datetime import datetime


def run_complete_backtest(lookback_days=180, initial_capital=10000):
    """
    Run complete backtesting suite
    
    Args:
        lookback_days: Number of days to backtest
        initial_capital: Starting capital for trading simulation
    """
    print("\n" + "=" * 70)
    print(" " * 20 + "ALPHASIGNAL BACKTEST SUITE")
    print("=" * 70)
    print(f"\nBacktest Period: Last {lookback_days} days")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 70)
    
    # Load data
    print("\n[1/3] Loading historical data...")
    df = load_data(lookback_days)
    
    if df.empty:
        print("\n ERROR: No prediction data available")
        print("\nTo generate predictions:")
        print("  1. Run: python src/orchestrator/run_phase3_predictionpipeline.py")
        print("  2. Wait for predictions to accumulate over time")
        print("  3. Re-run this backtest")
        return
    
    print(f" Loaded {len(df)} predictions from {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    
    # Run accuracy backtest
    print("\n" + "=" * 70)
    print("[2/3] Running Prediction Accuracy Backtest...")
    print("=" * 70)
    accuracy_metrics, accuracy_df = run_accuracy_backtest(lookback_days)
    
    # Run trading backtest
    print("\n" + "=" * 70)
    print("[3/3] Running Trading Strategy Backtest...")
    print("=" * 70)
    strategy_metrics, bnh_metrics, trading_df = run_trading_backtest(df, initial_capital)
    
    # Generate summary
    print("\n" + "=" * 70)
    print(" " * 25 + "BACKTEST SUMMARY")
    print("=" * 70)
    
    print("\n PREDICTION ACCURACY")
    print("-" * 70)
    print(f"  Mean Absolute % Error (MAPE):  {accuracy_metrics['mape']:.2f}%")
    print(f"  Directional Accuracy:           {accuracy_metrics['directional_accuracy']:.1f}%")
    print(f"  Correlation:                    {accuracy_metrics['correlation']:.3f}")
    
    print("\n TRADING PERFORMANCE")
    print("-" * 70)
    print(f"  Strategy Return:                {strategy_metrics['total_return_pct']:+.2f}%")
    print(f"  Buy & Hold Return:              {bnh_metrics['total_return_pct']:+.2f}%")
    print(f"  Outperformance:                 {strategy_metrics['total_return_pct'] - bnh_metrics['total_return_pct']:+.2f}%")
    print(f"  Sharpe Ratio:                   {strategy_metrics['sharpe_ratio']:.2f}")
    print(f"  Maximum Drawdown:               {strategy_metrics['max_drawdown_pct']:.2f}%")
    print(f"  Win Rate:                       {strategy_metrics['win_rate']:.1f}%")
    
    print("\n OUTPUT FILES")
    print("-" * 70)
    print("  Reports:")
    print("    - backtest_results/accuracy_report_*.txt")
    print("    - backtest_results/trading_report_*.txt")
    print("\n  Visualizations:")
    print("    - backtest_results/predictions_vs_actual.png")
    print("    - backtest_results/error_distribution.png")
    print("    - backtest_results/equity_curve.png")
    print("    - backtest_results/drawdown.png")
    print("\n  Data:")
    print("    - backtest_results/backtest_data.csv")
    print("    - backtest_results/trading_results.csv")
    
    print("\n" + "=" * 70)
    print(" BACKTEST COMPLETE!")
    print("=" * 70)
    print(f"\nView results in: {Path('backtest_results').absolute()}")
    print("\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run AlphaSignal Backtesting Suite')
    parser.add_argument('--days', type=int, default=180, 
                       help='Number of days to backtest (default: 180)')
    parser.add_argument('--capital', type=float, default=10000,
                       help='Initial capital for trading simulation (default: 10000)')
    
    args = parser.parse_args()
    
    run_complete_backtest(lookback_days=args.days, initial_capital=args.capital)
