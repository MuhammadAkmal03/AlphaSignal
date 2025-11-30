"""
Backtesting Framework - Prediction Accuracy Module
Tests model predictions against actual historical prices
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Paths
MASTER_DATASET = Path("data/final/master_dataset_cleaned.csv")
PREDICTION_LOG = Path("data/final/prediction/prediction_log.csv")
BACKTEST_DIR = Path("backtest_results")
BACKTEST_DIR.mkdir(parents=True, exist_ok=True)


def load_data(lookback_days=180):
    """
    Load actual prices and predictions for backtesting
    
    Args:
        lookback_days: Number of days to backtest
    
    Returns:
        pd.DataFrame: Combined data with predictions and actuals
    """
    # Load actual prices
    df_actual = pd.read_csv(MASTER_DATASET)
    df_actual['date'] = pd.to_datetime(df_actual['date'], errors='coerce').dt.normalize()
    df_actual = df_actual.dropna(subset=['date'])
    df_actual = df_actual[['date', 'close_price']].rename(columns={'close_price': 'actual'})
    
    # Load predictions
    if not PREDICTION_LOG.exists():
        print(" No prediction log found. Run predictions first.")
        return pd.DataFrame()
    
    df_pred = pd.read_csv(PREDICTION_LOG)
    df_pred['date'] = pd.to_datetime(df_pred['date'], errors='coerce').dt.normalize()
    df_pred = df_pred.dropna(subset=['date'])
    df_pred = df_pred.rename(columns={'predicted': 'prediction'})
    
    # Merge predictions with actual prices (next day)
    # Prediction on date X is for price on date X+1
    df_pred['target_date'] = df_pred['date'] + timedelta(days=1)
    
    df_combined = df_pred.merge(
        df_actual,
        left_on='target_date',
        right_on='date',
        how='inner',
        suffixes=('_pred', '_actual')
    )
    
    # Keep only recent data
    cutoff = datetime.now() - timedelta(days=lookback_days)
    df_combined = df_combined[df_combined['date_pred'] >= cutoff]
    
    # Clean up columns
    df_combined = df_combined[['date_pred', 'prediction', 'actual']].rename(
        columns={'date_pred': 'date'}
    )
    
    return df_combined.sort_values('date')


def calculate_accuracy_metrics(df):
    """
    Calculate prediction accuracy metrics
    
    Args:
        df: DataFrame with 'prediction' and 'actual' columns
    
    Returns:
        dict: Accuracy metrics
    """
    if df.empty:
        return {}
    
    # Basic error metrics
    errors = df['prediction'] - df['actual']
    abs_errors = np.abs(errors)
    pct_errors = (abs_errors / df['actual']) * 100
    
    # Directional accuracy
    df['pred_direction'] = (df['prediction'] > df['actual'].shift(1)).astype(int)
    df['actual_direction'] = (df['actual'] > df['actual'].shift(1)).astype(int)
    directional_accuracy = (df['pred_direction'] == df['actual_direction']).mean() * 100
    
    metrics = {
        'mae': abs_errors.mean(),
        'rmse': np.sqrt((errors ** 2).mean()),
        'mape': pct_errors.mean(),
        'max_error': abs_errors.max(),
        'directional_accuracy': directional_accuracy,
        'total_predictions': len(df),
        'avg_actual_price': df['actual'].mean(),
        'avg_predicted_price': df['prediction'].mean(),
        'correlation': df['prediction'].corr(df['actual'])
    }
    
    return metrics


def plot_predictions_vs_actual(df, save_path=None):
    """
    Plot predictions vs actual prices
    
    Args:
        df: DataFrame with predictions and actuals
        save_path: Path to save the plot
    """
    plt.figure(figsize=(14, 6))
    
    plt.plot(df['date'], df['actual'], label='Actual Price', linewidth=2, color='#2c3e50')
    plt.plot(df['date'], df['prediction'], label='Predicted Price', linewidth=2, 
             color='#e74c3c', linestyle='--', alpha=0.8)
    
    plt.fill_between(df['date'], df['actual'], df['prediction'], alpha=0.2, color='gray')
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Brent Crude Price ($)', fontsize=12)
    plt.title('Model Predictions vs Actual Prices', fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return plt.gcf()


def plot_error_distribution(df, save_path=None):
    """
    Plot error distribution
    
    Args:
        df: DataFrame with predictions and actuals
        save_path: Path to save the plot
    """
    errors = df['prediction'] - df['actual']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Error histogram
    axes[0].hist(errors, bins=30, color='#3498db', alpha=0.7, edgecolor='black')
    axes[0].axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Error')
    axes[0].set_xlabel('Prediction Error ($)', fontsize=11)
    axes[0].set_ylabel('Frequency', fontsize=11)
    axes[0].set_title('Error Distribution', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Error over time
    axes[1].plot(df['date'], errors, color='#e74c3c', alpha=0.6)
    axes[1].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[1].fill_between(df['date'], 0, errors, alpha=0.3, color='#e74c3c')
    axes[1].set_xlabel('Date', fontsize=11)
    axes[1].set_ylabel('Prediction Error ($)', fontsize=11)
    axes[1].set_title('Error Over Time', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def generate_accuracy_report(df, metrics):
    """
    Generate text report of accuracy metrics
    
    Args:
        df: DataFrame with predictions
        metrics: Dictionary of calculated metrics
    
    Returns:
        str: Formatted report
    """
    report = []
    report.append("=" * 60)
    report.append("PREDICTION ACCURACY REPORT")
    report.append("=" * 60)
    report.append(f"\nBacktest Period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    report.append(f"Total Predictions: {metrics['total_predictions']}")
    report.append(f"\n{'Metric':<30} {'Value':>15}")
    report.append("-" * 60)
    report.append(f"{'Mean Absolute Error (MAE)':<30} ${metrics['mae']:>14.2f}")
    report.append(f"{'Root Mean Squared Error (RMSE)':<30} ${metrics['rmse']:>14.2f}")
    report.append(f"{'Mean Absolute % Error (MAPE)':<30} {metrics['mape']:>14.2f}%")
    report.append(f"{'Maximum Error':<30} ${metrics['max_error']:>14.2f}")
    report.append(f"{'Directional Accuracy':<30} {metrics['directional_accuracy']:>14.1f}%")
    report.append(f"{'Correlation (Pred vs Actual)':<30} {metrics['correlation']:>14.3f}")
    report.append(f"\n{'Average Actual Price':<30} ${metrics['avg_actual_price']:>14.2f}")
    report.append(f"{'Average Predicted Price':<30} ${metrics['avg_predicted_price']:>14.2f}")
    report.append("=" * 60)
    
    return "\n".join(report)


def run_accuracy_backtest(lookback_days=180):
    """
    Run complete prediction accuracy backtest
    
    Args:
        lookback_days: Number of days to backtest
    """
    print("=" * 60)
    print("Backtesting - Prediction Accuracy")
    print("=" * 60)
    
    # Load data
    print(f"\n Loading data (last {lookback_days} days)...")
    df = load_data(lookback_days)
    
    if df.empty:
        print(" No data available for backtesting")
        return None
    
    print(f" Loaded {len(df)} predictions")
    
    # Calculate metrics
    print("\n Calculating accuracy metrics...")
    metrics = calculate_accuracy_metrics(df)
    
    # Generate report
    report = generate_accuracy_report(df, metrics)
    print(f"\n{report}")
    
    # Save report
    report_path = BACKTEST_DIR / f"accuracy_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n Report saved: {report_path}")
    
    # Generate plots
    print("\n Generating visualizations...")
    
    plot1_path = BACKTEST_DIR / "predictions_vs_actual.png"
    plot_predictions_vs_actual(df, plot1_path)
    
    plot2_path = BACKTEST_DIR / "error_distribution.png"
    plot_error_distribution(df, plot2_path)
    
    # Save data
    data_path = BACKTEST_DIR / "backtest_data.csv"
    df.to_csv(data_path, index=False)
    print(f" Data saved: {data_path}")
    
    print("\n" + "=" * 60)
    print(" Accuracy Backtest Complete!")
    print("=" * 60)
    
    return metrics, df


if __name__ == "__main__":
    run_accuracy_backtest(lookback_days=180)
