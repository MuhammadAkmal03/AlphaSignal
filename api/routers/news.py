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
from services.gcs_data_loader import read_csv_from_gcs, read_text_from_gcs

router = APIRouter()

NEWS_DATA_GCS = "data/news/realtime_news_sentiment.csv"
NEWS_SUMMARY_GCS = "data/news/news_summary.json"


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
        print(f"Loading news from GCS: {NEWS_DATA_GCS}")
        df = read_csv_from_gcs(NEWS_DATA_GCS)
        print(f"News data loaded: {df is not None}, Empty: {df.empty if df is not None else 'N/A'}")
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="News data not found or empty")
        
        print(f"News columns: {df.columns.tolist()}")
        print(f"News shape: {df.shape}")
        
        df['date'] = pd.to_datetime(df['date'])
        
        # Get most recent articles
        df = df.sort_values('date', ascending=False).head(limit)
        
        articles = []
        for _, row in df.iterrows():
            # The CSV has 'sentiment_label' column, not 'sentiment'
            sentiment = row.get('sentiment_label', row.get('sentiment', 'neutral'))
            articles.append(NewsArticle(
                title=row.get('title', 'No title'),
                sentiment=sentiment.lower() if isinstance(sentiment, str) else 'neutral',
                score=float(row.get('sentiment_score', 0.0)),
                published_at=row['date'].isoformat()
            ))
        
        print(f"Returning {len(articles)} articles")
        return {"articles": articles, "count": len(articles)}
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error loading news: {str(e)}")
        print(f"Traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error loading news: {str(e)}")


@router.get("/summary", response_model=NewsSummary)
async def get_news_summary():
    """Get AI-generated news summary"""
    try:
        content = read_text_from_gcs(NEWS_SUMMARY_GCS)
        if content is None:
            raise HTTPException(status_code=404, detail="News summary not found")
        
        data = json.loads(content)
        
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
        df = read_csv_from_gcs(NEWS_DATA_GCS)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="News data not found")
        
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
