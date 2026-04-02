from rich.console import Console
from ragy_ui.constants import ASCII_LOGO, SUBTITLE
from ragy_cli.handlers import (
    handle_search,
    handle_extract,
    handle_create,
    handle_show_db,
    handle_show_emb,
)

console = Console()

COMMANDS = {
    "search": "Search the web with Tavily",
    "extract": "Extract data from database",
    "create": "Create a new index",
    "show-db": "Show database content",
    "show-emb": "Show embedding info",
    "help": "Show this help menu",
    "exit": "Exit the CLI",
}


def print_header():
    """Print ASCII logo and subtitle"""
    console.print(ASCII_LOGO)
    console.print(SUBTITLE)
    console.print()


def print_help():
    """Print two-column command table"""
    console.print("[bold]Available Commands:[/bold]")
    console.print("-" * 60)

    cmd_width = max(len(cmd) for cmd in COMMANDS.keys()) + 2

    for cmd, desc in COMMANDS.items():
        console.print(f"  [cyan]{cmd:<{cmd_width}}[/cyan] {desc}")

    console.print("-" * 60)
    console.print()


def main():
    """Main CLI entry point"""
    print_header()
    print_help()

    while True:
        try:
            user_input = input("ragy> ").strip().lower()

            if not user_input:
                continue

            if user_input in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if user_input == "help":
                print_help()
                continue

            if user_input == "search":
                handle_search()
            elif user_input == "extract":
                handle_extract()
            elif user_input == "create":
                handle_create()
            elif user_input == "show-db":
                handle_show_db()
            elif user_input == "show-emb":
                handle_show_emb()
            else:
                console.print(f"[red]Unknown command: {user_input}[/red]")
                console.print("Type 'help' to see available commands.")

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except EOFError:
            console.print("\n[yellow]Goodbye![/yellow]")
            break


if __name__ == "__main__":
    main()
