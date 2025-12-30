"""
Chatbot Router
Interactive AI assistant using Groq
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import pandas as pd
import sys

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.groq_client import chat_completion
from services.gcs_data_loader import read_csv_from_gcs

router = APIRouter()

# GCS data paths
PREDICTION_LOG_GCS = "data/prediction/prediction_log.csv"
PERFORMANCE_METRICS_GCS = "data/prediction/performance_metrics.csv"
NEWS_DATA_GCS = "data/news/realtime_news_sentiment.csv"


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    timestamp: str


def build_context() -> dict:
    """Build context from current system data"""
    context = {
        "latest_prediction": "N/A",
        "mae": "N/A",
        "mape": "N/A",
        "total_predictions": 0,
        "news_sentiment": "Neutral"
    }
    
    try:
        # Get latest prediction
        df = read_csv_from_gcs(PREDICTION_LOG_GCS)
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            context["latest_prediction"] = f"{float(latest['predicted']):.2f}"
            context["total_predictions"] = len(df)
        
        # Get model metrics
        metrics_df = read_csv_from_gcs(PERFORMANCE_METRICS_GCS)
        if metrics_df is not None and not metrics_df.empty:
            latest_metrics = metrics_df.iloc[-1]
            context["mae"] = f"{float(latest_metrics['MAE']):.2f}"
            context["mape"] = f"{float(latest_metrics['MAPE']):.2f}"
        
        # Get news sentiment
        news_df = read_csv_from_gcs(NEWS_DATA_GCS)
        if news_df is not None and not news_df.empty:
            # Get most recent sentiment
            sentiment_counts = news_df['sentiment'].value_counts()
            if len(sentiment_counts) > 0:
                context["news_sentiment"] = sentiment_counts.index[0].capitalize()
    
    except Exception as e:
        print(f"Error building context: {e}")
    
    return context


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with AlphaSignal AI Assistant
    
    Args:
        request: ChatRequest with user message and conversation history
    
    Returns:
        AI assistant's response
    """
    try:
        # Build context from current data
        context = build_context()
        
        # Convert Pydantic models to dicts for Groq
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Get AI response
        reply = chat_completion(
            message=request.message,
            context=context,
            history=history
        )
        
        return ChatResponse(
            reply=reply,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
