// Dashboard Page - Main Component
// This is where everything comes together!

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Newspaper, BarChart3, AlertCircle, Mail } from 'lucide-react';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import NewsSummary from '../components/NewsSummary';
import EmailReportModal from '../components/EmailReportModal';
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
    const [previousPrediction, setPreviousPrediction] = useState<Prediction | null>(null);
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

    // State for email modal
    const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);

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

            // Also load previous prediction for comparison
            try {
                const prevResponse = await getPredictions.previous();
                setPreviousPrediction(prevResponse.data);
            } catch (prevError) {
                console.log('Previous prediction not available:', prevError);
            }

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

    const formatPrice = (price: number | undefined | null) => {
        if (typeof price !== 'number') return '$0.00';
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Page Header */}
            <div className="mb-10 flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">Dashboard</h1>
                    <p className="text-gray-600 dark:text-gray-400 text-lg">
                        Live predictions, news sentiment, and model performance
                    </p>
                </div>
                <button
                    onClick={() => setIsEmailModalOpen(true)}
                    className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-semibold hover:shadow-lg hover:scale-105 transition-all duration-200"
                >
                    <Mail className="w-5 h-5" />
                    Get Email Report
                </button>
            </div>

            {/* Grid Layout - Responsive */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">

                {/* ============================================ */}
                {/* PREDICTION CARD */}
                {/* ============================================ */}
                <Card className="lg:col-span-1 hover:shadow-xl transition-shadow duration-300">
                    <div className="flex items-center mb-6">
                        <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg mr-3">
                            <TrendingUp className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        </div>
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

                    {prediction && !predictionLoading && !predictionError && (() => {
                        // Calculate trend using actual previous prediction
                        const previousPrice = previousPrediction?.predicted_price || prediction.predicted_price;
                        const priceChange = prediction.predicted_price - previousPrice;
                        const percentChange = previousPrice > 0 ? (priceChange / previousPrice) * 100 : 0;
                        const isUp = priceChange > 0;

                        return (
                            <div>
                                {/* Main Price Display - Large and Prominent */}
                                <div className={`p-6 rounded-xl mb-4 transition-all duration-300 ${isUp
                                    ? 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-2 border-green-400/50 shadow-green-100 dark:shadow-green-900/20 shadow-lg'
                                    : 'bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 border-2 border-red-400/50 shadow-red-100 dark:shadow-red-900/20 shadow-lg'
                                    }`}>
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                            Crude Oil Price
                                        </span>
                                        {isUp ? (
                                            <TrendingUp className="w-8 h-8 text-green-600 animate-pulse" />
                                        ) : (
                                            <TrendingDown className="w-8 h-8 text-red-600 animate-pulse" />
                                        )}
                                    </div>

                                    {/* Huge Price */}
                                    <div className={`text-6xl font-bold mb-2 ${isUp ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'
                                        }`}>
                                        {formatPrice(prediction.predicted_price)}
                                    </div>

                                    {/* Change Indicator */}
                                    <div className={`flex items-center gap-2 text-lg font-semibold ${isUp ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'
                                        }`}>
                                        <span>{isUp ? '▲' : '▼'}</span>
                                        <span>{isUp ? '+' : ''}{formatPrice(Math.abs(priceChange))}</span>
                                        <span>({isUp ? '+' : ''}{percentChange.toFixed(2)}%)</span>
                                    </div>

                                    <p className={`text-sm mt-2 ${isUp ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                                        }`}>
                                        vs previous: {formatPrice(previousPrice)}
                                    </p>
                                </div>

                                {/* Additional Info */}
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-gray-600 dark:text-gray-400">Predicted for:</span>
                                        <span className="font-semibold">{formatDate(prediction.date)}</span>
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-gray-600 dark:text-gray-400">Last updated:</span>
                                        <span className="font-semibold">{new Date(prediction.timestamp).toLocaleTimeString()}</span>
                                    </div>
                                </div>

                                {/* Trend Message */}
                                <div className={`mt-4 p-3 rounded-lg ${isUp
                                    ? 'bg-green-100 dark:bg-green-900/30 border border-green-300 dark:border-green-700'
                                    : 'bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700'
                                    }`}>
                                    <p className={`text-sm font-medium ${isUp ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'
                                        }`}>
                                        {isUp ? '📈 Bullish Signal' : '📉 Bearish Signal'}
                                        {' - '}
                                        {isUp
                                            ? 'Price expected to rise'
                                            : 'Price expected to fall'}
                                    </p>
                                </div>
                            </div>
                        );
                    })()}
                </Card>

                {/* ============================================ */}
                {/* MODEL METRICS CARD */}
                {/* ============================================ */}
                <Card className="lg:col-span-1 hover:shadow-xl transition-shadow duration-300">
                    <div className="flex items-center mb-6">
                        <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg mr-3">
                            <BarChart3 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        </div>
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
                        <div className="space-y-4">
                            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                                <span className="text-gray-600 dark:text-gray-400 font-medium">MAE</span>
                                <span className="font-bold text-lg">${metrics?.mae?.toFixed(2) || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                                <span className="text-gray-600 dark:text-gray-400 font-medium">MAPE</span>
                                <span className="font-bold text-lg">{metrics?.mape?.toFixed(2) || 'N/A'}%</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                                <span className="text-gray-600 dark:text-gray-400 font-medium">Total Predictions</span>
                                <span className="font-bold text-lg">{metrics?.total_predictions || 'N/A'}</span>
                            </div>
                        </div>
                    )}
                </Card>

                {/* ============================================ */}
                {/* NEWS SENTIMENT CARD */}
                {/* ============================================ */}
                <Card className="lg:col-span-1 hover:shadow-xl transition-shadow duration-300">
                    <div className="flex items-center mb-6">
                        <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg mr-3">
                            <Newspaper className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        </div>
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
                        <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
                            {/* Array.map() - Loop through news articles */}
                            {news.map((article, index) => (
                                <div
                                    key={index}
                                    className="pb-3 border-b border-gray-200 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-800/30 p-2 rounded-lg transition-colors"
                                >
                                    <p className="text-sm font-medium mb-1 line-clamp-2">
                                        {article.title}
                                    </p>
                                    <div className="flex items-center justify-between">
                                        <span className={`text-xs font-medium ${getSentimentColor(article.sentiment)}`}>
                                            {getSentimentIcon(article.sentiment)} {article.sentiment}
                                        </span>
                                        <span className="text-xs text-gray-500">
                                            Score: {article.score?.toFixed(2) || 'N/A'}
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

            {/* AI News Summary Section */}
            <div className="mt-8">
                <NewsSummary />
            </div>

            {/* Info Section */}
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 shadow-sm">
                <div className="flex items-start">
                    <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                    <div>
                        <p className="text-sm text-blue-800 dark:text-blue-200">
                            <strong>Dashboard Updates:</strong> Data is fetched from the FastAPI backend when the page loads.
                            Refresh the page to see the latest predictions and news.
                        </p>
                    </div>
                </div>
            </div>

            {/* Email Report Modal */}
            <EmailReportModal
                isOpen={isEmailModalOpen}
                onClose={() => setIsEmailModalOpen(false)}
            />
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
