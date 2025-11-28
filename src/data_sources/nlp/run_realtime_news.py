"""
Standalone runner for Real-Time Oil News Analyzer
"""
from realtime_oil_news import run_realtime_news_analyzer

if __name__ == "__main__":
    # Fetch and analyze news from the past 7 days
    run_realtime_news_analyzer(lookback_days=7)
