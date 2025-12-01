# AlphaSignal FastAPI Backend

## Quick Start

### 1. Install Dependencies
```bash
cd api
pip install -r requirements.txt
```

### 2. Run the Server
```bash
# Development mode (auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Predictions
- `GET /api/predictions/latest` - Get latest prediction
- `GET /api/predictions/history?days=30` - Get prediction history
- `GET /api/predictions/stats` - Get prediction statistics

### Backtesting
- `POST /api/backtest/run` - Run backtest
- `GET /api/backtest/results/latest` - Get latest results
- `GET /api/backtest/charts` - Get chart paths

### RL Agent
- `GET /api/rl/recommendation` - Get current recommendation
- `GET /api/rl/performance` - Get performance metrics
- `GET /api/rl/equity-curve` - Get equity curve data

### News
- `GET /api/news/latest?limit=5` - Get latest news
- `GET /api/news/summary` - Get AI summary
- `GET /api/news/sentiment-stats` - Get sentiment statistics

### Metrics
- `GET /api/metrics/model` - Get model metrics
- `GET /api/metrics/system` - Get system health
- `GET /api/metrics/overview` - Get comprehensive overview

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test latest prediction
curl http://localhost:8000/api/predictions/latest
```

## Project Structure
```
api/
├── main.py              # FastAPI app entry point
├── requirements.txt     # Python dependencies
└── routers/            # API route handlers
    ├── predictions.py  # Prediction endpoints
    ├── backtest.py     # Backtesting endpoints
    ├── rl_agent.py     # RL agent endpoints
    ├── news.py         # News endpoints
    └── metrics.py      # Metrics endpoints
```
