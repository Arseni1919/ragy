import subprocess
import time
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


def ensure_api_running() -> bool:
    from ragy_cli.api_client import APIClient

    client = APIClient()

    try:
        client.health_check()
        console.print("[dim]API server is already running[/dim]\n")
        return True
    except:
        pass

    console.print("[yellow]API server is not running.[/yellow]")
    console.print("[cyan]To start API server in background, the following command will be executed:[/cyan]")
    console.print("  [dim]uvicorn ragy_api.main:app --host 0.0.0.0 --port 8000[/dim]")
    console.print("[cyan]To stop it later, use:[/cyan]")
    console.print("  [dim]pkill -f 'uvicorn ragy_api.main:app'[/dim]")
    console.print()

    response = console.input("[cyan]Start API server? (Y/n):[/cyan] ").strip().lower()
    if response and response not in ['y', 'yes', '']:
        console.print("[yellow]API server not started. Please start it manually:[/yellow]")
        console.print("  [dim]uv run uvicorn ragy_api.main:app --reload[/dim]")
        return False

    console.print("[cyan]Starting API server in background...[/cyan]")

    try:
        subprocess.Popen(
            ["uvicorn", "ragy_api.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        for i in range(10):
            time.sleep(1)
            try:
                client.health_check()
                console.print("[green]✓[/green] API server started\n")
                return True
            except:
                continue

        console.print("[red]Failed to start API server (timeout)[/red]")
        return False

    except Exception as e:
        console.print(f"[red]Error starting API: {e}[/red]")
        return False


def shutdown_api_server():
    console.print("[yellow]Stopping API server...[/yellow]")

    try:
        result = subprocess.run(
            ["pkill", "-f", "uvicorn ragy_api.main:app"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            console.print("[green]✓[/green] API server stopped")
        else:
            console.print("[yellow]No API server process found[/yellow]")

    except Exception as e:
        console.print(f"[red]Error stopping API: {e}[/red]")


def print_header():
    console.print(ASCII_LOGO)
    console.print(SUBTITLE)
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
    if not ensure_api_running():
        return

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

            if cmd == "shutdown":
                shutdown_api_server()
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
