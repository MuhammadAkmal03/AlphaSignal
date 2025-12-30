// AI News Summary Component
// Displays AI-generated summary of today's oil news

import { useState, useEffect } from 'react';
import { Sparkles, RefreshCw, TrendingUp, Calendar } from 'lucide-react';
import Card from './Card';
import { getNews } from '../api/client';

interface NewsSummaryData {
    summary: string;
    article_count: number;
    overall_sentiment: string;
    generated_at: string;
}

const NewsSummary = () => {
    const [summary, setSummary] = useState<NewsSummaryData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchSummary();
    }, []);

    const fetchSummary = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await getNews.summary();
            setSummary(response.data);
        } catch (err) {
            console.error('Failed to fetch news summary:', err);
            setError('Failed to load news summary');
        } finally {
            setLoading(false);
        }
    };

    // Sentiment color mapping
    const getSentimentColor = (sentiment: string) => {
        const s = sentiment.toLowerCase();
        if (s.includes('positive')) return 'text-green-600 bg-green-50 dark:bg-green-900/20';
        if (s.includes('negative')) return 'text-red-600 bg-red-50 dark:bg-red-900/20';
        if (s.includes('mixed')) return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20';
        return 'text-gray-600 bg-gray-50 dark:bg-gray-800';
    };

    return (
        <Card>
            <div className="space-y-4">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-primary-600" />
                        <h3 className="text-lg font-semibold">AI News Summary</h3>
                    </div>
                    <button
                        onClick={fetchSummary}
                        disabled={loading}
                        className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        {loading ? 'Generating...' : summary ? 'Refresh' : 'Generate Summary'}
                    </button>
                </div>

                {/* Content */}
                {!summary && !loading && !error && (
                    <div className="text-center py-8">
                        <p className="text-gray-500 mb-4">Click refresh to generate AI summary of today's oil news</p>
                        <button
                            onClick={fetchSummary}
                            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                        >
                            Generate Summary
                        </button>
                    </div>
                )}

                {loading && (
                    <div className="text-center py-8">
                        <div className="inline-block w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
                        <p className="mt-4 text-gray-600 dark:text-gray-400">Generating AI summary...</p>
                    </div>
                )}

                {error && (
                    <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                        <p className="text-red-800 dark:text-red-200">{error}</p>
                    </div>
                )}

                {summary && !loading && (
                    <div className="space-y-4">
                        {/* Summary Text */}
                        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                                {summary.summary}
                            </p>
                        </div>

                        {/* Metadata */}
                        <div className="grid md:grid-cols-3 gap-4">
                            {/* Article Count */}
                            <div className="flex items-center gap-2 text-sm">
                                <Calendar className="w-4 h-4 text-gray-500" />
                                <span className="text-gray-600 dark:text-gray-400">
                                    {summary.article_count} articles
                                </span>
                            </div>

                            {/* Sentiment */}
                            <div className="flex items-center gap-2 text-sm">
                                <TrendingUp className="w-4 h-4 text-gray-500" />
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(summary.overall_sentiment)}`}>
                                    {summary.overall_sentiment}
                                </span>
                            </div>

                            {/* Last Updated */}
                            <div className="text-sm text-gray-500 text-right">
                                {new Date(summary.generated_at).toLocaleTimeString()}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </Card>
    );
};

export default NewsSummary;
