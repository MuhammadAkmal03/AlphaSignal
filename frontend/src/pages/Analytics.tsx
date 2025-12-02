import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Calendar, Target, AlertCircle } from 'lucide-react';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { getPredictions } from '../api/client';
import type { Prediction } from '../types';

const Analytics = () => {
    const [predictions, setPredictions] = useState<Prediction[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [timeRange, setTimeRange] = useState(365);
    const [featureImportance, setFeatureImportance] = useState<any[]>([]);

    // Feature names mapping from training data
    const FEATURE_NAMES = [
        "Ulsan_7ma", "Fujairah_7ma", "demand_score", "Singapore_7ma", "close_price_lag_1",
        "close_price_7vol", "Houston", "yolo_fullness", "Rotterdam_7vol", "PortArthur_7ma",
        "Singapore_lag_1", "Rotterdam", "Dalian_7ma", "Houston_7ma", "Antwerp_7vol",
        "wti_price", "RasTanura_7vol", "Singapore_7vol", "MinaAlAhmadi", "Ulsan",
        "Singapore_x_diesel_price", "Antwerp_7ma", "Yokohama", "Yokohama_lag_7", "Mumbai_7ma",
        "Dalian", "Qingdao_7vol", "Qingdao", "Ulsan_7vol", "month",
        "Dalian_7vol", "Singapore", "Fawley_UK_7ma", "MinaAlAhmadi_7ma", "Antwerp",
        "RasTanura_7ma", "tank_inventory_score", "RasTanura", "close_price"
    ];

    useEffect(() => {
        // Load feature importance data
        const loadFeatureImportance = async () => {
            console.log('Starting loadFeatureImportance...');
            try {
                const response = await fetch('/api/explainability/summary');
                console.log('Feature importance response status:', response.status);
                const data = await response.json();
                console.log('Feature importance data received:', data);

                // Map generic names to real names and format
                const mappedData = data.global_importance?.map((item: any) => {
                    // Extract index from "feature_X"
                    const indexMatch = item.feature.match(/feature_(\d+)/);
                    let realName = item.feature;

                    if (indexMatch && indexMatch[1]) {
                        const index = parseInt(indexMatch[1]);
                        if (index < FEATURE_NAMES.length) {
                            realName = FEATURE_NAMES[index];
                        }
                    }

                    // Format name for display (replace underscores with spaces)
                    const displayName = realName.replace(/_/g, ' ').replace(/7ma/g, '7D MA').replace(/7vol/g, '7D Vol');

                    return {
                        ...item,
                        feature: displayName,
                        originalFeature: item.feature
                    };
                }) || [];

                // Get top 10 features
                setFeatureImportance(mappedData.slice(0, 10));
            } catch (err) {
                console.error('Failed to load feature importance:', err);
            }
        };
        loadFeatureImportance();
    }, []);

    useEffect(() => {
        loadPredictions();
    }, [timeRange]);

    const loadPredictions = async () => {
        console.log('Starting loadPredictions...');
        setLoading(true);
        try {
            const response = await getPredictions.history(timeRange);
            console.log('Predictions loaded:', response.data);
            setPredictions(response.data.predictions || []);
            setError(null);
        } catch (err) {
            console.error('Failed to load predictions:', err);
            setError('Failed to load prediction data');
        } finally {
            console.log('Finished loadPredictions, setting loading to false');
            setLoading(false);
        }
    };

    const chartData = predictions.map((pred) => ({
        date: new Date(pred.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        predicted: pred.predicted_price,
        actual: pred.predicted_price * (0.95 + Math.random() * 0.1),
    }));

    const stats = {
        totalPredictions: predictions.length,
        avgPrice: predictions.length > 0
            ? predictions.reduce((sum, p) => sum + p.predicted_price, 0) / predictions.length
            : 0,
        minPrice: predictions.length > 0
            ? Math.min(...predictions.map(p => p.predicted_price))
            : 0,
        maxPrice: predictions.length > 0
            ? Math.max(...predictions.map(p => p.predicted_price))
            : 0,
    };

    const errorDistribution = chartData.map(d => ({
        date: d.date,
        error: Math.abs(d.predicted - d.actual),
    }));

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-10">
                <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">Analytics & Insights</h1>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    Detailed visualization of prediction performance and historical data
                </p>
            </div>

            <div className="mb-8 flex gap-2">
                {[30, 60, 90, 180, 365].map((days) => (
                    <button
                        key={days}
                        onClick={() => setTimeRange(days)}
                        className={`px-5 py-2.5 rounded-lg font-semibold transition-all duration-200 ${timeRange === days
                            ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg scale-105'
                            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 hover:shadow-md'
                            }`}
                    >
                        {days} Days
                    </button>
                ))}
            </div>

            {loading && <LoadingSpinner />}
            {error && <ErrorMessage message={error} retry={loadPredictions} />}

            {!loading && !error && predictions.length > 0 && (
                <div className="space-y-8">
                    <div className="grid md:grid-cols-4 gap-6 mb-8">
                        <Card className="hover:shadow-xl transition-shadow duration-300">
                            <div className="flex items-center justify-between p-3 bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Total Predictions</p>
                                    <p className="text-3xl font-bold text-primary-600">{stats.totalPredictions}</p>
                                </div>
                                <Calendar className="w-10 h-10 text-primary-600 opacity-30" />
                            </div>
                        </Card>

                        <Card className="hover:shadow-xl transition-shadow duration-300">
                            <div className="flex items-center justify-between p-3 bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Average Price</p>
                                    <p className="text-3xl font-bold text-primary-600">${stats.avgPrice.toFixed(2)}</p>
                                </div>
                                <TrendingUp className="w-10 h-10 text-primary-600 opacity-30" />
                            </div>
                        </Card>

                        <Card className="hover:shadow-xl transition-shadow duration-300">
                            <div className="flex items-center justify-between p-3 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Min Price</p>
                                    <p className="text-3xl font-bold text-green-600">${stats.minPrice.toFixed(2)}</p>
                                </div>
                                <Target className="w-10 h-10 text-green-600 opacity-30" />
                            </div>
                        </Card>

                        <Card className="hover:shadow-xl transition-shadow duration-300">
                            <div className="flex items-center justify-between p-3 bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 rounded-lg">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Max Price</p>
                                    <p className="text-3xl font-bold text-red-600">${stats.maxPrice.toFixed(2)}</p>
                                </div>
                                <Target className="w-10 h-10 text-red-600 opacity-30" />
                            </div>
                        </Card>
                    </div>

                    <Card title="Predicted vs Actual Prices" className="hover:shadow-xl transition-shadow duration-300">
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                                <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} domain={['auto', 'auto']} />
                                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }} />
                                <Legend />
                                <Line type="monotone" dataKey="predicted" stroke="#2563eb" strokeWidth={2} dot={{ fill: '#2563eb', r: 4 }} name="Predicted Price" />
                                <Line type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 4 }} name="Actual Price" />
                            </LineChart>
                        </ResponsiveContainer>
                    </Card>

                    <Card title="Prediction Error Over Time" className="hover:shadow-xl transition-shadow duration-300">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={errorDistribution}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                                <XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }} />
                                <Bar dataKey="error" fill="#f59e0b" name="Absolute Error ($)" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Card>

                    {/* Feature Importance Chart */}
                    {featureImportance.length > 0 && (
                        <Card title="Top 10 Most Important Features" className="hover:shadow-xl transition-shadow duration-300">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                                These features have the highest impact on price predictions. Higher values indicate greater importance.
                            </p>
                            <ResponsiveContainer width="100%" height={350}>
                                <BarChart data={featureImportance} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                                    <XAxis type="number" stroke="#6b7280" style={{ fontSize: '12px' }} />
                                    <YAxis
                                        type="category"
                                        dataKey="feature"
                                        stroke="#6b7280"
                                        style={{ fontSize: '11px' }}
                                        width={150}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: '#1f2937',
                                            border: '1px solid #374151',
                                            borderRadius: '8px',
                                            color: '#fff'
                                        }}
                                        formatter={(value: any) => [value.toFixed(4), 'Importance']}
                                    />
                                    <Bar dataKey="importance" fill="#2563eb" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                            <div className="mt-4 p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                    <strong>💡 Insight:</strong> Feature importance is calculated using the XGBoost model's built-in feature importance scores,
                                    showing which technical indicators and features contribute most to price predictions.
                                </p>
                            </div>
                        </Card>
                    )}

                    <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 shadow-sm">
                        <div className="flex items-start">
                            <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                            <div>
                                <p className="text-sm text-blue-800 dark:text-blue-200">
                                    <strong>Note:</strong> Actual prices shown are simulated. In production, these would come from your actuals log.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {!loading && !error && predictions.length === 0 && (
                <Card>
                    <p className="text-center text-gray-500 py-8">
                        No prediction data available for the selected time range.
                    </p>
                </Card>
            )}
        </div>
    );
};

export default Analytics;
