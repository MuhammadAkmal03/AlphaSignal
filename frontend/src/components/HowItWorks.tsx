// HowItWorks Component
// Educational section explaining the RL agent

import { useState } from 'react';
import { Brain, Target, TrendingUp, Shield } from 'lucide-react';
import Card from './Card';

const HowItWorks = () => {
    const [activeTab, setActiveTab] = useState(0);

    const tabs = [
        {
            title: 'What is RL?',
            icon: Brain,
            content: (
                <div className="space-y-4">
                    <h3 className="text-xl font-semibold">Reinforcement Learning Explained</h3>
                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                        Reinforcement Learning (RL) is like teaching a robot to trade by rewarding good decisions
                        and penalizing bad ones. Instead of just predicting prices, the agent learns the optimal
                        <strong> when</strong> and <strong>how much</strong> to trade.
                    </p>
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                        <p className="text-sm text-blue-800 dark:text-blue-200">
                            <strong>Key Concept:</strong> The agent interacts with the market environment,
                            takes actions (buy/sell/hold), receives rewards (profit/loss), and learns from experience.
                        </p>
                    </div>
                </div>
            ),
        },
        {
            title: 'Our Approach',
            icon: Target,
            content: (
                <div className="space-y-4">
                    <h3 className="text-xl font-semibold">PPO + XGBoost Hybrid</h3>
                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                        We use <strong>Proximal Policy Optimization (PPO)</strong>, a state-of-the-art RL algorithm,
                        combined with XGBoost price predictions.
                    </p>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <h4 className="font-semibold mb-2">State Space</h4>
                            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                                <li>• XGBoost price prediction</li>
                                <li>• Current position</li>
                                <li>• Market features</li>
                                <li>• Portfolio value</li>
                            </ul>
                        </div>
                        <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <h4 className="font-semibold mb-2">Action Space</h4>
                            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                                <li>• <span className="text-blue-600">HOLD</span>: Maintain position</li>
                                <li>• <span className="text-green-600">LONG</span>: Buy signal</li>
                                <li>• <span className="text-red-600">SHORT</span>: Sell signal</li>
                            </ul>
                        </div>
                    </div>
                    <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                        <h4 className="font-semibold mb-2 text-amber-800 dark:text-amber-200">Reward Function</h4>
                        <p className="text-sm text-amber-700 dark:text-amber-300">
                            Reward = Portfolio Return - Transaction Costs - Risk Penalty
                        </p>
                    </div>
                </div>
            ),
        },
        {
            title: 'Training Process',
            icon: TrendingUp,
            content: (
                <div className="space-y-4">
                    <h3 className="text-xl font-semibold">How the Agent Learned</h3>
                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                        The agent was trained on historical crude oil price data, learning to maximize
                        risk-adjusted returns while minimizing transaction costs.
                    </p>
                    <div className="space-y-3">
                        <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                                <span className="text-primary-600 font-bold">1</span>
                            </div>
                            <div>
                                <h4 className="font-semibold">Data Preparation</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Historical prices, technical indicators, and XGBoost predictions
                                </p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                                <span className="text-primary-600 font-bold">2</span>
                            </div>
                            <div>
                                <h4 className="font-semibold">Training Episodes</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Agent trades through historical periods, learning from outcomes
                                </p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                                <span className="text-primary-600 font-bold">3</span>
                            </div>
                            <div>
                                <h4 className="font-semibold">Policy Optimization</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    PPO algorithm updates the trading policy to improve performance
                                </p>
                            </div>
                        </div>
                        <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                                <span className="text-primary-600 font-bold">4</span>
                            </div>
                            <div>
                                <h4 className="font-semibold">Validation</h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Tested on unseen data to ensure generalization
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            ),
        },
        {
            title: 'Why Use RL?',
            icon: Shield,
            content: (
                <div className="space-y-4">
                    <h3 className="text-xl font-semibold">Advantages Over Pure ML</h3>
                    <div className="grid gap-4">
                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                            <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2">
                                ✓ Transaction Cost Awareness
                            </h4>
                            <p className="text-sm text-green-700 dark:text-green-300">
                                Unlike pure prediction models, RL learns to account for trading costs,
                                avoiding excessive trading that erodes profits.
                            </p>
                        </div>
                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                            <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2">
                                ✓ Optimal Timing
                            </h4>
                            <p className="text-sm text-green-700 dark:text-green-300">
                                Learns when to enter and exit positions, not just what direction to trade.
                            </p>
                        </div>
                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                            <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2">
                                ✓ Risk Management
                            </h4>
                            <p className="text-sm text-green-700 dark:text-green-300">
                                Balances returns with risk through the reward function, leading to more stable performance.
                            </p>
                        </div>
                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                            <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2">
                                ✓ Adaptive Strategy
                            </h4>
                            <p className="text-sm text-green-700 dark:text-green-300">
                                Can adapt to changing market conditions through continuous learning.
                            </p>
                        </div>
                    </div>
                </div>
            ),
        },
    ];

    return (
        <Card>
            <div className="space-y-6">
                <h2 className="text-2xl font-bold">How It Works</h2>

                {/* Tabs */}
                <div className="flex flex-wrap gap-2 border-b border-gray-200 dark:border-gray-700">
                    {tabs.map((tab, index) => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={index}
                                onClick={() => setActiveTab(index)}
                                className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors border-b-2 ${activeTab === index
                                        ? 'border-primary-600 text-primary-600'
                                        : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                {tab.title}
                            </button>
                        );
                    })}
                </div>

                {/* Content */}
                <div className="py-4">
                    {tabs[activeTab].content}
                </div>
            </div>
        </Card>
    );
};

export default HowItWorks;
