import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(ROOT)

from src.rl.env.rolling_window_env import RollingWindowMomentumEnv

MODEL_PATH = Path("models/ppo_momentum/final_model.zip")
OUT_DIR = Path("data/final/rl_eval_momentum")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def backtest():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}")

    env = RollingWindowMomentumEnv(
        df_path="data/final/features/engineered_features.csv",
        window_size=30,
        flatten_observation=True,
        base_transaction_cost=0.0003,
        base_slippage=0.0007,
        train_transaction_cost=0.00005,
        train_slippage=0.0001,
        use_cost_curriculum=False,  
        min_holding_days=3,
        momentum_coef=0.2,
        vol_penalty=0.1,
        xgb_align_coef=0.2,
        verbose=False,
    )

    model = PPO.load(str(MODEL_PATH))

    obs, info = env.reset()
    done = False

    history = {
        "step": [], "price": [], "action": [], "position": [],
        "raw_return": [], "net_return": [], "txn_cost": [], "slippage": [], "unrealized_profit": []
    }

    prev_price = float(info.get("price", env.df.loc[env.current_step, "close_price"]))

    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        cur_step = int(info.get("step", env.current_step))
        price = float(info.get("price", env.df.loc[cur_step, "close_price"])) if "price" in info else float(env.df.loc[cur_step, "close_price"])
        raw_r = float(info.get("raw_return", 0.0))
        net_r = float(info.get("net_return", reward)) if "net_return" in info else float(reward)
        txn = float(info.get("txn_cost", 0.0))
        slip = float(info.get("slippage", 0.0))
        unreal = float(info.get("unrealized_profit", 0.0))

        history["step"].append(cur_step)
        history["price"].append(price)
        history["action"].append(int(action))
        history["position"].append(int(info.get("position", env.position)))
        history["raw_return"].append(raw_r)
        history["net_return"].append(net_r)
        history["txn_cost"].append(txn)
        history["slippage"].append(slip)
        history["unrealized_profit"].append(unreal)

        prev_price = price

    df = pd.DataFrame(history)
    if df.empty:
        raise RuntimeError("No steps recorded during evaluation.")

    df["gross_equity"] = (1 + df["raw_return"]).cumprod()
    df["net_equity"] = (1 + df["net_return"]).cumprod()
    df["rolling_sharpe_net"] = df["net_return"].rolling(30).mean() / (df["net_return"].rolling(30).std() + 1e-9)
    df["net_cummax"] = df["net_equity"].cummax()
    df["net_drawdown"] = (df["net_equity"] - df["net_cummax"]) / df["net_cummax"]

    df.to_csv(OUT_DIR / "backtest_full.csv", index=False)
    df[["step","action","price","position","raw_return","net_return","txn_cost","slippage","unrealized_profit"]].to_csv(OUT_DIR / "trades_log.csv", index=False)

    summary = {
        "gross_total_return": float(df["gross_equity"].iloc[-1] - 1.0),
        "net_total_return": float(df["net_equity"].iloc[-1] - 1.0),
        "net_sharpe": float(df["net_return"].mean() / (df["net_return"].std() + 1e-9)),
        "net_max_drawdown": float(df["net_drawdown"].min()),
        "avg_cost_per_step": float((df["txn_cost"] + df["slippage"]).mean()),
        "total_costs": float((df["txn_cost"] + df["slippage"]).sum()),
    }

    pd.DataFrame([summary]).to_csv(OUT_DIR / "evaluation_summary.csv", index=False)
    return df, summary

def plot_results(df):
    plt.figure(figsize=(10,4))
    plt.plot(df["step"], df["net_equity"], label="Net equity")
    plt.title("Net equity")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "net_equity.png")
    plt.close()

    plt.figure(figsize=(10,3))
    plt.plot(df["step"], df["rolling_sharpe_net"])
    plt.title("Rolling sharpe (net)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "rolling_sharpe.png")
    plt.close()

if __name__ == "__main__":
    df, summary = backtest()
    plot_results(df)
    print("Evaluation completed. Results saved to:", OUT_DIR)
    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
