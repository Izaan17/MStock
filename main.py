import argparse

from config import (EMAIL_FROM, EMAIL_PASSWORD)
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
    test_message = "This is a test notification from your Macy's Stock Checker application."
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


def main():
    parser = argparse.ArgumentParser()
    printer = CustomPrinter()
    cinput = CustomInput()

    # Positional args
    parser.add_argument('urls', nargs='*', help='The urls of products to monitor.')

    # Monitoring flags
    parser.add_argument('-i', '--interval', type=int, default=DEFAULT_CHECK_INTERVAL_IN_SECONDS,
                        help='Check interval in seconds')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output with detailed product information')
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

        if arguments.email_to:
            email_config = EmailConfig(sender_email=EMAIL_FROM, sender_password=EMAIL_PASSWORD,
                                       recipient_email=arguments.email_to)
            printer.info(f"Email notifications will be sent to {arguments.email_to}")

        if arguments.phone_to:
            sms_config = SMSConfig(to_number=arguments.phone_to)
            printer.info(f"SMS notifications will be sent to {arguments.phone_to}")

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
        checker.check_stock(valid_urls, interval=arguments.interval, verbose=arguments.verbose)
    else:
        printer.error('No URLs provided')
        printer.info('Example usage:')
        printer.info('python main.py "url1" "url2" -i 60 -v --email-to recipient@email.com --phone-to "+1234567890"')
        printer.info('To test notifications: python main.py -t --email-to recipient@email.com --phone-to "+1234567890"')
        quit(1)


if __name__ == "__main__":
    main()
