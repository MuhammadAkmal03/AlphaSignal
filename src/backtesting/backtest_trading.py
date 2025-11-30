"""
Backtesting Framework - Trading Strategy Simulator
Simulates trading based on model predictions and calculates performance metrics
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

BACKTEST_DIR = Path("backtest_results")
BACKTEST_DIR.mkdir(parents=True, exist_ok=True)


def simulate_trading_strategy(df, initial_capital=10000, transaction_cost=0.001):
    """
    Simulate simple trading strategy based on predictions
    
    Strategy:
    - If prediction > current price: Buy (expect price to go up)
    - If prediction < current price: Sell/Hold cash (expect price to go down)
    
    Args:
        df: DataFrame with 'date', 'prediction', 'actual' columns
        initial_capital: Starting capital in USD
        transaction_cost: Transaction cost as fraction (0.001 = 0.1%)
    
    Returns:
        pd.DataFrame: Trading results with equity curve
    """
    results = []
    capital = initial_capital
    position = 0  # Number of barrels held
    cash = capital
    
    for i in range(len(df) - 1):
        current_price = df.iloc[i]['actual']
        next_price = df.iloc[i + 1]['actual']
        prediction = df.iloc[i]['prediction']
        date = df.iloc[i]['date']
        
        # Trading signal
        if prediction > current_price and position == 0:
            # Buy signal
            barrels_to_buy = cash / (current_price * (1 + transaction_cost))
            position = barrels_to_buy
            cash = 0
            action = 'BUY'
        elif prediction < current_price and position > 0:
            # Sell signal
            cash = position * current_price * (1 - transaction_cost)
            position = 0
            action = 'SELL'
        else:
            action = 'HOLD'
        
        # Calculate portfolio value
        portfolio_value = cash + (position * current_price)
        
        results.append({
            'date': date,
            'price': current_price,
            'prediction': prediction,
            'action': action,
            'position': position,
            'cash': cash,
            'portfolio_value': portfolio_value,
            'return_pct': ((portfolio_value - initial_capital) / initial_capital) * 100
        })
    
    # Close any open position at the end
    if position > 0:
        final_price = df.iloc[-1]['actual']
        cash = position * final_price * (1 - transaction_cost)
        position = 0
    
    results_df = pd.DataFrame(results)
    return results_df


def calculate_trading_metrics(results_df, initial_capital=10000):
    """
    Calculate trading performance metrics
    
    Args:
        results_df: DataFrame from simulate_trading_strategy
        initial_capital: Initial capital
    
    Returns:
        dict: Performance metrics
    """
    final_value = results_df['portfolio_value'].iloc[-1]
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    # Daily returns
    results_df['daily_return'] = results_df['portfolio_value'].pct_change()
    
    # Sharpe Ratio (annualized, assuming 252 trading days)
    mean_return = results_df['daily_return'].mean()
    std_return = results_df['daily_return'].std()
    sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
    
    # Maximum Drawdown
    cumulative_returns = (1 + results_df['daily_return']).cumprod()
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min() * 100
    
    # Win rate
    trades = results_df[results_df['action'].isin(['BUY', 'SELL'])]
    winning_trades = len(trades[trades['return_pct'] > 0])
    total_trades = len(trades) // 2  # Buy + Sell = 1 trade
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    metrics = {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return_pct': total_return,
        'total_return_usd': final_value - initial_capital,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown_pct': max_drawdown,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_daily_return': mean_return * 100,
        'volatility': std_return * 100
    }
    
    return metrics


def calculate_buy_and_hold(df, initial_capital=10000):
    """
    Calculate buy-and-hold baseline performance
    
    Args:
        df: DataFrame with actual prices
        initial_capital: Initial capital
    
    Returns:
        dict: Buy-and-hold metrics
    """
    initial_price = df.iloc[0]['actual']
    final_price = df.iloc[-1]['actual']
    
    barrels = initial_capital / initial_price
    final_value = barrels * final_price
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    return {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return_pct': total_return,
        'total_return_usd': final_value - initial_capital
    }


def plot_equity_curve(results_df, save_path=None):
    """
    Plot equity curve showing portfolio value over time
    
    Args:
        results_df: Trading results DataFrame
        save_path: Path to save plot
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # Equity curve
    axes[0].plot(results_df['date'], results_df['portfolio_value'], 
                linewidth=2, color='#27ae60', label='Strategy')
    axes[0].axhline(results_df['portfolio_value'].iloc[0], 
                   color='gray', linestyle='--', label='Initial Capital')
    axes[0].fill_between(results_df['date'], 
                         results_df['portfolio_value'].iloc[0],
                         results_df['portfolio_value'],
                         alpha=0.3, color='#27ae60')
    axes[0].set_ylabel('Portfolio Value ($)', fontsize=11)
    axes[0].set_title('Equity Curve', fontsize=13, fontweight='bold')
    axes[0].legend(loc='best')
    axes[0].grid(True, alpha=0.3)
    
    # Returns
    axes[1].plot(results_df['date'], results_df['return_pct'], 
                linewidth=2, color='#3498db')
    axes[1].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[1].fill_between(results_df['date'], 0, results_df['return_pct'],
                         alpha=0.3, color='#3498db')
    axes[1].set_xlabel('Date', fontsize=11)
    axes[1].set_ylabel('Return (%)', fontsize=11)
    axes[1].set_title('Cumulative Returns', fontsize=13, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig


def plot_drawdown(results_df, save_path=None):
    """
    Plot drawdown chart
    
    Args:
        results_df: Trading results DataFrame
        save_path: Path to save plot
    """
    # Calculate drawdown
    cumulative_returns = (1 + results_df['daily_return']).cumprod()
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - running_max) / running_max * 100
    
    plt.figure(figsize=(14, 5))
    plt.fill_between(results_df['date'], 0, drawdown, 
                     alpha=0.5, color='#e74c3c', label='Drawdown')
    plt.plot(results_df['date'], drawdown, color='#c0392b', linewidth=2)
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Date', fontsize=11)
    plt.ylabel('Drawdown (%)', fontsize=11)
    plt.title('Portfolio Drawdown', fontsize=13, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f" Saved: {save_path}")
    
    return plt.gcf()


def generate_trading_report(strategy_metrics, bnh_metrics):
    """
    Generate trading performance report
    
    Args:
        strategy_metrics: Strategy performance metrics
        bnh_metrics: Buy-and-hold metrics
    
    Returns:
        str: Formatted report
    """
    outperformance = strategy_metrics['total_return_pct'] - bnh_metrics['total_return_pct']
    
    report = []
    report.append("=" * 60)
    report.append("TRADING STRATEGY PERFORMANCE")
    report.append("=" * 60)
    report.append(f"\n{'Metric':<35} {'Strategy':>12} {'Buy & Hold':>12}")
    report.append("-" * 60)
    report.append(f"{'Initial Capital':<35} ${strategy_metrics['initial_capital']:>11,.2f} ${bnh_metrics['initial_capital']:>11,.2f}")
    report.append(f"{'Final Value':<35} ${strategy_metrics['final_value']:>11,.2f} ${bnh_metrics['final_value']:>11,.2f}")
    report.append(f"{'Total Return':<35} {strategy_metrics['total_return_pct']:>11.2f}% {bnh_metrics['total_return_pct']:>11.2f}%")
    report.append(f"{'Total Return ($)':<35} ${strategy_metrics['total_return_usd']:>11,.2f} ${bnh_metrics['total_return_usd']:>11,.2f}")
    report.append(f"\n{'Outperformance':<35} {outperformance:>11.2f}%")
    report.append(f"\n{'Strategy-Specific Metrics':<35}")
    report.append("-" * 60)
    report.append(f"{'Sharpe Ratio':<35} {strategy_metrics['sharpe_ratio']:>12.2f}")
    report.append(f"{'Maximum Drawdown':<35} {strategy_metrics['max_drawdown_pct']:>11.2f}%")
    report.append(f"{'Total Trades':<35} {strategy_metrics['total_trades']:>12.0f}")
    report.append(f"{'Win Rate':<35} {strategy_metrics['win_rate']:>11.1f}%")
    report.append(f"{'Avg Daily Return':<35} {strategy_metrics['avg_daily_return']:>11.3f}%")
    report.append(f"{'Volatility (Daily)':<35} {strategy_metrics['volatility']:>11.3f}%")
    report.append("=" * 60)
    
    return "\n".join(report)


def run_trading_backtest(df, initial_capital=10000):
    """
    Run complete trading strategy backtest
    
    Args:
        df: DataFrame with predictions and actuals
        initial_capital: Starting capital
    """
    print("=" * 60)
    print("Backtesting - Trading Strategy")
    print("=" * 60)
    
    # Simulate trading
    print(f"\n Simulating trading strategy (Initial capital: ${initial_capital:,.2f})...")
    results_df = simulate_trading_strategy(df, initial_capital)
    
    # Calculate metrics
    print(" Calculating performance metrics...")
    strategy_metrics = calculate_trading_metrics(results_df, initial_capital)
    bnh_metrics = calculate_buy_and_hold(df, initial_capital)
    
    # Generate report
    report = generate_trading_report(strategy_metrics, bnh_metrics)
    print(f"\n{report}")
    
    # Save report
    report_path = BACKTEST_DIR / f"trading_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n Report saved: {report_path}")
    
    # Generate plots
    print("\n Generating visualizations...")
    
    plot1_path = BACKTEST_DIR / "equity_curve.png"
    plot_equity_curve(results_df, plot1_path)
    
    plot2_path = BACKTEST_DIR / "drawdown.png"
    plot_drawdown(results_df, plot2_path)
    
    # Save trading data
    data_path = BACKTEST_DIR / "trading_results.csv"
    results_df.to_csv(data_path, index=False)
    print(f" Data saved: {data_path}")
    
    print("\n" + "=" * 60)
    print(" Trading Backtest Complete!")
    print("=" * 60)
    
    return strategy_metrics, bnh_metrics, results_df


if __name__ == "__main__":
    # Load data from accuracy backtest
    from backtest_accuracy import load_data
    
    df = load_data(lookback_days=180)
    if not df.empty:
        run_trading_backtest(df, initial_capital=10000)
    else:
        print("❌ No data available for backtesting")
