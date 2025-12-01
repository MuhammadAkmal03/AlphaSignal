const Dashboard = () => {
    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="card">
                    <h2 className="text-xl font-semibold mb-4">Latest Prediction</h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        Price prediction data will be displayed here
                    </p>
                </div>
                <div className="card">
                    <h2 className="text-xl font-semibold mb-4">News Sentiment</h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        Latest news and sentiment analysis
                    </p>
                </div>
                <div className="card">
                    <h2 className="text-xl font-semibold mb-4">Model Performance</h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        Accuracy metrics and statistics
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
