import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Predictions
export const getPredictions = {
    latest: () => api.get('/predictions/latest'),
    history: (days: number = 30) => api.get(`/predictions/history?days=${days}`),
    stats: () => api.get('/predictions/stats'),
};

// RL Agent
export const getRLAgent = {
    recommendation: () => api.get('/rl/recommendation'),
    performance: () => api.get('/rl/performance'),
    equityCurve: () => api.get('/rl/equity-curve'),
};

// News
export const getNews = {
    latest: (limit: number = 5) => api.get(`/news/latest?limit=${limit}`),
    summary: () => api.get('/news/summary'),
    sentimentStats: () => api.get('/news/sentiment-stats'),
};

// Metrics
export const getMetrics = {
    model: () => api.get('/metrics/model'),
};

// Backtest
export const getBacktest = {
    run: (params: { lookback_days: number; initial_capital: number }) =>
        api.post('/backtest/run', params),
};

export default api;
