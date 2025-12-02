import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Brain, TrendingUp, AlertCircle, Info, Sparkles } from 'lucide-react';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

interface FeatureImportanceData {
    feature: string;
    importance: number;
    rank: number;
}

interface SHAPSummary {
    global_importance: FeatureImportanceData[];
    total_features: number;
    model_type: string;
}

const FeatureImportance = () => {
    const [data, setData] = useState<SHAPSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCount, setShowCount] = useState(10);

    useEffect(() => {
        loadFeatureImportance();
    }, []);

    const loadFeatureImportance = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/explainability/summary');
            if (!response.ok) throw new Error('Failed to load feature importance');
            const result = await response.json();
            setData(result);
            setError(null);
        } catch (err) {
            console.error('Failed to load feature importance:', err);
            setError('Failed to load feature importance data');
        } finally {
            setLoading(false);
        }
    };

    const COLORS = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#f0f9ff', '#e0f2fe', '#bae6fd'];

    const displayData = data?.global_importance.slice(0, showCount) || [];
    const topFeature = data?.global_importance[0];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-10">
                <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
                    Feature Importance Analysis
                </h1>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    Understand which features drive crude oil price predictions
                </p>
            </div>

            {loading && <LoadingSpinner />}
            {error && <ErrorMessage message={error} />}

            {!loading && !error && data && (
                <div className="space-y-8">
                    {/* Summary Cards */}
                    <div className="grid md:grid-cols-3 gap-6">
                        <Card className="hover:shadow-xl transition-shadow duration-300">
                            <div className="flex items-center justify-between p-3 bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Total Features</p>
                                    <p className="text-3xl font-bold text-primary-600">{data.total_features}</p>
                                </div>
                                <Brain className="w-10 h-10 text-primary-600 opacity-30" />
                            </div>
                        </Card>

                        <Card className="hover:shadow-xl transition-shadow duration-300">
                            <div className="flex items-center justify-between p-3 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Model Type</p>
                                    <p className="text-2xl font-bold text-green-600">{data.model_type}</p>
                                </div>
                                <Sparkles className="w-10 h-10 text-green-600 opacity-30" />
                            </div>
                        </Card>

                        <Card className="hover:shadow-xl transition-shadow duration-300">
                            <div className="flex items-center justify-between p-3 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg">
                                <div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Top Feature</p>
                                    <p className="text-lg font-bold text-purple-600 truncate">{topFeature?.feature}</p>
                                    <p className="text-xs text-gray-500">Importance: {topFeature?.importance.toFixed(4)}</p>
                                </div>
                                <TrendingUp className="w-10 h-10 text-purple-600 opacity-30" />
                            </div>
                        </Card>
                    </div>

                    {/* Info Box */}
                    <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 shadow-sm">
                        <div className="flex items-start">
                            <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                            <div>
                                <p className="text-sm text-blue-800 dark:text-blue-200">
                                    <strong>What is Feature Importance?</strong> Feature importance shows which input features (technical indicators, price lags, etc.)
                                    have the most influence on the model's predictions. Higher values indicate greater importance in determining crude oil price forecasts.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* View Controls */}
                    <div className="flex items-center gap-4">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Show:</span>
                        {[10, 20, 38].map((count) => (
                            <button
                                key={count}
                                onClick={() => setShowCount(count)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${showCount === count
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-md'
                                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                                    }`}
                            >
                                Top {count}
                            </button>
                        ))}
                    </div>

                    {/* Horizontal Bar Chart */}
                    <Card title="Feature Importance Ranking" className="hover:shadow-xl transition-shadow duration-300">
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                            Features are ranked by their contribution to model predictions. The longer the bar, the more important the feature.
                        </p>
                        <ResponsiveContainer width="100%" height={Math.max(400, displayData.length * 35)}>
                            <BarChart data={displayData} layout="vertical" margin={{ left: 100 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                                <XAxis type="number" stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <YAxis
                                    type="category"
                                    dataKey="feature"
                                    stroke="#6b7280"
                                    style={{ fontSize: '11px' }}
                                    width={90}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1f2937',
                                        border: '1px solid #374151',
                                        borderRadius: '8px',
                                        color: '#fff'
                                    }}
                                    formatter={(value: any) => [value.toFixed(6), 'Importance']}
                                />
                                <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                                    {displayData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </Card>

                    {/* Top 10 Pie Chart */}
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card title="Top 10 Feature Distribution" className="hover:shadow-xl transition-shadow duration-300">
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={data.global_importance.slice(0, 10)}
                                        dataKey="importance"
                                        nameKey="feature"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={100}
                                        label={(entry) => `${entry.feature.substring(0, 10)}...`}
                                    >
                                        {data.global_importance.slice(0, 10).map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value: any) => value.toFixed(6)} />
                                </PieChart>
                            </ResponsiveContainer>
                        </Card>

                        <Card title="Feature Importance Details" className="hover:shadow-xl transition-shadow duration-300">
                            <div className="space-y-3 max-h-[300px] overflow-y-auto custom-scrollbar">
                                {data.global_importance.slice(0, 10).map((feature, index) => (
                                    <div
                                        key={feature.rank}
                                        className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 font-bold text-sm">
                                                {index + 1}
                                            </span>
                                            <span className="font-medium text-gray-900 dark:text-gray-100">
                                                {feature.feature}
                                            </span>
                                        </div>
                                        <span className="text-sm font-semibold text-primary-600">
                                            {(feature.importance * 100).toFixed(2)}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    </div>

                    {/* Insights */}
                    <Card title="Key Insights" className="hover:shadow-xl transition-shadow duration-300">
                        <div className="space-y-4">
                            <div className="flex items-start gap-3 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                                <AlertCircle className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <h3 className="font-semibold text-primary-900 dark:text-primary-100 mb-1">Model Interpretability</h3>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                        Feature importance helps understand which inputs drive predictions, ensuring the model uses logical patterns rather than spurious correlations.
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                <TrendingUp className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <h3 className="font-semibold text-green-900 dark:text-green-100 mb-1">Feature Engineering</h3>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                        Low-importance features can be removed to simplify the model, while high-importance features can be further engineered for better predictions.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </Card>
                </div>
            )}
        </div>
    );
};

export default FeatureImportance;
