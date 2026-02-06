import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.app.config import settings

async def send_reset_code_email(to_email: str, reset_code: str):
    """Send password reset code via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = "Password Reset Code - Admin Panel"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center;">Password Reset Request</h2>
                <p style="color: #666; font-size: 16px;">You requested a password reset for your admin account.</p>
                
                <div style="background: #f0f0f0; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">Your verification code:</p>
                    <h1 style="margin: 0; color: #2563eb; font-size: 36px; letter-spacing: 5px;">{reset_code}</h1>
                </div>
                
                <p style="color: #666; font-size: 14px;">This code will expire in 15 minutes.</p>
                <p style="color: #999; font-size: 12px; margin-top: 30px;">If you didn't request this reset, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False