"""
Test Email Configuration
Run this to verify your Gmail SMTP settings
"""
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# Load email configuration - support both old and new variable names
EMAIL_HOST = os.getenv('SMTP_SERVER') or os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('SMTP_PORT') or os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('SENDER_EMAIL') or os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('SENDER_PASSWORD') or os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM', f'AlphaSignal <{EMAIL_USER}>')

print("=" * 50)
print("EMAIL CONFIGURATION TEST")
print("=" * 50)
print(f"EMAIL_HOST: {EMAIL_HOST}")
print(f"EMAIL_PORT: {EMAIL_PORT}")
print(f"EMAIL_USER: {EMAIL_USER}")
print(f"EMAIL_PASSWORD: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'NOT SET'}")
print(f"EMAIL_FROM: {EMAIL_FROM}")
print("=" * 50)

# Check if all required fields are set
if not EMAIL_USER:
    print("❌ ERROR: EMAIL_USER is not set in .env file")
    exit(1)

if not EMAIL_PASSWORD:
    print("❌ ERROR: EMAIL_PASSWORD is not set in .env file")
    exit(1)

# Try to connect and send a test email
print("\n🔄 Testing SMTP connection...")

try:
    # Create a test message
    message = MIMEMultipart('alternative')
    message['From'] = EMAIL_FROM
    message['To'] = EMAIL_USER  # Send to yourself
    message['Subject'] = "AlphaSignal Email Test"
    
    html = """
    <html>
        <body>
            <h2>✅ Email Configuration Test Successful!</h2>
            <p>Your AlphaSignal email notification system is working correctly.</p>
            <p>You can now send prediction reports via email.</p>
        </body>
    </html>
    """
    
    html_part = MIMEText(html, 'html')
    message.attach(html_part)
    
    # Connect to SMTP server
    print(f"📡 Connecting to {EMAIL_HOST}:{EMAIL_PORT}...")
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10) as server:
        print("✅ Connected to SMTP server")
        
        print("🔒 Starting TLS encryption...")
        server.starttls()
        print("✅ TLS encryption enabled")
        
        print(f"🔑 Logging in as {EMAIL_USER}...")
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        print("✅ Login successful")
        
        print(f"📧 Sending test email to {EMAIL_USER}...")
        server.send_message(message)
        print("✅ Test email sent successfully!")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)
    print(f"\nCheck your inbox at {EMAIL_USER} for the test email.")
    print("If you don't see it, check your spam folder.")
    
except smtplib.SMTPAuthenticationError as e:
    print("\n❌ AUTHENTICATION ERROR")
    print("=" * 50)
    print("Your email/password is incorrect or you need to:")
    print("1. Enable 2-Factor Authentication on your Gmail account")
    print("2. Generate an App Password:")
    print("   - Go to: https://myaccount.google.com/apppasswords")
    print("   - Create a new app password for 'AlphaSignal'")
    print("   - Copy the 16-character password")
    print("   - Update EMAIL_PASSWORD in your .env file")
    print(f"\nError details: {str(e)}")
    
except smtplib.SMTPException as e:
    print("\n❌ SMTP ERROR")
    print("=" * 50)
    print(f"Error: {str(e)}")
    
except Exception as e:
    print("\n❌ UNEXPECTED ERROR")
    print("=" * 50)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
