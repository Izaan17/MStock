class CustomPrinter:
    # ANSI color codes for terminal output
    _COLORS = {'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m', 'blue': '\033[94m', 'reset': '\033[0m'}

    def __init__(self, use_colors=True):
        self._use_colors = use_colors

    def error(self, message):
        """Print error messages with [-] prefix"""
        prefix = self._format_prefix("[-]", 'red')
        print(f"{prefix} {message}")

    def success(self, message):
        """Print success messages with [+] prefix"""
        prefix = self._format_prefix("[+]", 'green')
        print(f"{prefix} {message}")

    def info(self, message):
        """Print info messages with [*] prefix"""
        prefix = self._format_prefix("[*]", 'blue')
        print(f"{prefix} {message}")

    def warning(self, message):
        """Print warning messages with [!] prefix"""
        prefix = self._format_prefix("[!]", 'yellow')
        print(f"{prefix} {message}")

    def _format_prefix(self, prefix, color):
        if self._use_colors:
            return f"{self._COLORS[color]}{prefix}{self._COLORS['reset']}"
        return prefix


# Example usage
if __name__ == "__main__":
    printer = CustomPrinter()

    printer.error("Failed to connect to database")
    printer.success("File successfully uploaded")
    printer.info("Processing data...")
    printer.warning("Low disk space")
