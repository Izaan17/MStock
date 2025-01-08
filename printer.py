from constants import COLORS

class CustomPrinter:
    # Extended ANSI color codes and styles

    def __init__(self, use_colors=True):
        self._use_colors = use_colors
        self._indent_level = 0
        self._indent_size = 2

    def table(self, headers, rows, min_width=12):
        """Print data in a formatted table"""
        # Calculate column widths
        widths = [max(min_width, len(str(h))) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))

        # Print headers
        header = self._color('bold')
        header += " | ".join(str(h).ljust(w) for h, w in zip(headers, widths))
        header += self._color('reset')
        print(header)

        # Print separator
        print("-" * (sum(widths) + 3 * (len(headers) - 1)))

        # Print rows
        for row in rows:
            print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, widths)))

    def section(self, title, char='='):
        """Print a section header"""
        width = 80
        padding = max(0, (width - len(title) - 2) // 2)
        print(f"\n{char * padding} {self._style(title, 'bold')} {char * padding}\n")

    def progress(self, current, total, prefix='Progress:', suffix='Complete', length=50):
        """Print a progress bar"""
        percent = float(current) * 100 / total
        filled_length = int(length * current // total)
        bar = '█' * filled_length + '-' * (length - filled_length)
        print(f'\r{prefix} |{self._color("cyan")}{bar}{self._color("reset")}| {percent:.1f}% {suffix}', end='\r')
        if current == total:
            print()

    def success(self, message):
        """Print success messages with enhanced formatting"""
        self._print_formatted("✓", message, 'green', 'bold')

    def error(self, message):
        """Print error messages with enhanced formatting"""
        self._print_formatted("✗", message, 'red', 'bold')

    def info(self, message):
        """Print info messages with enhanced formatting"""
        self._print_formatted("ℹ", message, 'blue')

    def warning(self, message):
        """Print warning messages with enhanced formatting"""
        self._print_formatted("⚠", message, 'yellow', 'bold')

    def debug(self, message):
        """Print debug messages with enhanced formatting"""
        self._print_formatted("⚙", message, 'magenta', 'dim')

    def indent(self):
        """Increase indentation level"""
        self._indent_level += 1

    def dedent(self):
        """Decrease indentation level"""
        self._indent_level = max(0, self._indent_level - 1)

    def _print_formatted(self, symbol, message, color, *styles):
        indent = " " * (self._indent_level * self._indent_size)
        styled_text = self._style(f"{symbol} {message}", color, *styles)
        print(f"{indent}{styled_text}")

    def _style(self, text, *styles):
        if not self._use_colors:
            return text
        return ''.join(self._color(s) for s in styles) + text + self._color('reset')

    def _color(self, color):
        return COLORS.get(color, '') if self._use_colors else ''


# Example usage
if __name__ == "__main__":
    printer = CustomPrinter()

    # Section headers
    printer.section("Product Information")

    # Basic status messages
    printer.success("Successfully processed order #12345")
    printer.error("Failed to connect to database")
    printer.info("Processing new order...")
    printer.warning("Low disk space")
    printer.debug("Connection attempt: 3")

    # Indentation example
    printer.info("Order Details:")
    printer.indent()
    printer.info("Customer: John Doe")
    printer.info("Items: 3")
    printer.indent()
    printer.info("1. Product A - $10.99")
    printer.info("2. Product B - $24.99")
    printer.info("3. Product C - $15.99")
    printer.dedent()
    printer.info("Total: $51.97")
    printer.dedent()

    # Table example
    headers = ["ID", "Product", "Price", "Status"]
    rows = [["001", "Product A", "$10.99", "In Stock"], ["002", "Product B", "$24.99", "Low Stock"],
        ["003", "Product C", "$15.99", "Out of Stock"]]
    printer.section("Inventory Status", '-')
    printer.table(headers, rows)

    # Progress bar example
    import time

    print("\nProcessing order...")
    for i in range(21):
        printer.progress(i, 20, "Order Progress:")
        time.sleep(0.1)
