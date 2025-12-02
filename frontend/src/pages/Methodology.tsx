const Methodology = () => {
    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-4xl font-bold mb-10 bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">Methodology</h1>
            <div className="space-y-6">
                <div className="card hover:shadow-xl transition-shadow duration-300">
                    <h2 className="text-2xl font-semibold mb-4">Data Pipeline</h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        Technical documentation on data sources and feature engineering
                    </p>
                </div>
                <div className="card hover:shadow-xl transition-shadow duration-300">
                    <h2 className="text-2xl font-semibold mb-4">Model Architecture</h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        XGBoost configuration and training process
                    </p>
                </div>
                <div className="card hover:shadow-xl transition-shadow duration-300">
                    <h2 className="text-2xl font-semibold mb-4">RL Environment</h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        Reinforcement learning setup and reward function
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Methodology;
