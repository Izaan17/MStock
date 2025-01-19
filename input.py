from constants import COLORS


class CustomInput:
    def __init__(self, use_colors=True):
        self.use_colors = use_colors

    def prompt(self, message, prefix="[?]", color='purple'):
        """General input prompt with customizable prefix"""
        formatted_prefix = self._format_prefix(prefix, color)
        return input(f"{formatted_prefix} {message}: ")

    def confirm(self, message):
        """Yes/No confirmation prompt"""
        while True:
            response = self.prompt(f"{message} (y/n)", "[?]", 'blue').lower()
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print(self._format_prefix("[-]", 'red') + " Please enter 'y' or 'n'")

    def select(self, message, options):
        """Selection from multiple options"""
        print(self._format_prefix("[?]", 'purple') + f" {message}:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        while True:
            try:
                choice = int(self.prompt("Enter your choice (number)", "[?]", 'purple'))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                print(self._format_prefix("[-]", 'red') + f" Please enter a number between 1 and {len(options)}")
            except ValueError:
                print(self._format_prefix("[-]", 'red') + " Please enter a valid number")

    def _format_prefix(self, prefix, color):
        if self.use_colors:
            return f"{COLORS[color]}{prefix}{COLORS['reset']}"
        return prefix


# Example usage
if __name__ == "__main__":
    input_handler = CustomInput()

    # Basic prompt
    name = input_handler.prompt("Enter your name")
    print(f"Hello, {name}!")

    # Confirmation
    if input_handler.confirm("Do you want to continue"):
        print("Continuing...")
    else:
        print("Operation cancelled")

    # Selection
    options = ["Option A", "Option B", "Option C"]
    choice = input_handler.select("Choose an option", options)
    print(f"You selected: {choice}")
