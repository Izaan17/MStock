import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from constants import MACYS_PRODUCT_URL_PREFIX, DEFAULT_CHECK_INTERVAL_IN_SECONDS
from input import CustomInput
from notifications import EmailConfig, SMSConfig, NotificationService
from printer import CustomPrinter
from stock_checker import StockChecker
from utils import verify_urls


def test_notifications(notification_service, printer):
    """Test email and SMS notifications"""
    if not notification_service:
        printer.error("No notification methods configured")
        return False

    test_subject = "🧪 Test Notification"
    test_message = "This is a test notification from the MStock program."
    success = True

    if notification_service.email_config:
        printer.info("Testing email notification...")
        if notification_service.send_email(test_subject, test_message):
            printer.success("Email test successful!")
        else:
            printer.error("Email test failed")
            success = False

    if notification_service.sms_config:
        printer.info("Testing SMS notification...")
        if notification_service.send_sms(test_message):
            printer.success("SMS test successful!")
        else:
            printer.error("SMS test failed")
            success = False

    return success


def setup_configuration():
    """Initial setup to create .env file with user's email configuration"""
    printer = CustomPrinter()
    env_file = Path('.env')

    # Check if .env already exists
    if env_file.exists():
        printer.info("Configuration file already exists.")
        if not CustomInput().confirm("Would you like to reconfigure email settings?"):
            return True

    printer.section('Email Configuration Setup')
    printer.info("Please enter your email credentials for sending notifications.")

    # Get email configuration from user
    email = input("Enter your email address: ").strip()
    while not email or '@' not in email:
        printer.error("Please enter a valid email address.")
        email = input("Enter your email address: ").strip()

    # For security, use getpass for password input
    import getpass
    password = getpass.getpass("Enter your email password or app-specific password: ").strip()
    while not password:
        printer.error("Password cannot be empty.")
        password = getpass.getpass("Enter your email password or app-specific password: ").strip()

    # Create or update .env file
    env_content = f"""# Email Configuration
EMAIL_FROM="{email}"
EMAIL_PASSWORD="{password}"
"""

    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        os.chmod(env_file, 0o600)  # Set restrictive permissions
        printer.success("Configuration saved successfully!")

        # Add notice about app-specific passwords for common email providers
        printer.info("\nNote: If you're using Gmail or other major email providers,")
        printer.info("you may need to use an app-specific password instead of your regular password.")
        printer.info("Please check your email provider's documentation for more information.")

    except Exception as e:
        printer.error(f"Error saving configuration: {str(e)}")
        return False

    # Reload the environment variables
    load_dotenv()
    return True


def main():
    # Load environment variables at startup
    load_dotenv()

    parser = argparse.ArgumentParser()
    printer = CustomPrinter()
    cinput = CustomInput()

    # Positional args
    parser.add_argument('urls', nargs='*', help='The urls of products to monitor.')

    # Monitoring flags
    parser.add_argument('-i', '--interval', type=int, default=DEFAULT_CHECK_INTERVAL_IN_SECONDS,
                        help='Check interval in seconds')
    parser.add_argument('-t', '--test', action='store_true', help='Test email and SMS notifications')

    # Notification arguments
    notification_group = parser.add_argument_group('Notifications')
    notification_group.add_argument('--email-to', help='Email address to send notifications to')
    notification_group.add_argument('--phone-to', help='Phone number to send SMS notifications to')

    arguments = parser.parse_args()

    # Setup notifications if configured
    notification_service = None
    if any([arguments.email_to, arguments.phone_to]):
        email_config = None
        sms_config = None

        printer.section('Notification Information')

        if arguments.email_to:
            # Check if email configuration exists and run setup if needed
            if not Path('.env').exists() or not os.getenv('EMAIL_FROM') or not os.getenv('EMAIL_PASSWORD'):
                printer.info("Email configuration not found.")
                if not setup_configuration():
                    printer.error("Email setup failed. Email notifications will not be available.")
                else:
                    email_config = EmailConfig(sender_email=os.getenv('EMAIL_FROM'),
                                               sender_password=os.getenv('EMAIL_PASSWORD'),
                                               recipient_email=arguments.email_to)
                    printer.info(f"Email notifications will be sent to {arguments.email_to}")
            else:
                email_config = EmailConfig(sender_email=os.getenv('EMAIL_FROM'),
                                           sender_password=os.getenv('EMAIL_PASSWORD'),
                                           recipient_email=arguments.email_to)
                printer.info(f"Email notifications will be sent to {arguments.email_to}")

        if arguments.phone_to:
            sms_config = SMSConfig(to_number=arguments.phone_to)
            printer.info(f"SMS notifications will be sent to {arguments.phone_to}")

        print()  # Seperator

        notification_service = NotificationService(email_config, sms_config)

    # If test flag is set, run notification test and exit
    if arguments.test:
        printer.info("Running notification test...")
        if test_notifications(notification_service, printer):
            printer.success("All notification tests completed successfully!")
        else:
            printer.error("Some notification tests failed")
        return

    if arguments.urls:
        valid_urls, invalid_urls = verify_urls(arguments.urls)

        if not valid_urls:
            printer.warning('No valid urls were supplied')
            printer.info(f'Please use urls that start with {MACYS_PRODUCT_URL_PREFIX}')
            printer.error('Exiting...')
            quit(1)

        if invalid_urls:
            printer.error('Invalid urls were found:')
            print(*invalid_urls, sep='\n')
            if not cinput.confirm('Would you like to proceed?'):
                quit(1)

        printer.info('Valid urls:')
        print(*valid_urls, sep='\n')

        # Initialize stock checker and start monitoring
        checker = StockChecker(printer=printer, notification_service=notification_service)
        checker.check_stock(valid_urls, interval=arguments.interval)
    else:
        printer.error('No URLs provided')
        printer.info('Example usage:')
        printer.info('python main.py "url1" "url2" -i 60 -v --email-to recipient@email.com --phone-to "+1234567890"')
        printer.info('To test notifications: python main.py -t --email-to recipient@email.com --phone-to "+1234567890"')
        quit(1)


if __name__ == "__main__":
    main()
