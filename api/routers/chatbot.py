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

router = APIRouter()

# Data paths
PREDICTION_LOG = Path("data/final/prediction/prediction_log.csv")
PERFORMANCE_METRICS = Path("data/final/prediction/performance_metrics.csv")
NEWS_DATA = Path("data/processed/realtime_news_sentiment.csv")


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
        if PREDICTION_LOG.exists():
            df = pd.read_csv(PREDICTION_LOG)
            if not df.empty:
                latest = df.iloc[-1]
                context["latest_prediction"] = f"{float(latest['predicted']):.2f}"
                context["total_predictions"] = len(df)
        
        # Get model metrics
        if PERFORMANCE_METRICS.exists():
            metrics_df = pd.read_csv(PERFORMANCE_METRICS)
            if not metrics_df.empty:
                latest_metrics = metrics_df.iloc[-1]
                context["mae"] = f"{float(latest_metrics['MAE']):.2f}"
                context["mape"] = f"{float(latest_metrics['MAPE']):.2f}"
        
        # Get news sentiment
        if NEWS_DATA.exists():
            news_df = pd.read_csv(NEWS_DATA)
            if not news_df.empty:
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
