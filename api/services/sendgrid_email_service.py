"""
SendGrid Email Service using REST API
Handles sending emails using SendGrid REST API directly (no library needed)
"""
import os
import json
import requests
from datetime import datetime

# SendGrid configuration
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'test07work@gmail.com')
SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

print(f"📧 SendGrid Config: API Key={'*****' if SENDGRID_API_KEY else 'None'}, From={SENDER_EMAIL}")


def create_report_email_html(prediction_data: dict, metrics_data: dict = None) -> str:
    """
    Create HTML email template for prediction report
    """
    predicted_price = prediction_data.get('predicted_price', 0)
    date = prediction_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                background-color: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #2563eb;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #2563eb;
                margin: 0;
                font-size: 28px;
            }}
            .prediction-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                margin: 20px 0;
            }}
            .prediction-price {{
                font-size: 48px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .prediction-date {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 20px 0;
            }}
            .metric-card {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #2563eb;
            }}
            .metric-label {{
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-top: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 AlphaSignal Prediction Report</h1>
                <p style="color: #666; margin: 5px 0;">Crude Oil Price Prediction</p>
            </div>
            
            <div class="prediction-box">
                <div class="prediction-date">Prediction for {date}</div>
                <div class="prediction-price">${predicted_price:.2f}</div>
                <div>📈 View Dashboard for trend analysis</div>
            </div>
    """
    
    # Add metrics if available
    if metrics_data:
        mae = metrics_data.get('mae', 0)
        mape = metrics_data.get('mape', 0)
        total_predictions = metrics_data.get('total_predictions', 0)
        
        html += f"""
            <h3 style="color: #333; margin-top: 30px;">📈 Model Performance</h3>
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">Mean Absolute Error</div>
                    <div class="metric-value">${mae:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Mean Absolute % Error</div>
                    <div class="metric-value">{mape:.2f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Predictions</div>
                    <div class="metric-value">{total_predictions}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Model Accuracy</div>
                    <div class="metric-value">{100 - mape:.1f}%</div>
                </div>
            </div>
        """
    
    html += f"""
            <div class="footer">
                <p><strong>AlphaSignal</strong> - AI-Powered Crude Oil Price Prediction</p>
                <p style="font-size: 11px; color: #999;">
                    © {datetime.now().year} AlphaSignal. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def send_email_sendgrid(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send email using SendGrid REST API (no library needed)
    """
    try:
        if not SENDGRID_API_KEY:
            print("❌ SendGrid API key not configured")
            return False
        
        # Prepare email data for SendGrid API
        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": subject
                }
            ],
            "from": {"email": SENDER_EMAIL},
            "content": [
                {
                    "type": "text/html",
                    "value": html_content
                }
            ]
        }
        
        # Send request to SendGrid API
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            SENDGRID_API_URL,
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code == 202:
            print(f"✅ Email sent successfully to {to_email} (Status: {response.status_code})")
            return True
        else:
            print(f"❌ Failed to send email. Status: {response.status_code}, Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False


def send_instant_report(to_email: str, prediction_data: dict, metrics_data: dict = None) -> bool:
    """
    Send instant prediction report email via SendGrid
    """
    subject = f"Your AlphaSignal Prediction Report - {datetime.now().strftime('%B %d, %Y')}"
    html_content = create_report_email_html(prediction_data, metrics_data)
    return send_email_sendgrid(to_email, subject, html_content)


def send_daily_report(to_email: str, prediction_data: dict, metrics_data: dict = None) -> bool:
    """
    Send daily scheduled report email via SendGrid
    """
    subject = f"AlphaSignal Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    html_content = create_report_email_html(prediction_data, metrics_data)
    return send_email_sendgrid(to_email, subject, html_content)
