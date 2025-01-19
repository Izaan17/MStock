# MStock - Macy's Stock Checker

MStock is a Python-based tool that monitors Macy's product pages for stock availability. When items come back in stock,
it can notify you via email and SMS notifications.

## Features

- **Real-time Stock Monitoring**: Continuously checks Macy's product pages for stock status
- **Multi-Product Support**: Monitor multiple products simultaneously
- **Smart Caching**: Retains product information to provide details even when website scraping fails
- **Detailed Product Information**: Displays comprehensive product details including:
    - Product name and brand
    - Price
    - Ratings and reviews
    - Stock status
- **Flexible Notifications**:
    - Email notifications
    - SMS notifications (using iMessage)
    - Customizable check intervals

## Prerequisites

- Python 3.8 or higher
- macOS (for SMS notifications using iMessage)
- Gmail account (for sending email notifications)

## Installation

1. Clone the repository:

```shell
git clone https://github.com/Izaan17/MStock.git
cd mstock
```

2. Install required packages:

```shell
pip install -r requirements.txt
```

3. Set up email notifications:
    - For Gmail:
        1. Enable 2-factor authentication
        2. Generate an app-specific password
        3. Use this password in the configuration

## Configuration

When running the tool for the first time with email notifications, it will prompt you to enter your email credentials.
These will be saved in a `.env` file.

For email configuration, you'll need:

- Your Gmail address
- App-specific password (not your regular Gmail password)

## Usage

Basic usage:

```shell
python main.py "https://www.macys.com/shop/product/your-product-url"
```

Multiple products:

```shell
python main.py "url1" "url2" "url3"
```

### Command Line Options

- `-i, --interval`: Check interval in seconds (default: 60)
- `--email-to`: Email address to receive notifications
- `--phone-to`: Phone number to receive SMS notifications
- `-t, --test`: Test notification settings

### Testing Notifications

Before starting long-term monitoring, it's recommended to test your notification settings. Use the `-t` or `--test`
argument to send test notifications:

```shell
# Test both email and SMS notifications
python main.py -t --email-to your@email.com --phone-to "+1234567890"

# Test email notifications only
python main.py -t --email-to your@email.com

# Test SMS notifications only
python main.py -t --phone-to "+1234567890"
```

The test will:

1. Send a test email with subject "🧪 Test Notification"
2. Send a test SMS message
3. Report success or failure for each notification method
4. Exit after testing

Example test output:

```
===== Notification Test =====
Testing email notification...
✓ Email test successful!
Testing SMS notification...
✓ SMS test successful!
All notification tests completed successfully!
```

If any test fails, you'll see detailed error messages to help troubleshoot the issue.

### Examples

Monitor a single product with email notifications:

```shell
python main.py "https://www.macys.com/shop/product/your-product-url" --email-to your@email.com
```

Monitor multiple products with both email and SMS notifications:

```shell
python main.py "url1" "url2" --email-to your@email.com --phone-to "+1234567890" -i 120
```

Test notifications setup:

```shell
python main.py -t --email-to your@email.com --phone-to "+1234567890"
```

## Features in Detail

### Smart Caching

The tool implements a caching system that:

- Stores product information when successfully retrieved
- Uses cached information if current retrieval fails
- Indicates in notifications when cached information is being used
- Ensures continuous monitoring even during temporary website issues

### Notification Format

Email notifications include:

- Product name and brand (when available)
- Current price
- Product rating and reviews
- Direct link to the product
- Indication if using cached information

### Status Display

The tool provides:

- Real-time status updates in the console
- Detailed product information
- Current monitoring status
- Summary tables of all monitored products

## Error Handling

The tool handles various scenarios gracefully:

- Network connectivity issues
- Website structure changes
- Missing product information
- Invalid URLs
- Notification delivery failures

### Common Issues and Solutions

1. Email Notification Issues:
    - Verify your Gmail app-specific password is correct
    - Check if 2-factor authentication is enabled
    - Ensure the recipient email address is valid
    - Check your spam folder for test notifications

2. SMS Notification Issues:
    - You must have an icloud account logged in the computer using the script
    - Ensure you're running on macOS for iMessage support
    - Verify the phone number format (should include country code)
    - Sometimes messages will fail to send if the iMessage app is not open
    - Check Messages.app is properly configured

3. If Test Notifications Fail:
    - Run with `-t` flag to isolate notification issues
    - Check console output for specific error messages
    - Verify your internet connection
    - Ensure all credentials in .env file are correct

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.