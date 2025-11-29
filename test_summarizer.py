"""
Simple test of news summarizer
"""
import sys
sys.path.insert(0, 'src')

try:
    from data_sources.nlp.news_summarizer import generate_news_summary
    
    print("Starting news summarizer test...")
    summary = generate_news_summary()
    print("\n✅ SUCCESS!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
