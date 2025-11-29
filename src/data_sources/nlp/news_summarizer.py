"""
AI-Powered Oil News Summarizer
Generates executive summaries of oil news using LLMs (Gemini/OpenAI)
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Try to import Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed. Install with: pip install google-generativeai")

# Directories
OUTPUT_DIR = Path("data/summaries")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Debug: Show API key status
if __name__ == "__main__":
    print(f"DEBUG: GEMINI_API_KEY loaded: {'Yes' if GEMINI_API_KEY else 'No'}")
    print(f"DEBUG: OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")



def load_news_data(detailed_csv_path="data/raw/nlp/realtime_news_detailed.csv"):
    """Load the detailed news data from CSV"""
    import pandas as pd
    
    csv_path = Path(detailed_csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"News data not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    return df


def prepare_news_context(df, max_articles=20):
    """
    Prepare news articles for LLM summarization
    
    Args:
        df: DataFrame with news articles
        max_articles: Maximum number of articles to include
    
    Returns:
        str: Formatted news context for LLM
    """
    # Sort by date (most recent first) and sentiment confidence
    df_sorted = df.sort_values(['date', 'confidence'], ascending=[False, False])
    df_top = df_sorted.head(max_articles)
    
    context = "# Recent Oil Market News Articles\n\n"
    
    for idx, row in df_top.iterrows():
        context += f"## Article {idx + 1}\n"
        context += f"**Date:** {row['date']}\n"
        context += f"**Source:** {row['source']}\n"
        context += f"**Title:** {row['title']}\n"
        context += f"**Sentiment:** {row['sentiment_label']} ({row['sentiment_score']:.3f})\n"
        
        if row['oil_companies_mentioned'] != 'None':
            context += f"**Companies Mentioned:** {row['oil_companies_mentioned']}\n"
        
        context += "\n---\n\n"
    
    return context


def generate_summary_with_gemini(news_context, api_key):
    """
    Generate summary using Google Gemini
    
    Args:
        news_context: Formatted news articles
        api_key: Gemini API key
    
    Returns:
        str: Generated summary
    """
    if not GEMINI_AVAILABLE:
        raise ImportError("google-generativeai package not installed")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt = f"""You are an expert oil market analyst. Analyze the following recent oil news articles and provide a comprehensive executive summary.

{news_context}

Please provide:

1. **Market Overview** (2-3 sentences)
   - Overall market sentiment and direction
   - Key price movements or predictions

2. **Major Developments** (3-5 bullet points)
   - Most important news events
   - OPEC decisions, geopolitical events, supply/demand changes

3. **Sentiment Analysis**
   - Overall market sentiment (bullish/bearish/neutral)
   - Key factors driving sentiment

4. **Companies in Focus**
   - Which oil companies are making headlines and why

5. **Outlook & Implications** (2-3 sentences)
   - What this means for Brent crude oil prices
   - Short-term price direction expectations

Keep the summary concise, professional, and actionable for traders and analysts.
"""
    
    response = model.generate_content(prompt)
    return response.text


def generate_summary_with_openai(news_context, api_key):
    """
    Generate summary using OpenAI GPT
    
    Args:
        news_context: Formatted news articles
        api_key: OpenAI API key
    
    Returns:
        str: Generated summary
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Install with: pip install openai")
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""You are an expert oil market analyst. Analyze the following recent oil news articles and provide a comprehensive executive summary.

{news_context}

Please provide:

1. **Market Overview** (2-3 sentences)
2. **Major Developments** (3-5 bullet points)
3. **Sentiment Analysis**
4. **Companies in Focus**
5. **Outlook & Implications** (2-3 sentences)

Keep the summary concise, professional, and actionable.
"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert oil market analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content


def generate_news_summary(detailed_csv_path="data/raw/nlp/realtime_news_detailed.csv", 
                         max_articles=5,  # Reduced from 20 to 5 to avoid rate limits
                         use_cache=True):
    """
    Main function to generate AI-powered news summary
    
    Args:
        detailed_csv_path: Path to detailed news CSV
        max_articles: Maximum articles to summarize
        use_cache: Whether to use cached summaries
    
    Returns:
        dict: Summary data with text and metadata
    """
    print("=" * 60)
    print("AI-Powered Oil News Summarizer")
    print("=" * 60)
    
    # Load news data
    print(f"\n📰 Loading news data from {detailed_csv_path}...")
    df = load_news_data(detailed_csv_path)
    print(f"✅ Loaded {len(df)} articles")
    
    # Check cache
    cache_key = f"{df['date'].min()}_{df['date'].max()}_{len(df)}"
    cache_file = CACHE_DIR / f"summary_cache_{cache_key}.json"
    
    if use_cache and cache_file.exists():
        print(f"\n📦 Using cached summary...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached_data = json.load(f)
        print(f"✅ Loaded cached summary from {cache_file}")
        return cached_data
    
    # Prepare context
    print(f"\n🔄 Preparing news context (top {max_articles} articles)...")
    news_context = prepare_news_context(df, max_articles)
    
    # Generate summary with available LLM
    summary_text = None
    llm_used = None
    
    if GEMINI_API_KEY and GEMINI_AVAILABLE:
        print("\n🤖 Generating summary with Google Gemini...")
        try:
            summary_text = generate_summary_with_gemini(news_context, GEMINI_API_KEY)
            llm_used = "Gemini 1.5 Flash"
            print("✅ Summary generated successfully!")
        except Exception as e:
            print(f"❌ Gemini failed: {e}")
    
    if not summary_text and OPENAI_API_KEY:
        print("\n🤖 Generating summary with OpenAI GPT...")
        try:
            summary_text = generate_summary_with_openai(news_context, OPENAI_API_KEY)
            llm_used = "GPT-3.5-turbo"
            print("✅ Summary generated successfully!")
        except Exception as e:
            print(f"❌ OpenAI failed: {e}")
    
    if not summary_text:
        raise RuntimeError("No LLM available. Please set GEMINI_API_KEY or OPENAI_API_KEY in .env")
    
    # Prepare summary data
    summary_data = {
        "generated_at": datetime.now().isoformat(),
        "llm_used": llm_used,
        "articles_analyzed": len(df),
        "articles_summarized": min(max_articles, len(df)),
        "date_range": {
            "start": str(df['date'].min()),
            "end": str(df['date'].max())
        },
        "sentiment_stats": {
            "average_sentiment": float(df['sentiment_score'].mean()),
            "positive_ratio": float((df['sentiment_label'] == 'POSITIVE').sum() / len(df)),
            "total_articles": len(df)
        },
        "summary": summary_text
    }
    
    # Save to cache
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Summary cached to: {cache_file}")
    
    # Save to output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"oil_news_summary_{timestamp}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Oil Market News Summary\n\n")
        f.write(f"**Generated:** {summary_data['generated_at']}\n")
        f.write(f"**AI Model:** {llm_used}\n")
        f.write(f"**Articles Analyzed:** {summary_data['articles_analyzed']}\n")
        f.write(f"**Date Range:** {summary_data['date_range']['start']} to {summary_data['date_range']['end']}\n\n")
        f.write(f"**Average Sentiment:** {summary_data['sentiment_stats']['average_sentiment']:.3f}\n")
        f.write(f"**Positive Ratio:** {summary_data['sentiment_stats']['positive_ratio']:.1%}\n\n")
        f.write("---\n\n")
        f.write(summary_text)
    
    print(f"💾 Summary saved to: {output_file}")
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(summary_text)
    print("=" * 60)
    
    return summary_data


if __name__ == "__main__":
    try:
        summary = generate_news_summary()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure:")
        print("1. You have run realtime_oil_news.py to fetch news")
        print("2. You have set GEMINI_API_KEY or OPENAI_API_KEY in .env")
        print("3. You have installed: pip install google-generativeai")
