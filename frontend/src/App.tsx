import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import Backtesting from './pages/Backtesting'
import RLAgent from './pages/RLAgent'
import Analytics from './pages/Analytics'
import About from './pages/About'

function App() {
    return (
        <Router>
            <div className="min-h-screen">
                <Navbar />
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/backtest" element={<Backtesting />} />
                    <Route path="/rl-agent" element={<RLAgent />} />
                    <Route path="/analytics" element={<Analytics />} />
                    <Route path="/about" element={<About />} />
                </Routes>
            </div>
        </Router>
    )
}

export default App
