// RecommendationCard Component
// Displays the RL agent's current trading recommendation

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
import Card from './Card';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import { getRLAgent } from '../api/client';
import type { RLRecommendation } from '../types';

const RecommendationCard = () => {
    const [recommendation, setRecommendation] = useState<RLRecommendation | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchRecommendation();
    }, []);

    const fetchRecommendation = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getRLAgent.recommendation();
            setRecommendation(response.data);
        } catch (err) {
            console.error('Failed to fetch RL recommendation:', err);
            setError('Failed to load recommendation');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Card><LoadingSpinner /></Card>;
    if (error) return <Card><ErrorMessage message={error} /></Card>;
    if (!recommendation) return null;

    // Action styling
    const getActionStyle = (action: string) => {
        switch (action) {
            case 'LONG':
                return {
                    bg: 'bg-green-100 dark:bg-green-900/30',
                    text: 'text-green-700 dark:text-green-300',
                    border: 'border-green-500',
                    icon: TrendingUp,
                };
            case 'SHORT':
                return {
                    bg: 'bg-red-100 dark:bg-red-900/30',
                    text: 'text-red-700 dark:text-red-300',
                    border: 'border-red-500',
                    icon: TrendingDown,
                };
            default: // HOLD
                return {
                    bg: 'bg-blue-100 dark:bg-blue-900/30',
                    text: 'text-blue-700 dark:text-blue-300',
                    border: 'border-blue-500',
                    icon: Minus,
                };
        }
    };

    const style = getActionStyle(recommendation.action);
    const Icon = style.icon;

    return (
        <Card>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <Activity className="w-6 h-6 text-primary-600" />
                        Current Recommendation
                    </h2>
                    <button
                        onClick={fetchRecommendation}
                        className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    >
                        Refresh
                    </button>
                </div>

                {/* Action Badge */}
                <div className={`${style.bg} ${style.border} border-2 rounded-2xl p-8 text-center animate-pulse`}>
                    <div className="flex items-center justify-center gap-4 mb-4">
                        <Icon className={`w-12 h-12 ${style.text}`} />
                        <h3 className={`text-5xl font-bold ${style.text}`}>
                            {recommendation.action}
                        </h3>
                    </div>

                    {/* Confidence Meter */}
                    <div className="mt-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                Confidence
                            </span>
                            <span className={`text-lg font-bold ${style.text}`}>
                                {recommendation.confidence?.toFixed(1) || '0.0'}%
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                            <div
                                className={`h-3 rounded-full transition-all duration-500 ${recommendation.action === 'LONG'
                                    ? 'bg-green-500'
                                    : recommendation.action === 'SHORT'
                                        ? 'bg-red-500'
                                        : 'bg-blue-500'
                                    }`}
                                style={{ width: `${recommendation.confidence || 0}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Reasoning */}
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                    <h4 className="font-semibold mb-2 text-gray-700 dark:text-gray-300">
                        Analysis
                    </h4>
                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                        {recommendation.reasoning}
                    </p>
                </div>

                {/* What This Means */}
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                    <h4 className="font-semibold mb-2 text-blue-800 dark:text-blue-200 flex items-center gap-2">
                        💡 What This Means For You
                    </h4>
                    <div className="text-sm text-blue-700 dark:text-blue-300 space-y-2">
                        {recommendation.action === 'LONG' && (
                            <>
                                <p>✓ <strong>The AI expects oil prices to rise</strong></p>
                                <p>• Consider buying crude oil futures or related stocks</p>
                                <p>• This is a bullish signal based on market analysis</p>
                            </>
                        )}
                        {recommendation.action === 'SHORT' && (
                            <>
                                <p>✓ <strong>The AI expects oil prices to fall</strong></p>
                                <p>• Consider selling or shorting crude oil positions</p>
                                <p>• This is a bearish signal based on market analysis</p>
                            </>
                        )}
                        {recommendation.action === 'HOLD' && (
                            <>
                                <p>✓ <strong>The AI suggests waiting</strong></p>
                                <p>• Market conditions are uncertain or neutral</p>
                                <p>• Best to maintain current positions and observe</p>
                            </>
                        )}
                        <p className="text-xs mt-2 opacity-75">
                            ⚠️ This is AI-generated advice. Always do your own research and consult financial advisors.
                        </p>
                    </div>
                </div>

                {/* Last Updated */}
                <div className="text-center text-sm text-gray-500">
                    Last updated: {new Date().toLocaleTimeString()}
                </div>
            </div>
        </Card>
    );
};

export default RecommendationCard;
