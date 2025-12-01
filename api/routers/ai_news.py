"""
AI News Router
Endpoint for AI-generated news summaries using Groq
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
import sys

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.groq_client import generate_news_summary

router = APIRouter()

NEWS_DATA = Path("data/processed/realtime_news_sentiment.csv")


class NewsSummaryResponse(BaseModel):
    summary: str
    article_count: int
    sentiment_overview: str
    key_topics: list[str]
    generated_at: str


@router.post("/ai-summary", response_model=NewsSummaryResponse)
async def get_ai_news_summary(date: Optional[str] = None):
    """
    Generate AI summary of today's oil news using Groq
    
    Args:
        date: Optional date filter (YYYY-MM-DD), defaults to today
    
    Returns:
        AI-generated summary with key topics and sentiment
    """
    try:
        if not NEWS_DATA.exists():
            raise HTTPException(status_code=404, detail="News data not found")
        
        # Load news data
        df = pd.read_csv(NEWS_DATA)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Filter by date if provided, otherwise get today's news
        if date:
            target_date = pd.to_datetime(date)
            df = df[df['date'].dt.date == target_date.date()]
        else:
            # Get most recent news (last 5 articles)
            df = df.sort_values('date', ascending=False).head(5)
        
        if df.empty:
            return NewsSummaryResponse(
                summary="No news articles available for the selected date.",
                article_count=0,
                sentiment_overview="Neutral",
                key_topics=["Oil Markets"],
                generated_at=datetime.now().isoformat()
            )
        
        # Prepare articles for summarization
        articles = []
        for _, row in df.iterrows():
            articles.append({
                "title": row.get('title', 'Untitled'),
                "sentiment": row.get('sentiment', 'neutral')
            })
        
        # Generate AI summary using Groq
        ai_result = generate_news_summary(articles)
        
        return NewsSummaryResponse(
            summary=ai_result['summary'],
            article_count=len(articles),
            sentiment_overview=ai_result['sentiment_overview'],
            key_topics=ai_result['key_topics'],
            generated_at=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
