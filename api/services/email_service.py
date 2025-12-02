"""
Email Service
Handles sending emails with prediction reports
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration from environment
# Support both old and new variable names for compatibility
EMAIL_HOST = os.getenv('SMTP_SERVER') or os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('SMTP_PORT') or os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('SENDER_EMAIL') or os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('SENDER_PASSWORD') or os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM', f'AlphaSignal <{EMAIL_USER}>')


def create_report_email_html(prediction_data: dict, metrics_data: dict = None) -> str:
    """
    Create HTML email template for prediction report
    
    Args:
        prediction_data: Latest prediction data
        metrics_data: Model performance metrics (optional)
    
    Returns:
        HTML string for email body
    """
    predicted_price = prediction_data.get('predicted_price', 0)
    date = prediction_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Calculate trend (if previous price available)
    trend_emoji = "📈"
    trend_text = "View Dashboard for trend analysis"
    
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
            .cta-button {{
                display: inline-block;
                background-color: #2563eb;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #666;
            }}
            .emoji {{
                font-size: 24px;
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
                <div>{trend_emoji} {trend_text}</div>
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
            <div style="text-align: center;">
                <a href="http://localhost:3000/dashboard" class="cta-button">
                    View Full Dashboard →
                </a>
            </div>
            
            <div class="footer">
                <p><strong>AlphaSignal</strong> - AI-Powered Crude Oil Price Prediction</p>
                <p style="margin: 10px 0;">
                    This is an automated report. 
                    <a href="http://localhost:3000" style="color: #2563eb;">Visit Dashboard</a>
                </p>
                <p style="font-size: 11px; color: #999;">
                    © {datetime.now().year} AlphaSignal. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart('alternative')
        message['From'] = EMAIL_FROM
        message['To'] = to_email
        message['Subject'] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Connect to SMTP server
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False


def send_instant_report(to_email: str, prediction_data: dict, metrics_data: dict = None) -> bool:
    """
    Send instant prediction report email
    
    Args:
        to_email: Recipient email
        prediction_data: Latest prediction data
        metrics_data: Model metrics (optional)
    
    Returns:
        True if sent successfully
    """
    subject = f"Your AlphaSignal Prediction Report - {datetime.now().strftime('%B %d, %Y')}"
    html_content = create_report_email_html(prediction_data, metrics_data)
    return send_email(to_email, subject, html_content)


def send_daily_report(to_email: str, prediction_data: dict, metrics_data: dict = None) -> bool:
    """
    Send daily scheduled report email
    
    Args:
        to_email: Recipient email
        prediction_data: Latest prediction data
        metrics_data: Model metrics (optional)
    
    Returns:
        True if sent successfully
    """
    subject = f"AlphaSignal Daily Report - {datetime.now().strftime('%B %d, %Y')}"
    html_content = create_report_email_html(prediction_data, metrics_data)
    return send_email(to_email, subject, html_content)


if __name__ == "__main__":
    # Test email sending
    test_prediction = {
        'predicted_price': 75.50,
        'date': '2025-12-02'
    }
    
    test_metrics = {
        'mae': 6.27,
        'mape': 8.55,
        'total_predictions': 150
    }
    
    test_email = "test@example.com"  # Replace with your email for testing
    
    print("Testing email service...")
    success = send_instant_report(test_email, test_prediction, test_metrics)
    
    if success:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Test email failed. Check your .env configuration.")
