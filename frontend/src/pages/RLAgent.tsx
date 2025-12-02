// RL Agent Page
// Comprehensive view of the Reinforcement Learning trading agent

import RecommendationCard from '../components/RecommendationCard';
import PerformanceMetrics from '../components/PerformanceMetrics';
import EquityCurveChart from '../components/EquityCurveChart';
import HowItWorks from '../components/HowItWorks';
import PortfolioSimulator from '../components/PortfolioSimulator';
import BuyHoldComparison from '../components/BuyHoldComparison';
import TradesHistory from '../components/TradesHistory';

const RLAgent = () => {
    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Page Header */}
            <div className="mb-10">
                <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">RL Trading Agent</h1>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    AI-powered trading recommendations using Proximal Policy Optimization (PPO)
                </p>
            </div>

            {/* What You Get Section */}
            <div className="mb-10 p-6 bg-gradient-to-r from-primary-50 to-accent-50 dark:from-primary-900/20 dark:to-accent-900/20 rounded-xl border border-primary-200 dark:border-primary-800 shadow-sm">
                <h2 className="text-2xl font-bold mb-4 text-primary-900 dark:text-primary-100">
                    🎯 How This Helps You Make Better Trading Decisions
                </h2>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg hover:shadow-lg transition-shadow duration-300">
                        <h3 className="font-semibold mb-2 text-green-700 dark:text-green-300">
                            ✓ Smart Entry & Exit Timing
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                            Unlike simple predictions, this AI learns <strong>when</strong> to buy and sell,
                            not just which direction prices will move.
                        </p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg hover:shadow-lg transition-shadow duration-300">
                        <h3 className="font-semibold mb-2 text-blue-700 dark:text-blue-300">
                            ✓ Cost-Aware Trading
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                            The agent accounts for transaction fees and avoids excessive trading
                            that would eat into your profits.
                        </p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg hover:shadow-lg transition-shadow duration-300">
                        <h3 className="font-semibold mb-2 text-purple-700 dark:text-purple-300">
                            ✓ Risk-Adjusted Returns
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                            Trained to maximize returns while managing risk, leading to more
                            stable and sustainable performance.
                        </p>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="space-y-8">
                {/* Current Recommendation - Hero Section */}
                <RecommendationCard />

                {/* Performance Metrics Grid */}
                <div>
                    <h2 className="text-2xl font-bold mb-2">Performance Metrics</h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                        Track how well the AI agent has performed historically. Higher returns and Sharpe ratio are better,
                        while lower drawdown and costs are preferred.
                    </p>
                    <PerformanceMetrics />
                </div>

                {/* Equity Curve Chart */}
                <EquityCurveChart />

                {/* Portfolio Simulator - Interactive Tool */}
                <PortfolioSimulator />

                {/* Buy & Hold Comparison */}
                <BuyHoldComparison />

                {/* Recent Trades History */}
                <TradesHistory />

                {/* Educational Section */}
                <HowItWorks />

                {/* Info Footer */}
                <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 shadow-sm">
                    <div className="flex items-start gap-3">
                        <span className="text-2xl">ℹ️</span>
                        <div>
                            <p className="text-sm text-blue-800 dark:text-blue-200">
                                <strong>About the RL Agent:</strong> This reinforcement learning agent was trained
                                on historical crude oil price data to learn optimal trading strategies. It combines
                                XGBoost price predictions with PPO to make risk-adjusted trading decisions while
                                accounting for transaction costs.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RLAgent;
