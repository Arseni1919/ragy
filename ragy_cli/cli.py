from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table
from ragy_cli.constants import ASCII_LOGO, SUBTITLE
from ragy_cli.commands import COMMANDS, COMMAND_MAP
from ragy_cli.handlers import (
    handle_search,
    handle_extract,
    handle_create,
    handle_list,
    handle_show,
    handle_status,
    handle_delete,
    handle_health,
    handle_info,
    handle_jobs,
)


console = Console()


def print_header():
    console.print(ASCII_LOGO, justify="center")
    console.print(SUBTITLE, justify="center")
    console.print()


def print_help():
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Command", style="cyan", width=12)
    table.add_column("Description", style="white", width=28)
    table.add_column("Command", style="cyan", width=12)
    table.add_column("Description", style="white", width=28)

    mid = len(COMMANDS) // 2 + len(COMMANDS) % 2
    for i in range(mid):
        left_cmd = COMMANDS[i]
        right_cmd = COMMANDS[i + mid] if i + mid < len(COMMANDS) else None

        if right_cmd:
            table.add_row(
                left_cmd.name,
                left_cmd.description,
                right_cmd.name,
                right_cmd.description
            )
        else:
            table.add_row(left_cmd.name, left_cmd.description, "", "")

    console.print(table)
    console.print()


def main():
    print_header()
    print_help()

    command_names = [cmd.name for cmd in COMMANDS]
    completer = WordCompleter(command_names, ignore_case=True)
    session = PromptSession(completer=completer)

    handlers = {
        "search": handle_search,
        "extract": handle_extract,
        "create": handle_create,
        "list": handle_list,
        "show": handle_show,
        "status": handle_status,
        "delete": handle_delete,
        "health": handle_health,
        "info": handle_info,
        "jobs": handle_jobs,
    }

    while True:
        try:
            cmd = session.prompt("ragy> ").strip().lower()

            if not cmd:
                continue

            if cmd in ["exit", "quit", "q"]:
                console.print("[cyan]Goodbye![/cyan]")
                break

            if cmd == "help":
                print_help()
                continue

            if cmd in handlers:
                if cmd in COMMAND_MAP:
                    console.print(f"[dim]{COMMAND_MAP[cmd].tip}[/dim]")
                handlers[cmd]()
                console.print()
            else:
                console.print(f"[red]Unknown command: {cmd}[/red]")
                console.print("[yellow]Available commands:[/yellow]\n")
                print_help()

        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except EOFError:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
