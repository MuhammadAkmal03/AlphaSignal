import { useState } from 'react';
import { X, Mail, Send, Bell, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../api/client';

interface EmailReportModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const EmailReportModal = ({ isOpen, onClose }: EmailReportModalProps) => {
    const [activeTab, setActiveTab] = useState<'instant' | 'subscribe'>('instant');
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSendReport = async () => {
        if (!email) {
            setError('Please enter your email address');
            return;
        }

        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            const response = await api.post('/email/send-report', { email });
            setSuccess(true);
            setTimeout(() => {
                setEmail('');
                setSuccess(false);
                onClose();
            }, 2000);
        } catch (err: any) {
            setError(err.message || 'Failed to send report');
        } finally {
            setLoading(false);
        }
    };

    const handleSubscribe = async () => {
        if (!email) {
            setError('Please enter your email address');
            return;
        }

        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            const response = await api.post('/email/subscribe', { email });
            setSuccess(true);
            setTimeout(() => {
                setEmail('');
                setSuccess(false);
                onClose();
            }, 2000);
        } catch (err: any) {
            setError(err.message || 'Failed to subscribe');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                        Email Reports
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b dark:border-gray-700">
                    <button
                        onClick={() => {
                            setActiveTab('instant');
                            setError(null);
                            setSuccess(false);
                        }}
                        className={`flex-1 py-3 px-4 font-medium transition-colors ${activeTab === 'instant'
                            ? 'border-b-2 border-primary-600 text-primary-600'
                            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                            }`}
                    >
                        <Mail className="w-4 h-4 inline mr-2" />
                        Send Now
                    </button>
                    <button
                        onClick={() => {
                            setActiveTab('subscribe');
                            setError(null);
                            setSuccess(false);
                        }}
                        className={`flex-1 py-3 px-4 font-medium transition-colors ${activeTab === 'subscribe'
                            ? 'border-b-2 border-primary-600 text-primary-600'
                            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                            }`}
                    >
                        <Bell className="w-4 h-4 inline mr-2" />
                        Subscribe
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {activeTab === 'instant' ? (
                        <div>
                            <p className="text-gray-600 dark:text-gray-400 mb-4">
                                Get an instant email with the latest crude oil price prediction and model performance metrics.
                            </p>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="your.email@example.com"
                                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-4"
                            />
                            <button
                                onClick={handleSendReport}
                                disabled={loading || success}
                                className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                        Sending...
                                    </>
                                ) : success ? (
                                    <>
                                        <CheckCircle className="w-5 h-5" />
                                        Sent!
                                    </>
                                ) : (
                                    <>
                                        <Send className="w-5 h-5" />
                                        Send Report
                                    </>
                                )}
                            </button>
                        </div>
                    ) : (
                        <div>
                            <p className="text-gray-600 dark:text-gray-400 mb-4">
                                Subscribe to receive daily prediction reports automatically every morning at 8:00 AM.
                            </p>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="your.email@example.com"
                                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-4"
                            />
                            <button
                                onClick={handleSubscribe}
                                disabled={loading || success}
                                className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                        Subscribing...
                                    </>
                                ) : success ? (
                                    <>
                                        <CheckCircle className="w-5 h-5" />
                                        Subscribed!
                                    </>
                                ) : (
                                    <>
                                        <Bell className="w-5 h-5" />
                                        Subscribe to Daily Reports
                                    </>
                                )}
                            </button>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 text-center">
                                You can unsubscribe anytime from the email footer
                            </p>
                        </div>
                    )}

                    {/* Success/Error Messages */}
                    {success && (
                        <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-2 text-green-700 dark:text-green-300">
                            <CheckCircle className="w-5 h-5" />
                            <span className="text-sm font-medium">
                                {activeTab === 'instant' ? 'Report sent successfully!' : 'Successfully subscribed!'}
                            </span>
                        </div>
                    )}

                    {error && (
                        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2 text-red-700 dark:text-red-300">
                            <AlertCircle className="w-5 h-5" />
                            <span className="text-sm font-medium">{error}</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default EmailReportModal;
