"""
Email Router
Endpoints for sending prediction reports and managing subscriptions
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pathlib import Path
import pandas as pd
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.sendgrid_email_service import send_instant_report, send_daily_report

router = APIRouter()

# Path to subscribers CSV
SUBSCRIBERS_FILE = Path(__file__).parent.parent / "services" / "subscribers.csv"


class EmailRequest(BaseModel):
    email: EmailStr


class EmailResponse(BaseModel):
    success: bool
    message: str

GCS_SUBSCRIBERS_PATH = "data/subscribers/subscribers.csv"


def load_subscribers() -> pd.DataFrame:
    """Load subscribers from GCS for persistence"""
    from services.gcs_data_loader import read_csv_from_gcs
    
    df = read_csv_from_gcs(GCS_SUBSCRIBERS_PATH)
    if df is None or df.empty:
        return pd.DataFrame(columns=['email', 'subscribed_date', 'is_active', 'last_sent'])
    return df


def save_subscribers(df: pd.DataFrame):
    """Save subscribers to GCS for persistence"""
    from google.cloud import storage
    import io
    
    try:
        client = storage.Client()
        bucket = client.bucket("alphasignal-models")
        blob = bucket.blob(GCS_SUBSCRIBERS_PATH)
        
        # Convert DataFrame to CSV string
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        # Upload to GCS
        blob.upload_from_string(csv_buffer.getvalue(), content_type='text/csv')
        print(f"Subscribers saved to GCS: {len(df)} records")
    except Exception as e:
        print(f"Error saving subscribers to GCS: {e}")
        # Fallback to local file
        df.to_csv(SUBSCRIBERS_FILE, index=False)


def is_subscribed(email: str) -> bool:
    """Check if email is already subscribed"""
    df = load_subscribers()
    if df.empty:
        return False
    return ((df['email'] == email) & (df['is_active'] == True)).any()


@router.post("/send-report", response_model=EmailResponse)
async def send_report_now(request: EmailRequest):
    """
    Send instant prediction report to email
    Stores email in database for record keeping
    """
    try:
        # Load latest prediction from GCS
        from services.gcs_data_loader import read_csv_from_gcs
        
        df = read_csv_from_gcs("data/prediction/prediction_log.csv")
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No predictions available")
        
        latest = df.iloc[-1]
        prediction_data = {
            'predicted_price': float(latest['predicted']),
            'date': str(latest['date'])
        }
        
        # Load metrics (optional)
        metrics_data = None
        try:
            from routers.metrics import get_model_metrics
            metrics_response = await get_model_metrics()
            metrics_data = {
                'mae': metrics_response.get('mae', 0),
                'mape': metrics_response.get('mape', 0),
                'total_predictions': metrics_response.get('total_predictions', 0)
            }
        except:
            pass
        
        # Send email via SendGrid
        success = send_instant_report(request.email, prediction_data, metrics_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send email")
        
        # Store email in CSV for record keeping (even if not subscribed)
        try:
            subscribers_df = load_subscribers()
            
            # Check if email already exists
            if subscribers_df.empty or not (subscribers_df['email'] == request.email).any():
                # Add new email with is_active=False (not subscribed, just received instant report)
                new_entry = pd.DataFrame([{
                    'email': request.email,
                    'subscribed_date': datetime.now().strftime('%Y-%m-%d'),
                    'is_active': False,  # Not subscribed to daily reports
                    'last_sent': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }])
                subscribers_df = pd.concat([subscribers_df, new_entry], ignore_index=True)
            else:
                # Update last_sent timestamp
                subscribers_df.loc[subscribers_df['email'] == request.email, 'last_sent'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            save_subscribers(subscribers_df)
        except Exception as e:
            # Don't fail the request if storage fails, just log it
            print(f"Warning: Failed to store email in database: {str(e)}")
        
        return EmailResponse(
            success=True,
            message=f"Report sent successfully to {request.email}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending report: {str(e)}")


@router.post("/subscribe", response_model=EmailResponse)
async def subscribe_to_daily_reports(request: EmailRequest):
    """
    Subscribe email to daily prediction reports
    """
    try:
        df = load_subscribers()
        
        # Check if already subscribed
        if is_subscribed(request.email):
            return EmailResponse(
                success=True,
                message=f"{request.email} is already subscribed to daily reports"
            )
        
        # Check if email exists but is inactive
        if not df.empty and (df['email'] == request.email).any():
            # Reactivate subscription
            df.loc[df['email'] == request.email, 'is_active'] = True
            df.loc[df['email'] == request.email, 'subscribed_date'] = datetime.now().strftime('%Y-%m-%d')
        else:
            # Add new subscriber
            new_subscriber = pd.DataFrame([{
                'email': request.email,
                'subscribed_date': datetime.now().strftime('%Y-%m-%d'),
                'is_active': True,
                'last_sent': ''
            }])
            df = pd.concat([df, new_subscriber], ignore_index=True)
        
        save_subscribers(df)
        
        return EmailResponse(
            success=True,
            message=f"Successfully subscribed {request.email} to daily reports"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subscribing: {str(e)}")


@router.post("/unsubscribe", response_model=EmailResponse)
async def unsubscribe_from_daily_reports(request: EmailRequest):
    """
    Unsubscribe email from daily reports
    """
    try:
        df = load_subscribers()
        
        if df.empty or not (df['email'] == request.email).any():
            raise HTTPException(status_code=404, detail="Email not found in subscribers")
        
        # Set is_active to False
        df.loc[df['email'] == request.email, 'is_active'] = False
        save_subscribers(df)
        
        return EmailResponse(
            success=True,
            message=f"Successfully unsubscribed {request.email} from daily reports"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unsubscribing: {str(e)}")


@router.get("/subscribers")
async def get_subscribers():
    """Get list of active subscribers (admin endpoint)"""
    try:
        df = load_subscribers()
        
        if df.empty:
            return {
                "total_subscribers": 0,
                "active_subscribers": 0,
                "subscribers": []
            }
        
        active_df = df[df['is_active'] == True]
        
        return {
            "total_subscribers": len(df),
            "active_subscribers": len(active_df),
            "subscribers": active_df.to_dict(orient='records')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading subscribers: {str(e)}")
