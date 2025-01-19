import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, List

import requests
from bs4 import BeautifulSoup

from notifications import NotificationService
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
    last_checked: Optional[datetime] = None


class StockChecker:
    def __init__(self, printer: CustomPrinter = None, notification_service: NotificationService = None):
        self.printer = printer
        self.notification_service = notification_service
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9', }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.product_history = {}  # Cache for product information

    def get_cached_product_info(self, url: str) -> Optional[ProductInfo]:
        """Get cached product information if available"""
        return self.product_history.get(url)

    def cache_product_info(self, url: str, product_info: ProductInfo):
        """Cache product information for future use"""
        self.product_history[url] = product_info

    def notify_in_stock(self, url, current_product_info=None):
        """Send notifications when item comes in stock"""
        if not self.notification_service:
            return

        # Try to get product info from cache if current info is not available
        product_info = current_product_info or self.get_cached_product_info(url)

        if product_info and product_info.name and product_info.brand:
            subject = f"🛍️ In Stock Alert: {product_info.name}"
            message_parts = ["🎉 Item is now in stock! 🎉\n", f"Product: {product_info.name}",
                f"Brand: {product_info.brand}"]

            if product_info.price:
                message_parts.append(f"Price: {product_info.price}")
            if product_info.rating:
                message_parts.append(f"Rating: {product_info.rating}")
            if product_info.reviews_count:
                message_parts.append(f"Reviews: {product_info.reviews_count}")

            if current_product_info is None:
                message_parts.append("\n⚠️ Note: Using cached product information")
        else:
            subject = "🛍️ In Stock Alert"
            message_parts = ["🎉 Item is now in stock! 🎉\n", "⚠️ Unable to retrieve product information"]

        message_parts.append(f"\nShop now: {url}")
        message = "\n".join(message_parts)

        self.notification_service.send_email(subject, message)
        self.notification_service.send_sms(message)

    def print_status_summary(self, products: List[Tuple[str, ProductInfo]]):
        """Print a summary table of current product status"""
        headers = ["ID", "Brand", "Product", "Status", "Price", "Last Checked"]
        rows = []

        for url, info in products:
            last_checked = info.last_checked.strftime("%H:%M:%S") if info.last_checked else "Never"
            rows.append([info.id[:8] + "..." if len(info.id) > 8 else info.id,
                info.brand[:15] + "..." if len(info.brand) > 15 else info.brand,
                info.name[:20] + "..." if len(info.name) > 20 else info.name, info.status, info.price or "N/A",
                last_checked])

        self.printer.table(headers, rows)

    def check_stock(self, urls, interval=60):
        """Continuously check stock for multiple URLs"""
        self.printer.section("Stock Checker Started")
        self.printer.info(f"Monitoring {len(urls)} products")
        self.printer.info(f"Check interval: {interval} seconds")
        print()

        out_of_stock_urls = set(urls)
        check_count = 1

        while out_of_stock_urls:
            self.printer.section(f"Check #{check_count}", "-")
            self.printer.info(f"Checking {len(out_of_stock_urls)} items...")
            print()

            current_products = []
            newly_in_stock = set()

            for idx, url in enumerate(out_of_stock_urls, 1):
                self.printer.info(f"Checking item {idx}/{len(out_of_stock_urls)}...")
                status, product_info = self.check_macys_stock(url)

                # Get cached info if current info is not available
                if not product_info:
                    product_info = self.get_cached_product_info(url)
                    if product_info:
                        self.printer.info("Using cached product information")
                else:
                    # Cache new product info
                    self.cache_product_info(url, product_info)

                if product_info:
                    product_info.last_checked = datetime.now()
                    current_products.append((url, product_info))

                self.printer.indent()
                if status is True:
                    self.printer.success(f"Item {idx}/{len(out_of_stock_urls)} - IN STOCK")
                    self.notify_in_stock(url, product_info)
                    newly_in_stock.add(url)
                elif status is False:
                    self.printer.error(f"Item {idx}/{len(out_of_stock_urls)} - Out of stock")
                else:
                    self.printer.warning(f"Item {idx}/{len(out_of_stock_urls)} - Status unknown")
                self.printer.dedent()

                if product_info:
                    self.print_product_info(product_info)
                time.sleep(2)

            print()
            if current_products:
                self.printer.info("Current Status Summary:")
                self.print_status_summary(current_products)
                print()

            out_of_stock_urls -= newly_in_stock

            if out_of_stock_urls:
                self.printer.info(f"Next check in {interval:.0f} seconds...")
                time.sleep(interval)
            else:
                self.printer.section("Monitoring Complete")
                self.printer.success("All items are now in stock!")

            check_count += 1

    def print_product_info(self, product: ProductInfo):
        """Print detailed product information"""
        self.printer.indent()
        self.printer.info("Product Details:")
        self.printer.indent()
        self.printer.info(f"ID: {product.id}")
        self.printer.info(f"Brand: {product.brand}")
        self.printer.info(f"Name: {product.name}")
        if product.price:
            self.printer.info(f"Price: {product.price}")
        self.printer.info(f"Status: {product.status}")
        if product.rating:
            self.printer.info(f"Rating: {product.rating}")
        if product.reviews_count:
            self.printer.info(f"Reviews: {product.reviews_count}")
        if product.description:
            self.printer.info("Description:")
            self.printer.indent()
            self.printer.info(product.description)
            self.printer.dedent()
        self.printer.dedent()
        self.printer.dedent()

    def check_macys_stock(self, url):
        """Check stock status for a single Macy's URL"""
        try:
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            product_info = self.extract_product_info(soup)

            # Check for out of stock message
            out_of_stock_div = soup.find('div', {'class': ['error-color', 'large']})
            if out_of_stock_div and "sorry, this item is currently unavailable" in out_of_stock_div.text.lower():
                if product_info:
                    product_info.status = "Out of Stock"
                return False, product_info
            else:
                if product_info:
                    product_info.status = "In Stock"
                return True, product_info

        except requests.RequestException as e:
            self.printer.error(f"Error checking stock: {e}")
            return None, None

    def extract_product_info(self, soup) -> Optional[ProductInfo]:
        """Extract product information from the page"""
        try:
            # Extract product ID
            product_id = ""
            web_id_span = soup.find('span', class_='product-id')
            if web_id_span:
                product_id = web_id_span.text.replace('Web ID:', '').strip()

            # Extract price
            price = None
            price_elem = soup.find('div', class_='price')
            if price_elem:
                price = price_elem.text.strip()

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

            # Extract rating information
            rating = None
            reviews_count = None
            rating_elem = soup.find('span', class_='rating-average')
            if rating_elem:
                rating = rating_elem.text.strip()
            reviews_elem = soup.find('span', class_='rating-description')
            if reviews_elem:
                reviews_count = reviews_elem.text.strip()

            return ProductInfo(id=product_id, brand=brand, name=name, price=price, rating=rating,
                reviews_count=reviews_count, last_checked=datetime.now())

        except Exception as e:
            self.printer.error(f"Error extracting product info: {e}")
            return None
