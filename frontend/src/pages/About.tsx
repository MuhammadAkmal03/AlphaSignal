import { Github, Linkedin, Mail } from 'lucide-react';

const About = () => {
    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <h1 className="text-4xl font-bold mb-8">About This Project</h1>

            <div className="card mb-8">
                <h2 className="text-2xl font-semibold mb-4">Project Overview</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                    AlphaSignal is an end-to-end machine learning system for crude oil price prediction
                    and automated trading. It combines supervised learning (XGBoost), reinforcement learning (PPO),
                    and real-time news sentiment analysis to generate intelligent trading signals.
                </p>
                <p className="text-gray-600 dark:text-gray-400">
                    Built as a portfolio project to demonstrate full-stack ML engineering capabilities,
                    from data pipeline to production deployment.
                </p>
            </div>

            <div className="card mb-8">
                <h2 className="text-2xl font-semibold mb-4">Technologies Used</h2>
                <div className="grid md:grid-cols-2 gap-4">
                    <div>
                        <h3 className="font-semibold mb-2">Backend</h3>
                        <ul className="list-disc list-inside text-gray-600 dark:text-gray-400 space-y-1">
                            <li>Python & FastAPI</li>
                            <li>XGBoost & Scikit-learn</li>
                            <li>Stable-Baselines3 (RL)</li>
                            <li>Pandas & NumPy</li>
                        </ul>
                    </div>
                    <div>
                        <h3 className="font-semibold mb-2">Frontend</h3>
                        <ul className="list-disc list-inside text-gray-600 dark:text-gray-400 space-y-1">
                            <li>React & TypeScript</li>
                            <li>Tailwind CSS</li>
                            <li>Recharts</li>
                            <li>Vite</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div className="card">
                <h2 className="text-2xl font-semibold mb-4">Connect</h2>
                <div className="flex gap-4">
                    <a
                        href="https://github.com/MuhammadAkmal03/AlphaSignal"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-gray-900 dark:bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors"
                    >
                        <Github className="w-5 h-5" />
                        GitHub
                    </a>
                    <a
                        href="https://linkedin.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Linkedin className="w-5 h-5" />
                        LinkedIn
                    </a>
                    <a
                        href="mailto:your.email@example.com"
                        className="flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                    >
                        <Mail className="w-5 h-5" />
                        Email
                    </a>
                </div>
            </div>
        </div>
    );
};

export default About;
