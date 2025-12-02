import { Link } from 'react-router-dom';
import { TrendingUp, BarChart3, Brain, Newspaper, ArrowRight, Github, Mail, CheckCircle } from 'lucide-react';
import { useState } from 'react';

const LandingPage = () => {
    const [email, setEmail] = useState('');
    const [subscribeLoading, setSubscribeLoading] = useState(false);
    const [subscribeSuccess, setSubscribeSuccess] = useState(false);
    const [subscribeError, setSubscribeError] = useState<string | null>(null);

    const features = [
        {
            icon: <TrendingUp className="w-8 h-8" />,
            title: 'Price Predictions',
            description: 'XGBoost model with 6.6 MAE accuracy for next-day crude oil prices',
        },
        {
            icon: <BarChart3 className="w-8 h-8" />,
            title: 'Backtesting Engine',
            description: 'Comprehensive historical validation with trading strategy simulation',
        },
        {
            icon: <Brain className="w-8 h-8" />,
            title: 'RL Trading Agent',
            description: 'PPO-based reinforcement learning agent with XGBoost alignment',
        },
        {
            icon: <Newspaper className="w-8 h-8" />,
            title: 'News Sentiment',
            description: 'Real-time oil news analysis with AI-powered summaries',
        },
    ];

    const stats = [
        { label: 'Model Accuracy', value: '6.6 MAE' },
        { label: 'Backtest Return', value: '+30%' },
        { label: 'RL Performance', value: '1.30x' },
        { label: 'Data Sources', value: '15+' },
    ];

    const handleSubscribe = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!email) {
            setSubscribeError('Please enter your email address');
            return;
        }

        setSubscribeLoading(true);
        setSubscribeError(null);

        try {
            const response = await fetch('/api/email/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to subscribe');
            }

            setSubscribeSuccess(true);
            setEmail('');
            setTimeout(() => setSubscribeSuccess(false), 5000);
        } catch (err: any) {
            setSubscribeError(err.message || 'Failed to subscribe');
        } finally {
            setSubscribeLoading(false);
        }
    };

    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <section className="relative overflow-hidden bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900 text-white">
                <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
                <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
                    <div className="text-center">
                        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6">
                            <span className="block">Crude Oil Price</span>
                            <span className="block bg-gradient-to-r from-accent-500 to-yellow-400 bg-clip-text text-transparent">
                                Prediction & Trading
                            </span>
                        </h1>
                        <p className="text-xl sm:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
                            ML-powered system combining supervised learning, reinforcement learning,
                            and real-time news sentiment for intelligent oil trading decisions
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link to="/dashboard" className="btn-primary inline-flex items-center justify-center">
                                View Dashboard
                                <ArrowRight className="ml-2 w-5 h-5" />
                            </Link>
                            <a
                                href="https://github.com/MuhammadAkmal03/AlphaSignal"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="btn-secondary inline-flex items-center justify-center bg-white/10 hover:bg-white/20 text-white border-white/20"
                            >
                                <Github className="mr-2 w-5 h-5" />
                                View on GitHub
                            </a>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16">
                        {stats.map((stat, index) => (
                            <div key={index} className="text-center">
                                <div className="text-3xl sm:text-4xl font-bold text-accent-500 mb-2">
                                    {stat.value}
                                </div>
                                <div className="text-sm text-gray-300">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Email Subscription Section */}
            <section className="py-20 bg-white dark:bg-gray-800">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <Mail className="w-16 h-16 text-primary-600 mx-auto mb-4" />
                        <h2 className="text-4xl font-bold mb-4">Stay Updated</h2>
                        <p className="text-xl text-gray-600 dark:text-gray-400">
                            Subscribe to receive daily crude oil price predictions and market insights directly to your inbox
                        </p>
                    </div>

                    <form onSubmit={handleSubscribe} className="max-w-2xl mx-auto">
                        <div className="flex flex-col sm:flex-row gap-4">
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="Enter your email address"
                                className="flex-1 px-6 py-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-lg"
                                disabled={subscribeLoading || subscribeSuccess}
                            />
                            <button
                                type="submit"
                                disabled={subscribeLoading || subscribeSuccess}
                                className="px-8 py-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 whitespace-nowrap"
                            >
                                {subscribeLoading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                        Subscribing...
                                    </>
                                ) : subscribeSuccess ? (
                                    <>
                                        <CheckCircle className="w-5 h-5" />
                                        Subscribed!
                                    </>
                                ) : (
                                    <>
                                        <Mail className="w-5 h-5" />
                                        Subscribe
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Success/Error Messages */}
                        {subscribeSuccess && (
                            <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-2 text-green-700 dark:text-green-300">
                                <CheckCircle className="w-5 h-5" />
                                <span className="font-medium">Successfully subscribed! Check your inbox daily at 8:00 AM.</span>
                            </div>
                        )}

                        {subscribeError && (
                            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300">
                                <span className="font-medium">{subscribeError}</span>
                            </div>
                        )}
                    </form>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 bg-gray-50 dark:bg-gray-900">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold mb-4">Key Features</h2>
                        <p className="text-xl text-gray-600 dark:text-gray-400">
                            End-to-end ML pipeline for crude oil price prediction and trading
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {features.map((feature, index) => (
                            <div key={index} className="card hover:shadow-xl transition-shadow">
                                <div className="text-primary-600 mb-4">{feature.icon}</div>
                                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                                <p className="text-gray-600 dark:text-gray-400">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-800 text-white">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 className="text-4xl font-bold mb-6">Ready to Explore?</h2>
                    <p className="text-xl mb-8 text-gray-200">
                        Dive into the dashboard to see live predictions, backtesting results,
                        and RL agent recommendations
                    </p>
                    <Link to="/dashboard" className="btn-primary bg-white text-primary-600 hover:bg-gray-100">
                        Get Started
                    </Link>
                </div>
            </section>
        </div>
    );
};

export default LandingPage;
