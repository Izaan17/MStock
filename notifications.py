import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from dataclasses import dataclass

@dataclass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""  # App password for Gmail
    recipient_email: str = ""

@dataclass
class SMSConfig:
    account_sid: str = ""
    auth_token: str = ""
    from_number: str = ""  # Your Twilio phone number
    to_number: str = ""    # Your phone number

class NotificationService:
    def __init__(self, email_config: EmailConfig = None, sms_config: SMSConfig = None):
        self.email_config = email_config
        self.sms_config = sms_config
        self.twilio_client = None
        if sms_config:
            self.twilio_client = Client(sms_config.account_sid, sms_config.auth_token)

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
        if not self.sms_config or not self.twilio_client:
            return

        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.sms_config.from_number,
                to=self.sms_config.to_number
            )
            return True
        except Exception as e:
            print(f"Failed to send SMS: {str(e)}")
            return False