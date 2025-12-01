"""
News Router
Endpoints for news sentiment and summaries
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import pandas as pd
import json

router = APIRouter()

NEWS_DATA = Path("data/processed/realtime_news_sentiment.csv")
NEWS_SUMMARY = Path("data/processed/news_summary.json")


class NewsArticle(BaseModel):
    title: str
    sentiment: str
    score: float
    published_at: str


class NewsSummary(BaseModel):
    summary: str
    article_count: int
    overall_sentiment: str
    generated_at: str


@router.get("/latest")
async def get_latest_news(limit: Optional[int] = 5):
    """Get latest news articles with sentiment"""
    try:
        if not NEWS_DATA.exists():
            raise HTTPException(status_code=404, detail="News data not found")
        
        df = pd.read_csv(NEWS_DATA)
        df['date'] = pd.to_datetime(df['date'])
        
        # Get most recent articles
        df = df.sort_values('date', ascending=False).head(limit)
        
        articles = []
        for _, row in df.iterrows():
            articles.append(NewsArticle(
                title=row.get('title', 'No title'),
                sentiment=row.get('sentiment', 'neutral'),
                score=float(row.get('sentiment_score', 0.0)),
                published_at=row['date'].isoformat()
            ))
        
        return {"articles": articles, "count": len(articles)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading news: {str(e)}")


@router.get("/summary", response_model=NewsSummary)
async def get_news_summary():
    """Get AI-generated news summary"""
    try:
        if not NEWS_SUMMARY.exists():
            raise HTTPException(status_code=404, detail="News summary not found")
        
        with open(NEWS_SUMMARY, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return NewsSummary(
            summary=data.get('summary', 'No summary available'),
            article_count=data.get('article_count', 0),
            overall_sentiment=data.get('overall_sentiment', 'neutral'),
            generated_at=data.get('generated_at', '')
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading summary: {str(e)}")


@router.get("/sentiment-stats")
async def get_sentiment_stats():
    """Get aggregated sentiment statistics"""
    try:
        if not NEWS_DATA.exists():
            raise HTTPException(status_code=404, detail="News data not found")
        
        df = pd.read_csv(NEWS_DATA)
        
        # Calculate sentiment distribution
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        
        # Calculate average sentiment score
        avg_score = float(df['sentiment_score'].mean())
        
        # Get recent trend (last 7 days)
        df['date'] = pd.to_datetime(df['date'])
        recent = df[df['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]
        recent_avg = float(recent['sentiment_score'].mean()) if not recent.empty else 0.0
        
        return {
            "sentiment_distribution": sentiment_counts,
            "average_score": avg_score,
            "recent_trend": recent_avg,
            "total_articles": len(df)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")
