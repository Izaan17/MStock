import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
import mac_imessage

@dataclass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""  # App password for Gmail
    recipient_email: str = ""

@dataclass
class SMSConfig:
    to_number: str = ""    # Your phone number

class NotificationService:
    def __init__(self, email_config: EmailConfig = None, sms_config: SMSConfig = None):
        self.email_config = email_config
        self.sms_config = sms_config

    def send_email(self, subject: str, body: str):
        """Send email notification"""
        if not self.email_config:
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config.sender_email
            msg['To'] = self.email_config.recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.email_config.smtp_server, self.email_config.smtp_port)
            server.starttls()
            server.login(self.email_config.sender_email, self.email_config.sender_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def send_sms(self, message: str):
        """Send SMS notification"""
        if not self.sms_config:
            return

        try:
            message = mac_imessage.send_imessage(
                message=message,
                phone_number=self.sms_config.to_number
            )
            return True
        except Exception as e:
            print(f"Failed to send SMS: {str(e)}")
            return False