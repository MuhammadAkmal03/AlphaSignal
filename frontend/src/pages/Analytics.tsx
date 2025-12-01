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

    useEffect(() => {
        loadPredictions();
    }, [timeRange]);

    const loadPredictions = async () => {
        setLoading(true);
        try {
            const response = await getPredictions.history(timeRange);
            setPredictions(response.data.predictions || []);
            setError(null);
        } catch (err) {
            console.error('Failed to load predictions:', err);
            setError('Failed to load prediction data');
        } finally {
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="mb-8">
                <h1 className="text-4xl font-bold mb-2">Analytics & Insights</h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Detailed visualization of prediction performance and historical data
                </p>
            </div>

            <div className="mb-6 flex gap-2">
                {[30, 60, 90, 180, 365].map((days) => (
                    <button
                        key={days}
                        onClick={() => setTimeRange(days)}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${timeRange === days
                                ? 'bg-primary-600 text-white'
                                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
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
                    <div className="grid md:grid-cols-4 gap-6">
                        <Card>
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Predictions</p>
                                    <p className="text-3xl font-bold text-primary-600">{stats.totalPredictions}</p>
                                </div>
                                <Calendar className="w-10 h-10 text-primary-600 opacity-20" />
                            </div>
                        </Card>

                        <Card>
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Average Price</p>
                                    <p className="text-3xl font-bold text-primary-600">${stats.avgPrice.toFixed(2)}</p>
                                </div>
                                <TrendingUp className="w-10 h-10 text-primary-600 opacity-20" />
                            </div>
                        </Card>

                        <Card>
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Min Price</p>
                                    <p className="text-3xl font-bold text-green-600">${stats.minPrice.toFixed(2)}</p>
                                </div>
                                <Target className="w-10 h-10 text-green-600 opacity-20" />
                            </div>
                        </Card>

                        <Card>
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">Max Price</p>
                                    <p className="text-3xl font-bold text-red-600">${stats.maxPrice.toFixed(2)}</p>
                                </div>
                                <Target className="w-10 h-10 text-red-600 opacity-20" />
                            </div>
                        </Card>
                    </div>

                    <Card title="Predicted vs Actual Prices">
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

                    <Card title="Prediction Error Over Time">
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

                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div className="flex items-start">
                            <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3" />
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
