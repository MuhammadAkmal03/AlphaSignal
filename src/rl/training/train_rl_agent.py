import os
import sys
from pathlib import Path
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import ProgressBarCallback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(ROOT)

from src.rl.env.rolling_window_env import RollingWindowMomentumEnv

MODEL_DIR = Path("models/ppo_momentum")
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "final_model"

def train_ppo(total_timesteps: int = 200_000):
    print("Initializing momentum environment (cost curriculum ON for training)...")

    env = RollingWindowMomentumEnv(
        df_path="data/final/features/engineered_features.csv",
        window_size=30,
        flatten_observation=True,
        base_transaction_cost=0.0003,
        base_slippage=0.0007,
        train_transaction_cost=0.00005,
        train_slippage=0.0001,
        use_cost_curriculum=True,
        min_holding_days=3,
        momentum_coef=0.2,
        vol_penalty=0.1,
        xgb_align_coef=0.2,
        verbose=False,
    )

    print("Observation space:", env.observation_space)
    print("Action space:", env.action_space)

    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        tensorboard_log="logs/ppo_momentum/",
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=256,
        gamma=0.99,
    )

    print("Starting training...")
    model.learn(total_timesteps=total_timesteps, callback=ProgressBarCallback())

    print("Saving model...")
    model.save(str(MODEL_PATH))
    print(f"Model saved at: {MODEL_PATH}")

if __name__ == "__main__":
    train_ppo(total_timesteps=200_000)
