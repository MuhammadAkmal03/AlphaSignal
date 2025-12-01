import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Predictions
export const getPredictions = {
    latest: () => api.get('/api/predictions/latest'),
    history: (days: number = 30) => api.get(`/api/predictions/history?days=${days}`),
    stats: () => api.get('/api/predictions/stats'),
};

// Backtesting
export const getBacktest = {
    run: (params: { lookback_days: number; initial_capital: number }) =>
        api.post('/api/backtest/run', params),
    results: () => api.get('/api/backtest/results/latest'),
    charts: () => api.get('/api/backtest/charts'),
};

// RL Agent
export const getRLAgent = {
    recommendation: () => api.get('/api/rl/recommendation'),
    performance: () => api.get('/api/rl/performance'),
    equityCurve: () => api.get('/api/rl/equity-curve'),
};

// News
export const getNews = {
    latest: (limit: number = 5) => api.get(`/api/news/latest?limit=${limit}`),
    summary: () => api.get('/api/news/summary'),
    sentimentStats: () => api.get('/api/news/sentiment-stats'),
};

// Metrics
export const getMetrics = {
    model: () => api.get('/api/metrics/model'),
    system: () => api.get('/api/metrics/system'),
    overview: () => api.get('/api/metrics/overview'),
};

export default api;
