"""
Email Notification Module
Sends daily reports via email
"""
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

load_dotenv()

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")  
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")


def send_email_report(report_path, subject=None, recipients=None):
    """
    Send daily report via email
    
    Args:
        report_path: Path to the markdown report file
        subject: Email subject (optional)
        recipients: List of recipient emails (optional, uses env var if not provided)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    # Validate configuration
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(" Email not configured. Please set SENDER_EMAIL and SENDER_PASSWORD in .env")
        return False
    
    # Use environment variable if recipients not provided
    if recipients is None:
        if not RECIPIENT_EMAIL:
            print(" No recipients specified. Set RECIPIENT_EMAIL in .env")
            return False
        recipients = [RECIPIENT_EMAIL]
    
    # Read report content
    if not Path(report_path).exists():
        print(f" Report file not found: {report_path}")
        return False
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # Create email
    msg = MIMEMultipart('alternative')
    
    # Set subject
    if subject is None:
        subject = f"AlphaSignal Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = ', '.join(recipients)
    
    # Convert markdown to HTML (basic conversion)
    html_content = markdown_to_html(report_content)
    
    # Attach both plain text and HTML versions
    part1 = MIMEText(report_content, 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')
    
    msg.attach(part1)
    msg.attach(part2)
    
    # Optionally attach the markdown file
    attachment = MIMEBase('application', 'octet-stream')
    with open(report_path, 'rb') as f:
        attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header(
        'Content-Disposition',
        f'attachment; filename={Path(report_path).name}'
    )
    msg.attach(attachment)
    
    # Send email
    try:
        print(f"\n Sending email to {', '.join(recipients)}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print(f" Email sent successfully!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(" Authentication failed. Check your email and password.")
        print("   For Gmail, use an App Password: https://support.google.com/accounts/answer/185833")
        return False
    except Exception as e:
        print(f" Failed to send email: {e}")
        return False


def markdown_to_html(markdown_text):
    """
    Convert markdown to basic HTML
    (Simple conversion - for better results, use markdown library)
    """
    html = markdown_text
    
    # Headers
    html = html.replace('# ', '<h1>').replace('\n\n', '</h1>\n\n')
    html = html.replace('## ', '<h2>').replace('\n\n', '</h2>\n\n')
    html = html.replace('### ', '<h3>').replace('\n\n', '</h3>\n\n')
    
    # Bold
    import re
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Lists
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # Tables (basic)
    lines = html.split('\n')
    in_table = False
    result = []
    
    for line in lines:
        if '|' in line and not line.strip().startswith('|---'):
            if not in_table:
                result.append('<table border="1" cellpadding="5" cellspacing="0">')
                in_table = True
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            result.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>')
        elif line.strip().startswith('|---'):
            continue
        else:
            if in_table:
                result.append('</table>')
                in_table = False
            result.append(line)
    
    if in_table:
        result.append('</table>')
    
    html = '\n'.join(result)
    
    # Wrap in HTML structure
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            td {{ padding: 8px; border: 1px solid #ddd; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .emoji {{ font-size: 1.2em; }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    
    return html


def test_email_config():
    """Test email configuration"""
    print("=" * 60)
    print("Email Configuration Test")
    print("=" * 60)
    
    print(f"\nSMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"Sender: {SENDER_EMAIL if SENDER_EMAIL else ' Not configured'}")
    print(f"Password: {' Set' if SENDER_PASSWORD else ' Not set'}")
    print(f"Recipient: {RECIPIENT_EMAIL if RECIPIENT_EMAIL else ' Not configured'}")
    
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        print("\n  Email not fully configured. Add to .env:")
        print("   SENDER_EMAIL=your_email@gmail.com")
        print("   SENDER_PASSWORD=your_app_password")
        print("   RECIPIENT_EMAIL=recipient@example.com")
        print("\n For Gmail App Password: https://support.google.com/accounts/answer/185833")
        return False
    
    return True


if __name__ == "__main__":
    # Test configuration
    if test_email_config():
        print("\n Email configuration looks good!")
        print("\nTo send a report, use:")
        print("  from src.reporting.email_notifier import send_email_report")
        print("  send_email_report('reports/daily_report_20251129.md')")
