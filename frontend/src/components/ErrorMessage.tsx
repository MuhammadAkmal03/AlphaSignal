// Error Message Component
// Displays error messages in a consistent, user-friendly way

import { AlertCircle } from 'lucide-react';

// ============================================
// LESSON: Props with Default Values
// ============================================

interface ErrorMessageProps {
    message: string;
    retry?: () => void;  // Optional function to retry the failed operation
}

const ErrorMessage = ({ message, retry }: ErrorMessageProps) => {
    return (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-start">
                {/* Icon from lucide-react library */}
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-3" />

                <div className="flex-1">
                    <p className="text-red-800 dark:text-red-200">{message}</p>

                    {/* Conditional Rendering: Only show retry button if retry function provided */}
                    {retry && (
                        <button
                            onClick={retry}
                            className="mt-2 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200 font-medium"
                        >
                            Try Again
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ErrorMessage;

// ============================================
// LESSON: Event Handlers
// ============================================
// onClick={retry} passes the retry function to the button
// When clicked, it calls retry()
// This is how we handle user interactions in React
