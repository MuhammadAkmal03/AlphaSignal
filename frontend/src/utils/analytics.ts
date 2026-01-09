// GA Event Tracking

declare global {
    interface Window {
        gtag: (...args: any[]) => void;
    }
}

export const trackEvent = (
    eventName: string,
    category: string,
    label?: string,
    value?: number
) => {
    if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', eventName, {
            event_category: category,
            event_label: label,
            value: value,
        });
    }
};

export const trackEmailSubscription = () => {
    trackEvent('email_subscription', 'engagement', 'newsletter_signup');
};

export const trackReportSent = () => {
    trackEvent('report_sent', 'engagement', 'instant_report');
};

export const trackDashboardView = () => {
    trackEvent('dashboard_view', 'navigation', 'view_dashboard');
};

export const trackChatbotMessage = () => {
    trackEvent('chatbot_message', 'engagement', 'chatbot_interaction');
};

export const trackBacktestRun = () => {
    trackEvent('backtest_run', 'feature', 'run_backtest');
};

export const trackPredictionView = () => {
    trackEvent('prediction_view', 'feature', 'view_prediction');
};
