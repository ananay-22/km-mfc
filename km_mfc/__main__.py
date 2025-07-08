import sys
from rich.console import Console
from rich.panel import Panel


def main():
    """Main function for the km_mfc module."""
    console = Console()

    console.print(Panel(
        "[bold green]Hello from km-mfc![/bold green]\n\n"
        "This is a sample installable Python package.",
        title="Welcome",
        subtitle="Thank you for trying me out!"
    ))

    console.print("\nYou can run this package in two ways after installation:")
    console.print("1. As a module: [cyan]python -m km_mfc[/cyan]")
    console.print("2. As a command-line script: [cyan]km-mfc-cli[/cyan]")


if __name__ == "__main__":
    sys.exit(main())