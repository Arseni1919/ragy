import subprocess
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table
from ragy_api.config import settings
from ragy_cli.constants import ASCII_LOGO, SUBTITLE
from ragy_cli.commands import COMMANDS, COMMAND_MAP, COMMAND_GROUPS
from ragy_cli.handlers import (
    handle_search,
    handle_extract,
    handle_create,
    handle_list,
    handle_stats,
    handle_status,
    handle_delete,
    handle_health,
    handle_info,
    handle_jobs,
    handle_create_job,
    handle_delete_job,
    handle_sample,
    handle_head_index,
    handle_tail_index,
    handle_change_emb_model,
    handle_xray,
    handle_upload_csv,
)


console = Console()


def ensure_api_running() -> bool:
    from ragy_cli.api_client import APIClient

    client = APIClient()

    try:
        client.health_check()
        console.print(f"[dim]API server is already running on port {settings.API_PORT}[/dim]\n")
        return True
    except:
        pass

    console.print("[yellow]API server is not running.[/yellow]")
    console.print("[cyan]To start API server in background, the following command will be executed:[/cyan]")
    console.print(f"  [dim]uv run uvicorn ragy_api.main:app --host {settings.API_HOST} --port {settings.API_PORT}[/dim]")
    console.print("[cyan]To stop it later, use:[/cyan]")
    console.print("  [dim]pkill -f 'uvicorn ragy_api.main:app'[/dim]")
    console.print()

    response = console.input("[cyan]Start API server? (Y/n):[/cyan] ").strip().lower()
    if response and response not in ['y', 'yes', '']:
        console.print("[yellow]API server not started. Please start it manually:[/yellow]")
        console.print("  [dim]uv run uvicorn ragy_api.main:app --reload[/dim]")
        return False

    console.print("[cyan]Starting API server (loading embedding model, ~15 seconds)...[/cyan]")

    try:
        process = subprocess.Popen(
            ["uv", "run", "uvicorn", "ragy_api.main:app", "--host", settings.API_HOST, "--port", str(settings.API_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            text=True
        )

        for i in range(30):
            time.sleep(1)
            try:
                client.health_check()
                console.print(f"[green]✓[/green] API server started on port {settings.API_PORT} (took {i+1}s)\n")
                return True
            except:
                poll = process.poll()
                if poll is not None:
                    console.print(f"[red]API server process exited with code {poll}[/red]")
                    console.print("[red]Error output:[/red]")
                    stderr_output = process.stderr.read()
                    if stderr_output:
                        console.print(stderr_output)
                    return False

                if i % 5 == 4:
                    console.print(f"[dim]Still loading... ({i+1}s)[/dim]")
                continue

        console.print("[red]Failed to start API server (timeout after 30s)[/red]")
        console.print("[yellow]Checking for errors...[/yellow]")

        poll = process.poll()
        if poll is not None:
            stderr_output = process.stderr.read()
            if stderr_output:
                console.print("[red]Error output:[/red]")
                console.print(stderr_output)

        return False

    except Exception as e:
        console.print(f"[red]Error starting API:[/red]")
        import traceback
        console.print(traceback.format_exc())
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
    groups = list(COMMAND_GROUPS.items())
    table = Table(show_header=False, box=None, padding=(0, 3))
    table.add_column("Left", style="white")
    table.add_column("Right", style="white")
    left_groups = []
    right_groups = []
    for i, (group_name, commands) in enumerate(groups):
        lines = [f"[bold yellow]{group_name}[/bold yellow]"]
        for cmd in commands:
            lines.append(f"[cyan]{cmd.name:14}[/cyan] {cmd.description}")
        lines.append("")
        if i < len(groups) // 2 + len(groups) % 2:
            left_groups.extend(lines)
        else:
            right_groups.extend(lines)
    max_rows = max(len(left_groups), len(right_groups))
    left_groups.extend([""] * (max_rows - len(left_groups)))
    right_groups.extend([""] * (max_rows - len(right_groups)))
    for left, right in zip(left_groups, right_groups):
        table.add_row(left, right)
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
        "create_index": handle_create,
        "list": handle_list,
        "stats": handle_stats,
        "status": handle_status,
        "delete_index": handle_delete,
        "health": handle_health,
        "info": handle_info,
        "jobs": handle_jobs,
        "create_job": handle_create_job,
        "delete_job": handle_delete_job,
        "sample": handle_sample,
        "head_index": handle_head_index,
        "tail_index": handle_tail_index,
        "change_emb": handle_change_emb_model,
        "xray": handle_xray,
        "upload_csv": handle_upload_csv,
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
