// PortfolioSimulator Component
// Interactive tool for users to simulate trading with the RL agent

import { useState } from 'react';
import { Calculator, TrendingUp, DollarSign, AlertCircle } from 'lucide-react';
import Card from './Card';

const PortfolioSimulator = () => {
    const [capital, setCapital] = useState(10000);
    const [riskLevel, setRiskLevel] = useState<'conservative' | 'moderate' | 'aggressive'>('moderate');
    const [timeHorizon, setTimeHorizon] = useState(30); // days
    const [showResults, setShowResults] = useState(false);

    // Simulated returns based on historical RL agent performance
    const historicalReturn = 0.452; // 45.2% from actual data
    const sharpeRatio = 1.847;
    const maxDrawdown = 0.156;

    const calculateProjection = () => {
        // Adjust based on risk level
        const riskMultiplier = {
            conservative: 0.5,
            moderate: 1.0,
            aggressive: 1.5,
        }[riskLevel];

        // Time-adjusted return (annualized to daily)
        const dailyReturn = historicalReturn / 365;
        const projectedReturn = capital * (1 + dailyReturn * timeHorizon * riskMultiplier);
        const potentialGain = projectedReturn - capital;
        const potentialLoss = capital * maxDrawdown * riskMultiplier;

        return {
            projectedValue: projectedReturn,
            potentialGain,
            potentialLoss,
            returnPercent: (potentialGain / capital) * 100,
        };
    };

    const results = calculateProjection();

    return (
        <Card>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center gap-2">
                    <Calculator className="w-6 h-6 text-primary-600" />
                    <h2 className="text-2xl font-bold">Portfolio Simulator</h2>
                </div>

                <p className="text-gray-600 dark:text-gray-400">
                    See how the RL agent could have performed with your capital based on historical data.
                </p>

                {/* Input Controls */}
                <div className="grid md:grid-cols-2 gap-6">
                    {/* Initial Capital */}
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Initial Capital ($)
                        </label>
                        <input
                            type="number"
                            value={capital}
                            onChange={(e) => setCapital(Number(e.target.value))}
                            min="1000"
                            max="1000000"
                            step="1000"
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 bg-white dark:bg-gray-800"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            How much would you invest?
                        </p>
                    </div>

                    {/* Time Horizon */}
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Time Horizon (Days)
                        </label>
                        <input
                            type="range"
                            value={timeHorizon}
                            onChange={(e) => setTimeHorizon(Number(e.target.value))}
                            min="7"
                            max="365"
                            className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>7 days</span>
                            <span className="font-semibold text-primary-600">{timeHorizon} days</span>
                            <span>1 year</span>
                        </div>
                    </div>

                    {/* Risk Level */}
                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium mb-2">
                            Risk Tolerance
                        </label>
                        <div className="grid grid-cols-3 gap-3">
                            {(['conservative', 'moderate', 'aggressive'] as const).map((level) => (
                                <button
                                    key={level}
                                    onClick={() => setRiskLevel(level)}
                                    className={`p-3 rounded-lg border-2 transition-all ${riskLevel === level
                                            ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/30'
                                            : 'border-gray-300 dark:border-gray-600 hover:border-primary-400'
                                        }`}
                                >
                                    <div className="font-semibold capitalize">{level}</div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        {level === 'conservative' && '50% of full strategy'}
                                        {level === 'moderate' && '100% of full strategy'}
                                        {level === 'aggressive' && '150% of full strategy'}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Calculate Button */}
                <button
                    onClick={() => setShowResults(true)}
                    className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
                >
                    Calculate Projection
                </button>

                {/* Results */}
                {showResults && (
                    <div className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h3 className="font-semibold text-lg">Projected Results</h3>

                        <div className="grid md:grid-cols-3 gap-4">
                            {/* Projected Value */}
                            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                <div className="flex items-center gap-2 mb-2">
                                    <DollarSign className="w-5 h-5 text-blue-600" />
                                    <span className="text-sm text-blue-700 dark:text-blue-300">
                                        Projected Value
                                    </span>
                                </div>
                                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                                    ${results.projectedValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                                </p>
                            </div>

                            {/* Potential Gain */}
                            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                                <div className="flex items-center gap-2 mb-2">
                                    <TrendingUp className="w-5 h-5 text-green-600" />
                                    <span className="text-sm text-green-700 dark:text-green-300">
                                        Potential Gain
                                    </span>
                                </div>
                                <p className="text-2xl font-bold text-green-900 dark:text-green-100">
                                    +${results.potentialGain.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                                </p>
                                <p className="text-sm text-green-700 dark:text-green-300">
                                    ({results.returnPercent.toFixed(2)}%)
                                </p>
                            </div>

                            {/* Max Risk */}
                            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                                <div className="flex items-center gap-2 mb-2">
                                    <AlertCircle className="w-5 h-5 text-red-600" />
                                    <span className="text-sm text-red-700 dark:text-red-300">
                                        Max Drawdown Risk
                                    </span>
                                </div>
                                <p className="text-2xl font-bold text-red-900 dark:text-red-100">
                                    -${results.potentialLoss.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                                </p>
                            </div>
                        </div>

                        {/* Disclaimer */}
                        <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                            <p className="text-sm text-amber-800 dark:text-amber-200">
                                <strong>⚠️ Important:</strong> This is a simulation based on historical performance.
                                Past performance does not guarantee future results. Actual returns may vary significantly.
                                Always consult with a financial advisor before making investment decisions.
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </Card>
    );
};

export default PortfolioSimulator;
