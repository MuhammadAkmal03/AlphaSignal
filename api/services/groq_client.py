"""
Groq API Client Service
Handles AI completions for news summarization and chatbot
"""
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client (optional - will be None if API key not set)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None


def generate_news_summary(news_articles: list) -> dict:
    """
    Generate AI summary of news articles using Groq
    
    Args:
        news_articles: List of news article dicts with 'title' and 'sentiment'
    
    Returns:
        dict with summary, key_topics, sentiment_overview
    """
    # Check if client is available
    if not client:
        return {
            "summary": "AI summarization not available. Please configure GROQ_API_KEY.",
            "key_topics": ["Oil Markets"],
            "sentiment_overview": "Neutral"
        }
    
    # Format articles for prompt
    articles_text = "\n".join([
        f"- {article['title']} (Sentiment: {article.get('sentiment', 'neutral')})"
        for article in news_articles
    ])
    
    prompt = f"""You are an expert oil market analyst. Summarize the following news articles about crude oil prices.

Articles:
{articles_text}

Provide:
1. A concise 3-4 sentence summary of the key developments
2. List 3-5 key topics (comma-separated)
3. Overall market sentiment (Positive/Negative/Neutral/Mixed)

Format your response as:
SUMMARY: [your summary]
TOPICS: [topic1, topic2, topic3]
SENTIMENT: [sentiment]
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated to current model
            messages=[
                {"role": "system", "content": "You are an expert oil market analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Parse response
        lines = content.split('\n')
        summary = ""
        topics = []
        sentiment = "Neutral"
        
        for line in lines:
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("TOPICS:"):
                topics = [t.strip() for t in line.replace("TOPICS:", "").split(',')]
            elif line.startswith("SENTIMENT:"):
                sentiment = line.replace("SENTIMENT:", "").strip()
        
        return {
            "summary": summary or content[:300],  # Fallback to first 300 chars
            "key_topics": topics[:5] if topics else ["Oil Markets"],
            "sentiment_overview": sentiment
        }
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        return {
            "summary": "Unable to generate summary at this time.",
            "key_topics": ["Oil Markets"],
            "sentiment_overview": "Neutral"
        }


def chat_completion(message: str, context: dict, history: list = None) -> str:
    """
    Generate chatbot response using Groq
    
    Args:
        message: User's message
        context: Dict with latest_prediction, metrics, news_sentiment, etc.
        history: List of previous messages [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        AI response string
    """
    # Check if client is available
    if not client:
        return "Chatbot is not available. Please configure GROQ_API_KEY environment variable."
    
    # Build system prompt with context
    system_prompt = f"""You are AlphaSignal Assistant, an AI helper for the AlphaSignal crude oil price prediction system.

Current Data:
- Latest Prediction: ${context.get('latest_prediction', 'N/A')}
- Model Performance: MAE ${context.get('mae', 'N/A')}, MAPE {context.get('mape', 'N/A')}%
- Total Predictions Made: {context.get('total_predictions', 'N/A')}
- News Sentiment: {context.get('news_sentiment', 'Neutral')}

You help users understand:
- Price predictions and trends
- Model performance and accuracy
- Oil market news and sentiment
- How the system works

Be concise, helpful, and professional. If you don't have specific data, say so politely.
"""
    
    # Build messages list
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    if history:
        messages.extend(history[-10:])  # Keep last 10 messages for context
    
    # Add current user message
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,  # Slightly higher for more natural conversation
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error in chat completion: {e}")
        return "I'm having trouble processing your request right now. Please try again."
