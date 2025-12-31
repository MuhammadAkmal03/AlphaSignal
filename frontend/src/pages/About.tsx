import { Github, Linkedin, Mail, TrendingUp, Brain, Zap, Target, BarChart3, MessageCircle } from 'lucide-react';

const About = () => {
    return (
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-4xl font-bold mb-10 bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">About AlphaSignal</h1>

            {/* Project Overview */}
            <div className="card mb-8 hover:shadow-xl transition-shadow duration-300">
                <h2 className="text-2xl font-semibold mb-4">Project Overview</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                    <strong>AlphaSignal</strong> is a comprehensive machine learning system designed to predict crude oil prices and generate intelligent trading signals. This end-to-end solution combines cutting-edge AI techniques with modern web technologies to deliver actionable insights for traders and investors.
                </p>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                    The system integrates <strong>supervised learning</strong> (XGBoost) for price predictions, <strong>reinforcement learning</strong> (PPO) for optimal trading strategies, and <strong>real-time news sentiment analysis</strong> to capture market sentiment. All of this is packaged in a beautiful, user-friendly interface with automated email reports and an AI-powered chatbot assistant.
                </p>
                <p className="text-gray-600 dark:text-gray-400">
                    Built as a portfolio project to demonstrate full-stack ML engineering capabilities, from data pipeline design to production-ready deployment.
                </p>
            </div>

            {/* Key Features */}
            <div className="card mb-8 hover:shadow-xl transition-shadow duration-300">
                <h2 className="text-2xl font-semibold mb-6">Key Features</h2>
                <div className="grid md:grid-cols-2 gap-6">
                    <div className="flex gap-4">
                        <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                                <TrendingUp className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                            </div>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-2">Price Predictions</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                XGBoost model trained on historical data with technical indicators and sentiment features for accurate daily predictions.
                            </p>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                                <Brain className="w-6 h-6 text-green-600 dark:text-green-400" />
                            </div>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-2">RL Trading Agent</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Proximal Policy Optimization (PPO) agent that learns optimal buy/sell/hold strategies while accounting for transaction costs.
                            </p>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                                <BarChart3 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                            </div>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-2">Backtesting Engine</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Comprehensive backtesting system to evaluate model performance with customizable parameters and detailed metrics.
                            </p>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                                <MessageCircle className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                            </div>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-2">AI Chatbot</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Intelligent assistant powered by Groq API to answer questions about predictions, market trends, and system features.
                            </p>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
                                <Zap className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                            </div>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-2">Real-time Analytics</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Interactive dashboards with live predictions, performance metrics, and historical trend analysis.
                            </p>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
                                <Target className="w-6 h-6 text-red-600 dark:text-red-400" />
                            </div>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-2">Email Notifications</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Automated daily reports and instant predictions delivered directly to your inbox with subscription management.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Technical Architecture */}
            <div className="card mb-8 hover:shadow-xl transition-shadow duration-300">
                <h2 className="text-2xl font-semibold mb-6">Technical Architecture</h2>

                <div className="mb-6">
                    <h3 className="font-semibold mb-3 text-lg">Machine Learning Pipeline</h3>
                    <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg">
                        <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                            <li className="flex items-start gap-2">
                                <span className="text-primary-600 font-bold">1.</span>
                                <span><strong>Data Collection:</strong> Historical crude oil prices, technical indicators (RSI, MACD, Bollinger Bands), and news sentiment</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-primary-600 font-bold">2.</span>
                                <span><strong>Feature Engineering:</strong> 50+ features including lag features, rolling statistics, and sentiment scores</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-primary-600 font-bold">3.</span>
                                <span><strong>Model Training:</strong> XGBoost with hyperparameter tuning and cross-validation</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-primary-600 font-bold">4.</span>
                                <span><strong>RL Training:</strong> PPO agent trained on historical data with custom reward function</span>
                            </li>
                            <li className="flex items-start gap-2">
                                <span className="text-primary-600 font-bold">5.</span>
                                <span><strong>Deployment:</strong> FastAPI backend serving predictions via REST API</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                    <div>
                        <h3 className="font-semibold mb-3">Backend</h3>
                        <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>Python 3.10+</li>
                            <li>FastAPI (REST API)</li>
                            <li>XGBoost (Predictions)</li>
                            <li>Stable-Baselines3 (RL)</li>
                            <li>Pandas & NumPy</li>
                            <li>Scikit-learn</li>
                            <li>SMTP (Email)</li>
                            <li>Groq API (Chatbot)</li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="font-semibold mb-3">Frontend</h3>
                        <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>React 18</li>
                            <li>TypeScript</li>
                            <li>Tailwind CSS</li>
                            <li>Recharts (Visualization)</li>
                            <li>React Router</li>
                            <li>Vite (Build Tool)</li>
                            <li>Lucide Icons</li>
                            <li>Axios (HTTP Client)</li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="font-semibold mb-3">DevOps & Tools</h3>
                        <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            <li>Git & GitHub</li>
                            <li>Environment Variables</li>
                            <li>CORS Configuration</li>
                            <li>CSV Data Storage</li>
                            <li>Error Handling</li>
                            <li>API Documentation</li>
                            <li>Responsive Design</li>
                            <li>Dark Mode Support</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Connect Section */}
            <div className="card hover:shadow-xl transition-shadow duration-300">
                <h2 className="text-2xl font-semibold mb-4">Connect & Collaborate</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Interested in this project or want to collaborate? Feel free to reach out through any of the platforms below. The source code is available on GitHub for review and contributions.
                </p>
                <div className="flex flex-wrap gap-4">
                    <a
                        href="https://github.com/MuhammadAkmal03/AlphaSignal"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-6 py-3 bg-gray-900 dark:bg-gray-700 text-white rounded-lg hover:bg-gray-800 hover:shadow-lg transition-all duration-200"
                    >
                        <Github className="w-5 h-5" />
                        View on GitHub
                    </a>
                    <a
                        href="https://linkedin.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 hover:shadow-lg transition-all duration-200"
                    >
                        <Linkedin className="w-5 h-5" />
                        Connect on LinkedIn
                    </a>
                    <a
                        href="mailto:your.email@example.com"
                        className="flex items-center gap-2 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 hover:shadow-lg transition-all duration-200"
                    >
                        <Mail className="w-5 h-5" />
                        Send Email
                    </a>
                </div>
            </div>
        </div>
    );
};

export default About;
