"""
Real-Time Oil News Analyzer
Fetches oil-related news from NewsAPI.org and performs sentiment analysis
"""
import os
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from transformers import pipeline
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

# Fix for transformers/keras compatibility
os.environ["TF_USE_LEGACY_KERAS"] = "1"

# Directories
RAW_NLP = Path("data/raw/nlp")
RAW_NLP.mkdir(parents=True, exist_ok=True)

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Configuration
API_KEY = os.getenv("NEWSAPI_KEY", "fdbdb718eb3f425cbe5f19b62e26d26f")
BASE_URL = "https://newsapi.org/v2/everything"

# Oil-related keywords and entities
OIL_KEYWORDS = [
    "brent crude", "WTI crude", "oil price", "OPEC", "petroleum",
    "crude oil", "energy stocks", "oil market", "oil supply", "oil demand"
]

OIL_COMPANIES = [
    "exxon", "shell", "bp", "chevron", "conocophillips", "totalenergies",
    "eni", "equinor", "petrobras", "saudi aramco", "rosneft", "lukoil"
]

# Initialize sentiment analyzer (lazy loading)
_sentiment_analyzer = None

def get_sentiment_analyzer():
    """Lazy load sentiment analyzer to avoid loading at import"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        print(" Loading sentiment analysis model...")
        # Force PyTorch to avoid TensorFlow/Keras issues
        _sentiment_analyzer = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english",
            framework="pt"  # Explicitly use PyTorch
        )
        print(" Sentiment model loaded")
    return _sentiment_analyzer


def fetch_oil_news(lookback_days=7, max_articles=100):
    """
    Fetch oil-related news from NewsAPI.org
    
    Args:
        lookback_days: Number of days to look back for news
        max_articles: Maximum number of articles to fetch
    
    Returns:
        list: List of article dictionaries
    """
    from_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")
    
    # Check cache
    cache_file = CACHE_DIR / f"news_cache_{from_date}_{to_date}.json"
    if cache_file.exists():
        cache_age = time.time() - cache_file.stat().st_mtime
        if cache_age < 3600:  # Cache valid for 1 hour
            print(f" Using cached news data (age: {int(cache_age/60)} minutes)")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    # Build search query
    query = " OR ".join(OIL_KEYWORDS[:5])  # Limit to avoid too complex query
    
    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": min(max_articles, 100),  # API limit is 100
        "apiKey": API_KEY
    }
    
    print(f"\n Fetching oil news from {from_date} to {to_date}...")
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f" Retrieved {len(articles)} articles (Total available: {data.get('totalResults', 0)})")
        
        # Cache the results
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        return articles
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print(" ERROR: Invalid API key")
        elif response.status_code == 429:
            print(" ERROR: Rate limit exceeded. Using cached data if available.")
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        raise e
    
    except Exception as e:
        print(f" ERROR fetching news: {e}")
        # Try to use cache even if expired
        if cache_file.exists():
            print("  Using expired cache as fallback")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


def extract_oil_entities(text):
    """
    Extract oil company mentions from text
    
    Args:
        text: Article text (title + description)
    
    Returns:
        list: List of mentioned oil companies
    """
    if not text:
        return []
    
    text_lower = text.lower()
    mentioned = []
    
    for company in OIL_COMPANIES:
        if company in text_lower:
            mentioned.append(company.title())
    
    return mentioned


def analyze_sentiment(articles):
    """
    Perform sentiment analysis on articles
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        pd.DataFrame: DataFrame with article data and sentiment scores
    """
    if not articles:
        print("  No articles to analyze")
        return pd.DataFrame()
    
    analyzer = get_sentiment_analyzer()
    
    rows = []
    
    print(f"\n Analyzing sentiment for {len(articles)} articles...")
    
    for i, article in enumerate(articles, 1):
        try:
            # Extract text
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            # Combine title and description for analysis
            text = f"{title}. {description}".strip()
            
            if not text or len(text) < 10:
                continue
            
            # Truncate to 512 tokens (BERT limit)
            text = text[:512]
            
            # Perform sentiment analysis
            sentiment = analyzer(text)[0]
            
            # Convert to score: positive = +score, negative = -score
            score = sentiment['score'] if sentiment['label'] == 'POSITIVE' else -sentiment['score']
            
            # Extract entities
            entities = extract_oil_entities(f"{title} {description}")
            
            # Parse date
            pub_date = article.get('publishedAt', '')
            try:
                date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            rows.append({
                'date': date_str,
                'title': title[:100],  # Truncate for storage
                'source': article.get('source', {}).get('name', 'Unknown'),
                'sentiment_score': round(score, 4),
                'sentiment_label': sentiment['label'],
                'confidence': round(sentiment['score'], 4),
                'oil_companies_mentioned': ', '.join(entities) if entities else 'None',
                'url': article.get('url', '')
            })
            
            if i % 20 == 0:
                print(f"   Processed {i}/{len(articles)} articles...")
        
        except Exception as e:
            print(f" Error analyzing article {i}: {e}")
            continue
    
    df = pd.DataFrame(rows)
    print(f" Sentiment analysis complete: {len(df)} articles processed")
    
    return df


def aggregate_daily_scores(df):
    """
    Aggregate sentiment scores by date
    
    Args:
        df: DataFrame with individual article sentiments
    
    Returns:
        pd.DataFrame: Daily aggregated sentiment scores
    """
    if df.empty:
        return pd.DataFrame(columns=['date', 'news_sentiment', 'article_count', 'positive_ratio'])
    
    df['date'] = pd.to_datetime(df['date'])
    
    daily = df.groupby('date').agg({
        'sentiment_score': 'mean',
        'title': 'count',
        'sentiment_label': lambda x: (x == 'POSITIVE').sum() / len(x)
    }).reset_index()
    
    daily.columns = ['date', 'news_sentiment', 'article_count', 'positive_ratio']
    
    # Round for readability
    daily['news_sentiment'] = daily['news_sentiment'].round(4)
    daily['positive_ratio'] = daily['positive_ratio'].round(4)
    
    return daily


def save_results(df_detailed, df_daily):
    """
    Save analysis results to CSV files
    
    Args:
        df_detailed: Detailed article-level data
        df_daily: Daily aggregated data
    """
    # Save detailed results
    detailed_path = RAW_NLP / "realtime_news_detailed.csv"
    df_detailed.to_csv(detailed_path, index=False)
    print(f"\n Detailed results saved: {detailed_path}")
    
    # Save daily aggregated results
    daily_path = RAW_NLP / "realtime_news_sentiment.csv"
    df_daily.to_csv(daily_path, index=False)
    print(f" Daily sentiment saved: {daily_path}")
    
    # Print summary
    print(f"\n Summary:")
    print(f"   Date Range: {df_daily['date'].min()} to {df_daily['date'].max()}")
    print(f"   Total Articles: {df_detailed.shape[0]}")
    print(f"   Average Sentiment: {df_daily['news_sentiment'].mean():.4f}")
    print(f"   Positive Ratio: {df_daily['positive_ratio'].mean():.2%}")


def run_realtime_news_analyzer(lookback_days=7):
    """
    Main function to run the real-time news analyzer
    
    Args:
        lookback_days: Number of days to fetch news for
    """
    print("=" * 60)
    print("Real-Time Oil News Analyzer")
    print("=" * 60)
    
    # Fetch news
    articles = fetch_oil_news(lookback_days=lookback_days)
    
    if not articles:
        print("\n No articles retrieved. Exiting.")
        return
    
    # Analyze sentiment
    df_detailed = analyze_sentiment(articles)
    
    if df_detailed.empty:
        print("\n No valid articles to analyze. Exiting.")
        return
    
    # Aggregate daily scores
    df_daily = aggregate_daily_scores(df_detailed)
    
    # Save results
    save_results(df_detailed, df_daily)
    
    print("\n" + "=" * 60)
    print(" Analysis Complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_realtime_news_analyzer(lookback_days=7)
