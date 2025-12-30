// EquityCurveChart Component
// Displays the RL agent's equity curve over time

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';
import Card from './Card';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import { getRLAgent } from '../api/client';
import type { EquityCurveData } from '../types';

const EquityCurveChart = () => {
    const [data, setData] = useState<EquityCurveData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showGross, setShowGross] = useState(true);

    useEffect(() => {
        fetchEquityCurve();
    }, []);

    const fetchEquityCurve = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getRLAgent.equityCurve();
            setData(response.data);
        } catch (err) {
            console.error('Failed to fetch equity curve:', err);
            setError('Failed to load equity curve data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Card><LoadingSpinner /></Card>;
    if (error) return <Card><ErrorMessage message={error} /></Card>;
    if (!data || !data.data?.length) return <Card><p className="text-gray-500">No equity data available</p></Card>;

    return (
        <Card>
            <div className="space-y-4">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-primary-600" />
                        Equity Curve
                    </h2>
                    <div className="flex items-center gap-4">
                        <label className="flex items-center gap-2 text-sm cursor-pointer">
                            <input
                                type="checkbox"
                                checked={showGross}
                                onChange={(e) => setShowGross(e.target.checked)}
                                className="rounded"
                            />
                            <span className="text-gray-600 dark:text-gray-400">Show Gross Equity</span>
                        </label>
                    </div>
                </div>

                {/* Summary Stats */}
                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Initial</p>
                        <p className="text-lg font-bold">${data.summary?.initial_equity?.toFixed(2) || '0.00'}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Final</p>
                        <p className={`text-lg font-bold ${(data.summary?.final_equity || 0) >= (data.summary?.initial_equity || 0)
                            ? 'text-green-600'
                            : 'text-red-600'
                            }`}>
                            ${data.summary?.final_equity?.toFixed(2) || '0.00'}
                        </p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Peak</p>
                        <p className="text-lg font-bold text-blue-600">
                            ${data.summary?.peak_equity?.toFixed(2) || '0.00'}
                        </p>
                    </div>
                </div>

                {/* Chart */}
                <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={data.data}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                            <XAxis
                                dataKey="step"
                                stroke="#9ca3af"
                                label={{ value: 'Time Steps', position: 'insideBottom', offset: -5 }}
                            />
                            <YAxis
                                stroke="#9ca3af"
                                label={{ value: 'Equity', angle: -90, position: 'insideLeft' }}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1f2937',
                                    border: '1px solid #374151',
                                    borderRadius: '8px',
                                }}
                                labelStyle={{ color: '#f3f4f6' }}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="net_equity"
                                stroke="#2563eb"
                                strokeWidth={2}
                                dot={false}
                                name="Net Equity"
                            />
                            {showGross && (
                                <Line
                                    type="monotone"
                                    dataKey="gross_equity"
                                    stroke="#9ca3af"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    dot={false}
                                    name="Gross Equity"
                                />
                            )}
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Info */}
                <p className="text-sm text-gray-500 text-center">
                    Showing {data.summary.data_points} time steps
                </p>
            </div>
        </Card>
    );
};

export default EquityCurveChart;
