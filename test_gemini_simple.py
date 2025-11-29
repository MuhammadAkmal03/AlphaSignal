"""Simple test with explicit error handling"""
import os
import sys
from dotenv import load_dotenv

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

try:
    import google.generativeai as genai
    import pandas as pd
    
    # Load API key
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key loaded: {bool(api_key)}")
    
    # Load news data
    df = pd.read_csv("data/raw/nlp/realtime_news_detailed.csv")
    print(f"Loaded {len(df)} articles")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Simple test prompt with only 3 articles
    articles = df.head(3)
    prompt = f"""Summarize these oil news headlines in 2-3 sentences:

1. {articles.iloc[0]['title']}
2. {articles.iloc[1]['title']}
3. {articles.iloc[2]['title']}
"""
    
    print("\nGenerating summary...")
    response = model.generate_content(prompt)
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(response.text)
    print("="*60)
    print("\n✅ SUCCESS!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
