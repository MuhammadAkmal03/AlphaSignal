"""
- Minimal temporal-momentum environment tuned for PPO.
- Min holding days = 3 (agent can flip after 3 days).
- Reward = net_return + momentum_coef * momentum_7 - vol_penalty * volatility_30 + xgb_align_coef * xgb_strength
- Cost curriculum supported (reduced costs during training).
"""

from pathlib import Path
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

class RollingWindowMomentumEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        df_path: str = "data/final/features/engineered_features.csv",
        window_size: int = 30,
        flatten_observation: bool = True,
        # costs (base realistic; train_* for curriculum)
        base_transaction_cost: float = 0.0003,
        base_slippage: float = 0.0007,
        train_transaction_cost: float = 0.00005,
        train_slippage: float = 0.0001,
        use_cost_curriculum: bool = True,
        # momentum reward shaping
        min_holding_days: int = 3,
        momentum_coef: float = 0.2,
        vol_penalty: float = 0.1,
        xgb_align_coef: float = 0.2,
        verbose: bool = False,
    ):
        super().__init__()

        self.df_path = Path(df_path)
        if not self.df_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.df_path}")

        self.df = pd.read_csv(self.df_path)
        if "date" in self.df.columns:
            self.df["date"] = pd.to_datetime(self.df["date"])
            self.df = self.df.sort_values("date").reset_index(drop=True)

        self.window = int(window_size)
        self.flatten = bool(flatten_observation)

        # costs and curriculum
        self.base_tx = float(base_transaction_cost)
        self.base_slip = float(base_slippage)
        self.train_tx = float(train_transaction_cost)
        self.train_slip = float(train_slippage)
        self.use_cost_curriculum = bool(use_cost_curriculum)
        self.transaction_cost = self.train_tx if self.use_cost_curriculum else self.base_tx
        self.slippage = self.train_slip if self.use_cost_curriculum else self.base_slip

        # reward shaping hyperparameters
        self.min_holding_days = int(min_holding_days)
        self.momentum_coef = float(momentum_coef)
        self.vol_penalty = float(vol_penalty)
        self.xgb_align_coef = float(xgb_align_coef)

        self.verbose = bool(verbose)

        # prepare features
        self._ensure_features()

        # feature list used by this env
        self.feature_names = [
            "close_price",
            "price_return",
            "momentum_7",
            "volatility_30",
            "wti_price",
            "wti_return",
            "diesel_price",
            "xgb_predicted_return",
            "xgb_trend",
        ]
        self.feature_names = [f for f in self.feature_names if f in self.df.columns]

        # observation space (flattened window of features)
        if self.flatten:
            obs_shape = (len(self.feature_names) * self.window,)
        else:
            obs_shape = (self.window, len(self.feature_names))

        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=obs_shape, dtype=np.float32)
        self.action_space = spaces.Discrete(3)  # 0 hold, 1 long, 2 short

        # indices
        self.start_index = self.window
        self.end_index = len(self.df) - 1

        # state
        self.current_step = int(self.start_index)
        self.position = 0
        self.entry_price = 0.0
        self.holding_days = 0
        self.returns = []
        self.unrealized_profit = 0.0

    def _ensure_features(self):
        df = self.df

        if "close_price" not in df.columns:
            raise ValueError("close_price missing in dataset")

        if "price_return" not in df.columns:
            df["price_return"] = df["close_price"].pct_change().fillna(0.0)

        if "momentum_7" not in df.columns:
            df["momentum_7"] = (df["close_price"] / df["close_price"].shift(7)).fillna(1.0)

        if "volatility_30" not in df.columns:
            df["volatility_30"] = df["price_return"].rolling(30, min_periods=1).std().fillna(0.0)

        if "wti_return" not in df.columns and "wti_price" in df.columns:
            df["wti_return"] = df["wti_price"].pct_change().fillna(0.0)

        # xgb placeholders if absent
        if "xgb_predicted_return" not in df.columns:
            df["xgb_predicted_return"] = df["price_return"].shift(1).fillna(0.0)
        if "xgb_trend" not in df.columns:
            df["xgb_trend"] = np.sign(df["xgb_predicted_return"]).astype(int)

        self.df = df.fillna(0.0)

    def _get_observation(self):
        start = self.current_step - self.window
        window_df = self.df.iloc[start:self.current_step][self.feature_names].values.astype(np.float32)
        if self.flatten:
            return window_df.flatten()
        return window_df

    def set_cost_curriculum(self, use_curriculum: bool):
        self.use_cost_curriculum = bool(use_curriculum)
        self.transaction_cost = self.train_tx if self.use_cost_curriculum else self.base_tx
        self.slippage = self.train_slip if self.use_cost_curriculum else self.base_slip

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = int(self.start_index)
        self.position = 0
        self.entry_price = 0.0
        self.holding_days = 0
        self.returns = []
        self.unrealized_profit = 0.0
        obs = self._get_observation()
        info = {"price": float(self.df.loc[self.current_step, "close_price"]), "position": int(self.position)}
        return obs, info

    def step(self, action):
        prev_price = float(self.df.loc[self.current_step, "close_price"])

        # enforce minimum hold days before allowing flips
        if self.position != 0 and self.holding_days < self.min_holding_days:
            if action in (1, 2):
                action = 0

        will_trade = False
        if action == 1:
            if self.position in (0, -1):
                will_trade = True
                self.position = 1
                self.entry_price = prev_price
                self.holding_days = 0
        elif action == 2:
            if self.position in (0, 1):
                will_trade = True
                self.position = -1
                self.entry_price = prev_price
                self.holding_days = 0
        # else hold

        self.current_step += 1
        cur_price = float(self.df.loc[self.current_step, "close_price"])

        if self.position == 1:
            raw_rtn = (cur_price - prev_price) / (prev_price + 1e-12)
        elif self.position == -1:
            raw_rtn = (prev_price - cur_price) / (prev_price + 1e-12)
        else:
            raw_rtn = 0.0

        txn_cost = float(self.transaction_cost) if will_trade else 0.0
        slippage_cost = float(self.slippage) if will_trade else 0.0

        net_rtn = raw_rtn - txn_cost - slippage_cost

        self.returns.append(net_rtn)

        if self.position != 0:
            self.holding_days += 1
        else:
            self.holding_days = 0

        if self.position == 1:
            self.unrealized_profit = cur_price - self.entry_price
        elif self.position == -1:
            self.unrealized_profit = self.entry_price - cur_price
        else:
            self.unrealized_profit = 0.0

        # compose reward: base net return + momentum bonus - volatility penalty + xgb alignment
        reward = float(net_rtn)

        # momentum bonus: use momentum_7 at current step
        if "momentum_7" in self.df.columns:
            momentum = float(self.df.loc[self.current_step, "momentum_7"])
            # center around 1.0 (momentum >1 implies upward movement)
            momentum_adj = momentum - 1.0
            reward += float(self.momentum_coef * momentum_adj * (1 if self.position == 1 else -1 if self.position == -1 else 0))

        # volatility penalty: discourage taking positions in very volatile periods
        if "volatility_30" in self.df.columns:
            vol = float(self.df.loc[self.current_step, "volatility_30"])
            reward -= float(self.vol_penalty * vol * (1 if self.position != 0 else 0))

        # xgb alignment: reward if aligned with predicted trend and strength
        if "xgb_trend" in self.df.columns and "xgb_predicted_return" in self.df.columns:
            xgb_trend = int(self.df.loc[self.current_step, "xgb_trend"])
            xgb_strength = float(abs(self.df.loc[self.current_step, "xgb_predicted_return"]))
            if self.position != 0 and xgb_trend != 0 and (self.position == xgb_trend):
                reward += float(self.xgb_align_coef * xgb_strength)

        done = self.current_step >= self.end_index

        info = {
            "step": int(self.current_step),
            "position": int(self.position),
            "net_return": float(net_rtn),
            "raw_return": float(raw_rtn),
            "txn_cost": float(txn_cost),
            "slippage": float(slippage_cost),
            "unrealized_profit": float(self.unrealized_profit),
        }

        return self._get_observation(), float(reward), bool(done), False, info

    def render(self, mode="human"):
        row = self.df.loc[self.current_step]
        price = float(row["close_price"])
        print(f"Step: {self.current_step}, Price: {price:.2f}, Pos: {self.position}, HoldingDays: {self.holding_days}, Unrealized: {self.unrealized_profit:.2f}")
