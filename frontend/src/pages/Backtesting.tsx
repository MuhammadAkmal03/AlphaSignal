import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Play, TrendingUp, DollarSign, AlertTriangle, Target, Calendar } from 'lucide-react';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { getBacktest } from '../api/client';

interface BacktestResults {
    accuracy_metrics: {
        mae: number;
        rmse: number;
        mape: number;
        directional_accuracy: number;
        correlation: number;
    };
    trading_metrics: {
        total_return_pct: number;
        sharpe_ratio: number;
        max_drawdown_pct: number;
        win_rate: number;
    };
    equity_curve: Array<{ date: string; value: number; drawdown: number }>;
    trades: Array<{ date: string; action: string; price: number; return: number }>;
}

const Backtesting = () => {
    const [lookbackDays, setLookbackDays] = useState(90);
    const [initialCapital, setInitialCapital] = useState(10000);
    const [transactionCost, setTransactionCost] = useState(0.001);
    const [results, setResults] = useState<BacktestResults | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const runBacktest = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await getBacktest.run({
                lookback_days: lookbackDays,
                initial_capital: initialCapital,
            });
            setResults(response.data);
        } catch (err) {
            console.error('Backtest failed:', err);
            setError('Failed to run backtest. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-10">
                <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">Backtesting</h1>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    Test the model's historical performance with custom parameters
                </p>
            </div>

            {/* Configuration Panel */}
            <Card>
                <h2 className="text-2xl font-bold mb-6">Backtest Configuration</h2>

                <div className="grid md:grid-cols-2 gap-6 mb-6">
                    {/* Lookback Period */}
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            <Calendar className="w-4 h-4 inline mr-2" />
                            Lookback Period (Days)
                        </label>
                        <select
                            value={lookbackDays}
                            onChange={(e) => setLookbackDays(Number(e.target.value))}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 bg-white dark:bg-gray-800"
                        >
                            <option value={30}>30 Days</option>
                            <option value={60}>60 Days</option>
                            <option value={90}>90 Days</option>
                            <option value={180}>180 Days</option>
                            <option value={365}>1 Year</option>
                        </select>
                        <p className="text-xs text-gray-500 mt-1">
                            How far back to test the strategy
                        </p>
                    </div>

                    {/* Initial Capital */}
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            <DollarSign className="w-4 h-4 inline mr-2" />
                            Initial Capital ($)
                        </label>
                        <input
                            type="number"
                            value={initialCapital}
                            onChange={(e) => setInitialCapital(Number(e.target.value))}
                            min="1000"
                            max="1000000"
                            step="1000"
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 bg-white dark:bg-gray-800"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            Starting portfolio value
                        </p>
                    </div>

                    {/* Transaction Cost */}
                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium mb-2">
                            Transaction Cost: {(transactionCost * 100).toFixed(2)}%
                        </label>
                        <input
                            type="range"
                            value={transactionCost}
                            onChange={(e) => setTransactionCost(Number(e.target.value))}
                            min="0"
                            max="0.01"
                            step="0.0001"
                            className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>0%</span>
                            <span>1%</span>
                        </div>
                    </div>
                </div>

                {/* Run Button */}
                <button
                    onClick={runBacktest}
                    disabled={loading}
                    className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                    {loading ? (
                        <>
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                            Running Backtest...
                        </>
                    ) : (
                        <>
                            <Play className="w-5 h-5" />
                            Run Backtest
                        </>
                    )}
                </button>
            </Card>

            {/* Error Display */}
            {error && (
                <div className="mt-6">
                    <ErrorMessage message={error} retry={runBacktest} />
                </div>
            )}

            {/* Results Section */}
            {results && !loading && (
                <div className="mt-8 space-y-8">
                    {/* Performance Metrics */}
                    <div>
                        <h2 className="text-2xl font-bold mb-4">Backtest Results</h2>
                        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <Card>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Total Return</p>
                                        <p className={`text-3xl font-bold ${results.trading_metrics.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'
                                            }`}>
                                            {results.trading_metrics.total_return_pct >= 0 ? '+' : ''}
                                            {results.trading_metrics.total_return_pct.toFixed(2)}%
                                        </p>
                                    </div>
                                    <TrendingUp className="w-10 h-10 text-primary-600 opacity-20" />
                                </div>
                            </Card>

                            <Card>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Sharpe Ratio</p>
                                        <p className="text-3xl font-bold text-blue-600">
                                            {results.trading_metrics.sharpe_ratio.toFixed(2)}
                                        </p>
                                    </div>
                                    <Target className="w-10 h-10 text-blue-600 opacity-20" />
                                </div>
                            </Card>

                            <Card>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Max Drawdown</p>
                                        <p className="text-3xl font-bold text-red-600">
                                            {results.trading_metrics.max_drawdown_pct.toFixed(2)}%
                                        </p>
                                    </div>
                                    <AlertTriangle className="w-10 h-10 text-red-600 opacity-20" />
                                </div>
                            </Card>

                            <Card>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Win Rate</p>
                                        <p className="text-3xl font-bold text-green-600">
                                            {results.trading_metrics.win_rate.toFixed(1)}%
                                        </p>
                                    </div>
                                    <Target className="w-10 h-10 text-green-600 opacity-20" />
                                </div>
                            </Card>
                        </div>
                    </div>

                    {/* Prediction Accuracy */}
                    <Card>
                        <h3 className="text-xl font-bold mb-4">Prediction Accuracy</h3>
                        <div className="grid md:grid-cols-3 gap-4">
                            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                                <p className="text-sm text-gray-600 dark:text-gray-400">MAE</p>
                                <p className="text-2xl font-bold">${results.accuracy_metrics.mae.toFixed(2)}</p>
                            </div>
                            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                                <p className="text-sm text-gray-600 dark:text-gray-400">MAPE</p>
                                <p className="text-2xl font-bold">{results.accuracy_metrics.mape.toFixed(2)}%</p>
                            </div>
                            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                                <p className="text-sm text-gray-600 dark:text-gray-400">Directional Accuracy</p>
                                <p className="text-2xl font-bold text-green-600">
                                    {results.accuracy_metrics.directional_accuracy.toFixed(1)}%
                                </p>
                            </div>
                        </div>
                    </Card>

                    {/* Equity Curve */}
                    <Card>
                        <h3 className="text-xl font-bold mb-4">Equity Curve</h3>
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={results.equity_curve}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                                <XAxis dataKey="date" stroke="#9ca3af" />
                                <YAxis stroke="#9ca3af" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1f2937',
                                        border: '1px solid #374151',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#2563eb"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Portfolio Value"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </Card>

                    {/* Drawdown Chart */}
                    <Card>
                        <h3 className="text-xl font-bold mb-4">Drawdown Over Time</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={results.equity_curve}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                                <XAxis dataKey="date" stroke="#9ca3af" />
                                <YAxis stroke="#9ca3af" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1f2937',
                                        border: '1px solid #374151',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="drawdown"
                                    stroke="#ef4444"
                                    fill="#ef4444"
                                    fillOpacity={0.3}
                                    name="Drawdown %"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </Card>

                    {/* Trade Log */}
                    <Card>
                        <h3 className="text-xl font-bold mb-4">Trade Log (Last 10 Trades)</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-gray-200 dark:border-gray-700">
                                        <th className="text-left py-3 px-4 text-sm font-semibold">Date</th>
                                        <th className="text-left py-3 px-4 text-sm font-semibold">Action</th>
                                        <th className="text-right py-3 px-4 text-sm font-semibold">Price</th>
                                        <th className="text-right py-3 px-4 text-sm font-semibold">Return</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {results.trades.slice(-10).reverse().map((trade, index) => (
                                        <tr
                                            key={index}
                                            className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
                                        >
                                            <td className="py-3 px-4 text-sm">{trade.date}</td>
                                            <td className="py-3 px-4">
                                                <span className={`px-2 py-1 rounded text-xs font-medium ${trade.action === 'BUY'
                                                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                                                    : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                                                    }`}>
                                                    {trade.action}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4 text-sm text-right font-mono">
                                                ${trade.price.toFixed(2)}
                                            </td>
                                            <td className={`py-3 px-4 text-sm text-right font-semibold ${trade.return >= 0 ? 'text-green-600' : 'text-red-600'
                                                }`}>
                                                {trade.return >= 0 ? '+' : ''}{trade.return.toFixed(2)}%
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </Card>
                </div>
            )}

            {/* Empty State */}
            {!results && !loading && !error && (
                <div className="mt-8">
                    <Card>
                        <div className="text-center py-12">
                            <Play className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold mb-2">Ready to Backtest</h3>
                            <p className="text-gray-600 dark:text-gray-400">
                                Configure your parameters above and click "Run Backtest" to see historical performance
                            </p>
                        </div>
                    </Card>
                </div>
            )}
        </div>
    );
};

export default Backtesting;
