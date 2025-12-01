// TypeScript Type Definitions for API Responses
// This file defines the shape of data we expect from the FastAPI backend

// ============================================
// LESSON: TypeScript Interfaces
// ============================================
// Interfaces define the structure of objects
// They provide autocomplete and catch errors at compile-time

// Prediction Types
export interface Prediction {
    date: string;
    predicted_price: number;
    timestamp: string;
}

export interface PredictionHistory {
    predictions: Prediction[];
    count: number;
}

export interface PredictionStats {
    total_predictions: number;
    avg_predicted_price: number;
    min_predicted_price: number;
    max_predicted_price: number;
    date_range: {
        start: string;
        end: string;
    };
}

// News Types
export interface NewsArticle {
    title: string;
    sentiment: 'positive' | 'negative' | 'neutral'; // Union type - can only be these values
    score: number;
    published_at: string;
}

export interface NewsSummary {
    summary: string;
    article_count: number;
    overall_sentiment: string;
    generated_at: string;
}

// Model Metrics Types
export interface ModelMetrics {
    mae: number;
    mape: number;
    total_predictions: number;
    last_updated: string;
}

// RL Agent Types
export interface RLRecommendation {
    action: 'LONG' | 'SHORT' | 'HOLD';
    confidence: number;
    reasoning: string;
}

export interface RLPerformance {
    net_total_return: number;
    gross_total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    total_costs: number;
}

export interface EquityDataPoint {
    step: number;
    net_equity: number;
    gross_equity: number;
}

export interface EquityCurveData {
    data: EquityDataPoint[];
    summary: {
        initial_equity: number;
        final_equity: number;
        peak_equity: number;
        data_points: number;
    };
}

export interface Trade {
    date?: string;
    step: number;
    action: number;
    position: number;
    price: number;
    net_return: number;
    cumulative_return: number;
}

// Backtest Types
export interface BacktestMetrics {
    mae: number;
    rmse: number;
    mape: number;
    directional_accuracy: number;
    correlation: number;
}

export interface TradingMetrics {
    total_return_pct: number;
    sharpe_ratio: number;
    max_drawdown_pct: number;
    win_rate: number;
}

// ============================================
// LESSON: Why Use TypeScript?
// ============================================
// 1. Autocomplete: Your editor knows what properties exist
// 2. Error Prevention: Catches typos before runtime
// 3. Documentation: Types serve as inline documentation
// 4. Refactoring: Safely rename properties across entire codebase
