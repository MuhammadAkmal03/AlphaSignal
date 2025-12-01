// PerformanceMetrics Component
// Displays key RL agent performance metrics in a grid

import { useEffect, useState } from 'react';
import { TrendingUp, DollarSign, Activity, AlertTriangle, Coins, Target } from 'lucide-react';
import Card from './Card';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import { getRLAgent } from '../api/client';
import type { RLPerformance } from '../types';

const PerformanceMetrics = () => {
    const [performance, setPerformance] = useState<RLPerformance | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchPerformance();
    }, []);

    const fetchPerformance = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getRLAgent.performance();
            setPerformance(response.data);
        } catch (err) {
            console.error('Failed to fetch RL performance:', err);
            setError('Failed to load performance metrics');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Card><LoadingSpinner /></Card>;
    if (error) return <Card><ErrorMessage message={error} /></Card>;
    if (!performance) return null;

    const metrics = [
        {
            label: 'Net Total Return',
            value: `${(performance.net_total_return * 100).toFixed(2)}%`,
            icon: TrendingUp,
            color: performance.net_total_return >= 0 ? 'text-green-600' : 'text-red-600',
            bgColor: performance.net_total_return >= 0 ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30',
        },
        {
            label: 'Gross Total Return',
            value: `${(performance.gross_total_return * 100).toFixed(2)}%`,
            icon: DollarSign,
            color: 'text-blue-600',
            bgColor: 'bg-blue-100 dark:bg-blue-900/30',
        },
        {
            label: 'Sharpe Ratio',
            value: performance.sharpe_ratio.toFixed(3),
            icon: Activity,
            color: performance.sharpe_ratio >= 1 ? 'text-green-600' : 'text-yellow-600',
            bgColor: performance.sharpe_ratio >= 1 ? 'bg-green-100 dark:bg-green-900/30' : 'bg-yellow-100 dark:bg-yellow-900/30',
            tooltip: 'Risk-adjusted return (higher is better)',
        },
        {
            label: 'Max Drawdown',
            value: `${(performance.max_drawdown * 100).toFixed(2)}%`,
            icon: AlertTriangle,
            color: 'text-red-600',
            bgColor: 'bg-red-100 dark:bg-red-900/30',
            tooltip: 'Largest peak-to-trough decline',
        },
        {
            label: 'Total Costs',
            value: `${(performance.total_costs * 100).toFixed(2)}%`,
            icon: Coins,
            color: 'text-gray-600',
            bgColor: 'bg-gray-100 dark:bg-gray-800',
            tooltip: 'Transaction costs incurred',
        },
        {
            label: 'Net Profit',
            value: `${((performance.gross_total_return - performance.total_costs) * 100).toFixed(2)}%`,
            icon: Target,
            color: (performance.gross_total_return - performance.total_costs) >= 0 ? 'text-green-600' : 'text-red-600',
            bgColor: (performance.gross_total_return - performance.total_costs) >= 0 ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30',
        },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {metrics.map((metric, index) => {
                const Icon = metric.icon;
                return (
                    <Card key={index}>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <div className={`p-3 rounded-lg ${metric.bgColor}`}>
                                    <Icon className={`w-6 h-6 ${metric.color}`} />
                                </div>
                                {metric.tooltip && (
                                    <span
                                        className="text-xs text-gray-500 cursor-help"
                                        title={metric.tooltip}
                                    >
                                        ⓘ
                                    </span>
                                )}
                            </div>
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    {metric.label}
                                </p>
                                <p className={`text-2xl font-bold ${metric.color}`}>
                                    {metric.value}
                                </p>
                            </div>
                        </div>
                    </Card>
                );
            })}
        </div>
    );
};

export default PerformanceMetrics;
