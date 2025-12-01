// Dashboard Page - Main Component
// This is where everything comes together!

import { useState, useEffect } from 'react';
import { TrendingUp, Newspaper, BarChart3, AlertCircle } from 'lucide-react';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { getPredictions, getNews, getMetrics } from '../api/client';
import type { Prediction, NewsArticle, ModelMetrics } from '../types';

// ============================================
// LESSON: React Hooks - useState
// ============================================
// useState creates a "state variable" that React tracks
// When state changes, React re-renders the component

const Dashboard = () => {
    // State for prediction data
    const [prediction, setPrediction] = useState<Prediction | null>(null);
    const [predictionLoading, setPredictionLoading] = useState(true);
    const [predictionError, setPredictionError] = useState<string | null>(null);

    // State for news data
    const [news, setNews] = useState<NewsArticle[]>([]);
    const [newsLoading, setNewsLoading] = useState(true);
    const [newsError, setNewsError] = useState<string | null>(null);

    // State for metrics data
    const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
    const [metricsLoading, setMetricsLoading] = useState(true);
    const [metricsError, setMetricsError] = useState<string | null>(null);

    // ============================================
    // LESSON: React Hooks - useEffect
    // ============================================
    // useEffect runs code after the component renders
    // The empty array [] means "run once when component mounts"

    useEffect(() => {
        loadDashboardData();
    }, []); // Empty dependency array = run once on mount

    // ============================================
    // LESSON: Async/Await for API Calls
    // ============================================
    // async functions let us use 'await' to wait for promises
    // try/catch handles errors gracefully

    const loadDashboardData = async () => {
        // Load prediction
        try {
            const response = await getPredictions.latest();
            setPrediction(response.data);
            setPredictionError(null);
        } catch (error) {
            console.error('Failed to load prediction:', error);
            setPredictionError('Failed to load prediction data');
        } finally {
            setPredictionLoading(false); // Always runs, even if error
        }

        // Load news
        try {
            const response = await getNews.latest(5);
            setNews(response.data.articles || []);
            setNewsError(null);
        } catch (error) {
            console.error('Failed to load news:', error);
            setNewsError('Failed to load news data');
        } finally {
            setNewsLoading(false);
        }

        // Load metrics
        try {
            const response = await getMetrics.model();
            setMetrics(response.data);
            setMetricsError(null);
        } catch (error) {
            console.error('Failed to load metrics:', error);
            setMetricsError('Failed to load metrics data');
        } finally {
            setMetricsLoading(false);
        }
    };

    // ============================================
    // LESSON: Helper Functions
    // ============================================
    // Small functions that format data for display

    const formatPrice = (price: number) => {
        return `$${price.toFixed(2)}`;
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    };

    const getSentimentColor = (sentiment: string) => {
        switch (sentiment.toLowerCase()) {
            case 'positive':
                return 'text-green-600 dark:text-green-400';
            case 'negative':
                return 'text-red-600 dark:text-red-400';
            default:
                return 'text-gray-600 dark:text-gray-400';
        }
    };

    const getSentimentIcon = (sentiment: string) => {
        switch (sentiment.toLowerCase()) {
            case 'positive':
                return '📈';
            case 'negative':
                return '📉';
            default:
                return '➖';
        }
    };

    // ============================================
    // LESSON: JSX Return Statement
    // ============================================
    // This is what gets rendered to the screen
    // It looks like HTML but it's actually JavaScript (JSX)

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            {/* Page Header */}
            <div className="mb-8">
                <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Live predictions, news sentiment, and model performance
                </p>
            </div>

            {/* Grid Layout - Responsive */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">

                {/* ============================================ */}
                {/* PREDICTION CARD */}
                {/* ============================================ */}
                <Card className="lg:col-span-1">
                    <div className="flex items-center mb-4">
                        <TrendingUp className="w-6 h-6 text-primary-600 mr-2" />
                        <h2 className="text-xl font-semibold">Latest Prediction</h2>
                    </div>

                    {/* Conditional Rendering: Show different UI based on state */}
                    {predictionLoading && <LoadingSpinner />}

                    {predictionError && (
                        <ErrorMessage
                            message={predictionError}
                            retry={loadDashboardData}
                        />
                    )}

                    {prediction && !predictionLoading && !predictionError && (
                        <div>
                            <div className="text-4xl font-bold text-primary-600 mb-2">
                                {formatPrice(prediction.predicted_price)}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Predicted for {formatDate(prediction.date)}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                                Updated: {new Date(prediction.timestamp).toLocaleTimeString()}
                            </p>
                        </div>
                    )}
                </Card>

                {/* ============================================ */}
                {/* MODEL METRICS CARD */}
                {/* ============================================ */}
                <Card className="lg:col-span-1">
                    <div className="flex items-center mb-4">
                        <BarChart3 className="w-6 h-6 text-primary-600 mr-2" />
                        <h2 className="text-xl font-semibold">Model Performance</h2>
                    </div>

                    {metricsLoading && <LoadingSpinner />}

                    {metricsError && (
                        <ErrorMessage
                            message={metricsError}
                            retry={loadDashboardData}
                        />
                    )}

                    {metrics && !metricsLoading && !metricsError && (
                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-gray-600 dark:text-gray-400">MAE</span>
                                <span className="font-semibold">${metrics.mae.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-gray-600 dark:text-gray-400">MAPE</span>
                                <span className="font-semibold">{metrics.mape.toFixed(2)}%</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-gray-600 dark:text-gray-400">Total Predictions</span>
                                <span className="font-semibold">{metrics.total_predictions}</span>
                            </div>
                        </div>
                    )}
                </Card>

                {/* ============================================ */}
                {/* NEWS SENTIMENT CARD */}
                {/* ============================================ */}
                <Card className="lg:col-span-1">
                    <div className="flex items-center mb-4">
                        <Newspaper className="w-6 h-6 text-primary-600 mr-2" />
                        <h2 className="text-xl font-semibold">News Sentiment</h2>
                    </div>

                    {newsLoading && <LoadingSpinner />}

                    {newsError && (
                        <ErrorMessage
                            message={newsError}
                            retry={loadDashboardData}
                        />
                    )}

                    {news.length > 0 && !newsLoading && !newsError && (
                        <div className="space-y-3 max-h-64 overflow-y-auto">
                            {/* Array.map() - Loop through news articles */}
                            {news.map((article, index) => (
                                <div
                                    key={index}
                                    className="pb-3 border-b border-gray-200 dark:border-gray-700 last:border-0"
                                >
                                    <p className="text-sm font-medium mb-1 line-clamp-2">
                                        {article.title}
                                    </p>
                                    <div className="flex items-center justify-between">
                                        <span className={`text-xs font-medium ${getSentimentColor(article.sentiment)}`}>
                                            {getSentimentIcon(article.sentiment)} {article.sentiment}
                                        </span>
                                        <span className="text-xs text-gray-500">
                                            Score: {article.score.toFixed(2)}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {news.length === 0 && !newsLoading && !newsError && (
                        <p className="text-gray-500 text-center py-4">No news available</p>
                    )}
                </Card>
            </div>

            {/* Info Section */}
            <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-start">
                    <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" />
                    <div>
                        <p className="text-sm text-blue-800 dark:text-blue-200">
                            <strong>Dashboard Updates:</strong> Data is fetched from the FastAPI backend when the page loads.
                            Refresh the page to see the latest predictions and news.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

// ============================================
// LESSON: Key Takeaways
// ============================================
// 1. useState manages component state (data)
// 2. useEffect runs code when component mounts
// 3. async/await handles asynchronous API calls
// 4. Conditional rendering shows different UI based on state
// 5. Array.map() renders lists of items
// 6. TypeScript ensures type safety
// 7. Reusable components (Card, LoadingSpinner) keep code DRY
