import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Navbar from './components/Navbar';
import Chatbot from './components/Chatbot';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Backtesting from './pages/Backtesting';
import RLAgent from './pages/RLAgent';
import Analytics from './pages/Analytics';
import About from './pages/About';

function App() {
    return (
        <ThemeProvider>
            <Router>
                <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-200">
                    <Navbar />
                    <Routes>
                        <Route path="/" element={<LandingPage />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/backtest" element={<Backtesting />} />
                        <Route path="/backtesting" element={<Backtesting />} />
                        <Route path="/rl-agent" element={<RLAgent />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/about" element={<About />} />
                    </Routes>
                    {/* Chatbot available on all pages */}
                    <Chatbot />
                </div>
            </Router>
        </ThemeProvider>
    );
}

export default App;
