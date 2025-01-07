from bs4 import BeautifulSoup
import requests
import time
from dataclasses import dataclass
from typing import Optional
from printer import CustomPrinter

@dataclass
class ProductInfo:
    """Class to store product information"""
    id: str
    name: str
    brand: str
    price: Optional[str] = None
    status: str = "Unknown"
    description: Optional[str] = None
    reviews_count: Optional[str] = None
    rating: Optional[str] = None

class StockChecker:
    def __init__(self, printer=None, notification_service=None):
        self.printer = printer or CustomPrinter()
        self.notification_service = notification_service
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def notify_in_stock(self, url, product_info=None):
        """Send notifications when item comes in stock"""
        if not self.notification_service:
            return

        product_name = product_info.name if product_info else "Item"
        subject = f"🛍️ In Stock Alert: {product_name}"
        message = f"Item is now in stock!\n\nProduct: {product_name}\nURL: {url}"

        if self.notification_service:
            self.notification_service.send_email(subject, message)
            self.notification_service.send_sms(message)

    def check_stock(self, urls, interval=60, verbose=False):
        """Continuously check stock for multiple URLs until all items are in stock"""
        out_of_stock_urls = set(urls)
        check_count = 1

        while out_of_stock_urls:
            self.printer.info(f"Check #{check_count} - Checking {len(out_of_stock_urls)} items...")

            newly_in_stock = set()
            for idx, url in enumerate(out_of_stock_urls, 1):
                self.printer.info(f"Checking item {idx}/{len(out_of_stock_urls)}:")
                status, product_info = self.check_macys_stock(url, verbose)

                if verbose and product_info:
                    self.print_product_info(product_info, idx, len(out_of_stock_urls))

                if status is True:
                    self.printer.success(f"Item {idx}/{len(out_of_stock_urls)} - IN STOCK: {url}")
                    self.notify_in_stock(url, product_info)
                    newly_in_stock.add(url)
                elif status is False:
                    self.printer.error(f"Item {idx}/{len(out_of_stock_urls)} - Out of stock: {url}")
                else:
                    self.printer.warning(f"Item {idx}/{len(out_of_stock_urls)} - Unable to determine stock status: {url}")

                print() # Cleaner formatting

                time.sleep(2)

            out_of_stock_urls -= newly_in_stock

            if out_of_stock_urls:
                self.printer.info(f"Waiting {interval} seconds before next check...")
                time.sleep(interval)
            else:
                self.printer.success("All items are now in stock!")

            check_count += 1

    def print_product_info(self, product: ProductInfo, item_num: int, total_items: int):
        """Print detailed product information with item number"""
        self.printer.info(f"Product Information (Item {item_num}/{total_items}):")
        self.printer.info(f"  ID: {product.id}")
        self.printer.info(f"  Brand: {product.brand}")
        self.printer.info(f"  Name: {product.name}")
        if product.price:
            self.printer.info(f"  Price: {product.price}")
        self.printer.info(f"  Status: {product.status}")
        if product.description:
            self.printer.info(f"  Description: {product.description}")
        if product.rating:
            self.printer.info(f"  Rating: {product.rating}")
        if product.reviews_count:
            self.printer.info(f"  Reviews: {product.reviews_count}")

    def check_macys_stock(self, url, verbose=False):
        """Check stock status for a single Macy's URL"""
        try:
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Initialize product info
            product_info = None
            if verbose:
                product_info = self.extract_product_info(soup)

            # Check for the specific out of stock error message
            out_of_stock_div = soup.find('div', {'class': ['error-color', 'large']})
            if out_of_stock_div and "sorry, this item is currently unavailable" in out_of_stock_div.text.lower():
                if product_info:
                    product_info.status = "Out of Stock"
                return False, product_info

            # If we don't find the out of stock message, check for add to bag button
            add_to_bag = soup.find('button', {'data-auto-id': 'add-to-bag'})
            if add_to_bag and not add_to_bag.get('disabled'):
                if product_info:
                    product_info.status = "In Stock"
                return True, product_info

            if product_info:
                product_info.status = "Unknown"
            return None, product_info

        except requests.RequestException as e:
            self.printer.error(f"Error checking stock: {e}")
            return None, None

    def extract_product_info(self, soup) -> ProductInfo:
        """Extract product information from the page"""
        try:
            # Extract product ID
            product_id = ""
            web_id_span = soup.find('span', class_='product-id')
            if web_id_span:
                product_id = web_id_span.text.replace('Web ID:', '').strip()

            # Extract brand and name
            brand = ""
            name = ""
            title_elem = soup.find('h1', class_='product-title')
            if title_elem:
                brand_elem = title_elem.find('label', class_='subtitle-2')
                if brand_elem:
                    brand = brand_elem.text.strip()
                name_elem = title_elem.find('span', class_='subtitle-1')
                if name_elem:
                    name = name_elem.text.strip()

            # Extract description
            description = ""
            desc_elem = soup.find('div', class_='long-description')
            if desc_elem:
                description = desc_elem.text.strip()

            # Extract rating information
            rating = None
            reviews_count = None
            rating_elem = soup.find('span', class_='rating-average')
            if rating_elem:
                rating = rating_elem.text.strip()
            reviews_elem = soup.find('span', class_='rating-description')
            if reviews_elem:
                reviews_count = reviews_elem.text.strip()

            return ProductInfo(
                id=product_id,
                brand=brand,
                name=name,
                description=description,
                rating=rating,
                reviews_count=reviews_count
            )

        except Exception as e:
            self.printer.error(f"Error extracting product info: {e}")
            return ProductInfo(id="unknown", name="unknown", brand="unknown", status="Error")