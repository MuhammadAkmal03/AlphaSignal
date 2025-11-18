"""
- Cost curriculum (reduced transaction cost & slippage during training)
- Reward modes: 'net' (default, stable) or 'sharpe'
- Holding reward: small bonus for holding in the correct direction
- XGBoost alignment bonus: extra reward if agent follows XGB prediction
- Fine-grained toggles / hyperparameters exposed as constructor args
- Gymnasium-compliant reset/step signatures (seed/options supported)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import joblib

import gymnasium as gym
from gymnasium import spaces


ENGINEERED = Path("data/final/features/engineered_features.csv")
SELECTED = Path("data/final/features/selected_features.csv")
MODEL = Path("models/xgb_model.pkl")
SCALER = Path("models/scaler.pkl")


class CrudeTradingEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        df_path: Path = ENGINEERED,
        selected_features_path: Path = SELECTED,
        model_path: Path = MODEL,
        scaler_path: Path = SCALER,
        initial_balance: float = 100000.0,
        rolling_window: int = 30,
        eps: float = 1e-6,
        verbose: bool = False,
        start_index: int = None,
        end_index: int = None,
        # ---- Improvements toggles & hyperparams ----
        cost_curriculum: bool = True,        # reduce costs during training
        reward_mode: str = "net",            # 'net' or 'sharpe'
        holding_reward_coef: float = 0.0,    # add bonus per-step when holding in direction (0 to disable)
        xgb_alignment_bonus: float = 0.0,    # additional bonus when following xgb_trend (0 to disable)
        min_trade_hold: int = 1,             # minimum hold days before counting holding reward
    ):
        super().__init__()

        # paths
        self.df_path = Path(df_path)
        self.selected_features_path = Path(selected_features_path)
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)

        # basic config
        self.initial_balance = initial_balance
        self.rolling_window = rolling_window
        self.eps = eps
        self.verbose = bool(verbose)

        # improvement switches
        self.cost_curriculum = bool(cost_curriculum)
        self.reward_mode = reward_mode
        self.holding_reward_coef = float(holding_reward_coef)
        self.xgb_alignment_bonus = float(xgb_alignment_bonus)
        self.min_trade_hold = int(min_trade_hold)

        # load dataset
        if not self.df_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.df_path}")
        self.df = pd.read_csv(self.df_path)

        # preprocessing
        self._detect_date_column()
        self._standardize_close_column()
        self._detect_ais_columns()
        self._ensure_core_features()
        self._inject_xgb_predictions_and_signals()

        # observation features
        self.feature_names = self._build_feature_list()

        # cost parameters 
        self.base_transaction_cost = 0.0003   
        self.base_slippage = 0.0007           
        self.train_transaction_cost = 0.0001  
        self.train_slippage = 0.0002          

        # active cost rates 
        self.transaction_cost_rate = (
            self.train_transaction_cost if self.cost_curriculum else self.base_transaction_cost
        )
        self.slippage_rate = (self.train_slippage if self.cost_curriculum else self.base_slippage)

        # action/observation spaces
        self.action_space = spaces.Discrete(3)  # 0 hold, 1 long, 2 short
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(len(self.feature_names),),
            dtype=np.float32,
        )

        # indices
        self.start_index = 0 if start_index is None else int(start_index)
        self.end_index = len(self.df) - 1 if end_index is None else int(end_index)

        # state variables
        self.current_step = int(self.start_index)
        self.position = 0
        self.entry_price = 0.0
        self.balance = float(self.initial_balance)
        self.returns = []
        self.holding_days = 0
        self.unrealized_profit = 0.0

    # Data detection / preprocessing
    def _detect_date_column(self):
        for c in ("date", "timestamp"):
            if c in self.df.columns:
                self.date_col = c
                self.df[self.date_col] = pd.to_datetime(self.df[self.date_col])
                self.df = self.df.sort_values(self.date_col).reset_index(drop=True)
                return
        self.date_col = None

    def _standardize_close_column(self):
        for c in ("close_price", "close", "brent_close", "brent_close_price"):
            if c in self.df.columns:
                if c != "close_price":
                    self.df = self.df.rename(columns={c: "close_price"})
                return
        raise ValueError("No close price column found in dataframe.")

    def _detect_ais_columns(self):
        base_ports = [
            "Houston", "Singapore", "Rotterdam", "Fujairah", "RasTanura",
            "Antwerp", "Qingdao", "Dalian", "CorpusChristi", "PortArthur",
            "Fawley_UK", "MinaAlAhmadi", "Yokohama", "Ulsan", "Mumbai",
        ]
        cols = list(self.df.columns)
        ais_cols = []
        for port in base_ports:
            p = port.lower()
            for col in cols:
                low = col.lower()
                if low == p or low.startswith(p + "_") or low.startswith(p):
                    ais_cols.append(col)
        for col in cols:
            low = col.lower()
            if ("ais" in low or "congestion" in low) and col not in ais_cols:
                ais_cols.append(col)
        # order preserved
        self.ais_cols = [c for c in cols if c in ais_cols]
        if "ais_global_congestion" not in self.df.columns:
            if len(self.ais_cols) > 0:
                self.df["ais_global_congestion"] = self.df[self.ais_cols].mean(axis=1)
            else:
                self.df["ais_global_congestion"] = 0.0

    def _ensure_core_features(self):
        df = self.df
        if "price_return" not in df.columns:
            df["price_return"] = df["close_price"].pct_change().fillna(0.0)
        if "ma_7" not in df.columns:
            df["ma_7"] = df["close_price"].rolling(7, min_periods=1).mean()
        if "ma_30" not in df.columns:
            df["ma_30"] = df["close_price"].rolling(30, min_periods=1).mean()
        if "volatility_30" not in df.columns:
            df["volatility_30"] = df["price_return"].rolling(self.rolling_window, min_periods=1).std().fillna(0.0)
        if "momentum_7" not in df.columns:
            df["momentum_7"] = (df["close_price"] / df["close_price"].shift(7)).fillna(1.0)

    # XGBoost injection + strengthened signals

    def _inject_xgb_predictions_and_signals(self):
        price_col = "xgb_predicted_price"
        ret_col = "xgb_predicted_return"

        if price_col not in self.df.columns or ret_col not in self.df.columns:
            if self.model_path.exists() and self.scaler_path.exists() and self.selected_features_path.exists():
                try:
                    model = joblib.load(self.model_path)
                    scaler = joblib.load(self.scaler_path)
                    sel = pd.read_csv(self.selected_features_path)
                    selected = sel["feature"].tolist() if "feature" in sel.columns else [c for c in self.df.columns if c != self.date_col]
                    for s in selected:
                        if s not in self.df.columns:
                            self.df[s] = 0.0
                    X = self.df[selected].fillna(0.0)
                    Xs = scaler.transform(X)
                    preds = model.predict(Xs)
                    self.df[price_col] = preds
                    self.df[ret_col] = pd.Series(preds).pct_change().fillna(0.0)
                except Exception:
                    self.df[price_col] = self.df["close_price"].shift(1).bfill()
                    self.df[ret_col] = self.df[price_col].pct_change().fillna(0.0)
            else:
                self.df[price_col] = self.df["close_price"].shift(1).bfill()
                self.df[ret_col] = self.df[price_col].pct_change().fillna(0.0)

        # strengthen XGB signals for RL
        self.df["xgb_trend"] = np.sign(self.df[ret_col]).fillna(0).astype(int)
        self.df["xgb_strength"] = self.df[ret_col].abs().fillna(0.0)
        self.df["signal_agreement"] = (np.sign(self.df["price_return"]) == np.sign(self.df[ret_col])).astype(float)

    # Observation builder

    def _build_feature_list(self):
        core = [
            "close_price",
            "price_return",
            "ma_7",
            "ma_30",
            "volatility_30",
            "momentum_7",
            "ais_global_congestion",
        ]

        xgb = [
            "xgb_predicted_price",
            "xgb_predicted_return",
            "xgb_trend",
            "xgb_strength",
            "signal_agreement",
        ]

        internals = ["current_position", "unrealized_profit", "holding_days"]

        features = core + self.ais_cols + xgb + internals
        # filter to ensure exist / internal placeholders allowed
        features = [f for f in features if (f in self.df.columns) or (f in internals)]
        return features

    def _get_state(self, step=None):
        if step is None:
            step = int(self.current_step)
        row = self.df.loc[step]
        state = []
        for f in self.feature_names:
            if f == "current_position":
                state.append(float(self.position))
            elif f == "unrealized_profit":
                state.append(float(self.unrealized_profit))
            elif f == "holding_days":
                state.append(float(self.holding_days))
            else:
                state.append(float(row.get(f, 0.0)))
        return np.array(state, dtype=np.float32)

    # Trading calculations

    def _calculate_return(self, prev_price, cur_price, action):
        # raw return given current position
        if self.position == 1:
            rtn = (cur_price - prev_price) / (prev_price + self.eps)
        elif self.position == -1:
            rtn = (prev_price - cur_price) / (prev_price + self.eps)
        else:
            rtn = 0.0

        # cost components
        slippage_cost = self.slippage_rate
        txn_cost = self.transaction_cost_rate if action in (1, 2) else 0.0

        net_rtn = rtn - txn_cost - slippage_cost
        # append net return history (used by sharpe)
        self.returns.append(net_rtn)
        return float(net_rtn), float(rtn), float(txn_cost), float(slippage_cost)

    def _calculate_reward(self, net_rtn, raw_rtn, txn_cost, slippage):
        """
        Compose reward from several components:
        - base: either net_rtn or sharpe-style
        - holding reward: small bonus for holding in direction of price movement
        - xgb alignment bonus: if position matches xgb_trend, add bonus proportional to xgb_strength
        """
        # Base reward
        if self.reward_mode == "net":
            reward = float(net_rtn)
        else:
            # sharpe-style
            if len(self.returns) < 2:
                vol = np.std(self.returns) if self.returns else 0.0
            else:
                vol = np.std(self.returns[-self.rolling_window:])
            vol = max(vol, self.eps)
            reward = float(net_rtn / vol)

        # Holding reward: reward for holding in correct direction (scaled)
        if self.holding_reward_coef and self.position != 0 and self.holding_days >= self.min_trade_hold:   
            if (self.position == 1 and raw_rtn > 0) or (self.position == -1 and raw_rtn < 0):
                holding_bonus = self.holding_reward_coef * abs(raw_rtn)
                reward += holding_bonus

        # XGB alignment bonus
        if self.xgb_alignment_bonus and "xgb_trend" in self.df.columns and "xgb_strength" in self.df.columns:
            # current row's xgb_trend/strength
            xgb_trend = int(self.df.loc[self.current_step, "xgb_trend"])
            xgb_strength = float(self.df.loc[self.current_step, "xgb_strength"])
            if self.position != 0 and xgb_trend != 0 and (self.position == xgb_trend):
                # bonus proportional to predicted strength
                reward += self.xgb_alignment_bonus * xgb_strength

        return float(reward)

    # Gym methods

    def step(self, action):
        """
        Gymnasium step:
        returns: observation, reward, terminated, truncated, info
        """
        if self.current_step >= self.end_index:
            terminated = True
            truncated = False
            return self._get_state(), 0.0, terminated, truncated, {"msg": "end of data"}

        prev_price = float(self.df.loc[self.current_step, "close_price"])

        # apply action (open/flip positions)
        if action == 1:  # buy / go long
            if self.position in (0, -1):
                self.position = 1
                self.entry_price = prev_price
                self.holding_days = 0
        elif action == 2:  # sell / go short
            if self.position in (0, 1):
                self.position = -1
                self.entry_price = prev_price
                self.holding_days = 0
        # action == 0: hold -> no position change

        # step forward
        self.current_step += 1
        cur_price = float(self.df.loc[self.current_step, "close_price"])

        net_rtn, raw_rtn, txn_cost, slippage = self._calculate_return(prev_price, cur_price, action)

        # update unrealized profit
        if self.position == 1:
            self.unrealized_profit = cur_price - self.entry_price
        elif self.position == -1:
            self.unrealized_profit = self.entry_price - cur_price
        else:
            self.unrealized_profit = 0.0

        if self.position != 0:
            self.holding_days += 1

        # compute reward (composed)
        reward = self._calculate_reward(net_rtn, raw_rtn, txn_cost, slippage)

        done = self.current_step >= self.end_index

        info = {
            "step": int(self.current_step),
            "position": int(self.position),
            "entry_price": float(self.entry_price),
            "net_return": float(net_rtn),
            "raw_return": float(raw_rtn),
            "txn_cost": float(txn_cost),
            "slippage": float(slippage),
            "unrealized_profit": float(self.unrealized_profit),
        }

        terminated = bool(done)
        truncated = False  
        return self._get_state(), float(reward), terminated, truncated, info


    def reset(self, *, seed=None, options=None):
        """
        Gymnasium reset: returns (obs, info)
        """
        if seed is not None:
            np.random.seed(seed)

        random_start = False
        if options and "random_start" in options:
            random_start = options["random_start"]

        if random_start:
            self.current_step = int(
                np.random.randint(self.start_index, max(self.start_index + 1, self.end_index - 10))
            )
        else:
            self.current_step = int(self.start_index)

        self.position = 0
        self.entry_price = 0.0
        self.balance = float(self.initial_balance)
        self.returns = []
        self.holding_days = 0
        self.unrealized_profit = 0.0

        obs = self._get_state()
        info = {}
        return obs, info

    def render(self, mode="human"):
        row = self.df.loc[self.current_step]
        price = row["close_price"]
        print(f"Step: {self.current_step}, Price: {price:.2f}, Position: {self.position}, Unrealized: {self.unrealized_profit:.2f}")
