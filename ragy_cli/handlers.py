from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from ragy_cli.api_client import APIClient


console = Console()
client = APIClient()


def get_collection_completer():
    try:
        collections = client.list_collections()
        return WordCompleter(collections, ignore_case=True)
    except:
        return WordCompleter([], ignore_case=True)


def prompt_collection(prompt_text: str, allow_empty: bool = False) -> str:
    completer = get_collection_completer()
    session = PromptSession(completer=completer)

    try:
        result = session.prompt(prompt_text).strip()
        return result
    except (KeyboardInterrupt, EOFError):
        return ""


def handle_search():
    query = console.input("[cyan]Search query:[/cyan] ").strip()
    if not query:
        console.print("[red]Query cannot be empty[/red]")
        return

    try:
        with console.status("[cyan]Searching...[/cyan]"):
            result = client.search_web(query)

        if not result.get('results'):
            console.print("[yellow]No results found[/yellow]")
            return

        table = Table(title=f"Search Results: {result['query']}", title_style="bold cyan")
        table.add_column("Title", style="cyan", width=40)
        table.add_column("URL", style="blue", width=50)
        table.add_column("Content", style="white", width=60)

        for r in result['results'][:5]:
            table.add_row(
                r['title'][:38] + "..." if len(r['title']) > 40 else r['title'],
                r['url'][:48] + "..." if len(r['url']) > 50 else r['url'],
                r['content'][:58] + "..." if len(r['content']) > 60 else r['content']
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_extract():
    query = console.input("[cyan]Query:[/cyan] ").strip()
    if not query:
        console.print("[red]Query cannot be empty[/red]")
        return

    collection = prompt_collection("Collection: ")
    if not collection:
        console.print("[red]Collection cannot be empty[/red]")
        return

    top_k_input = console.input("[cyan]Top K (default 10):[/cyan] ").strip()
    top_k = int(top_k_input) if top_k_input else 10

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Extracting...", total=100)

            final_data = None
            for update in client.extract_data(query, collection, top_k):
                if update['status'] == 'in_progress':
                    progress.update(task, completed=update['progress'], description=update.get('message', 'Extracting...'))
                elif update['status'] == 'success':
                    progress.update(task, completed=100)
                    final_data = update.get('data')
                else:
                    console.print(f"[red]{update['message']}[/red]")
                    return

        if final_data and 'results' in final_data:
            table = Table(title=f"Extraction Results: {query}", title_style="bold cyan")
            table.add_column("Date", style="cyan", width=12)
            table.add_column("Score", style="green", width=8)
            table.add_column("Content", style="white", width=80)

            for r in final_data['results']:
                table.add_row(
                    r['date'],
                    f"{r['score']:.3f}",
                    r['content'][:78] + "..." if len(r['content']) > 80 else r['content']
                )

            console.print(table)
        else:
            console.print("[yellow]No results to display[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_create():
    query = console.input("[cyan]Query:[/cyan] ").strip()
    if not query:
        console.print("[red]Query cannot be empty[/red]")
        return

    collection = prompt_collection("Collection name: ")
    if not collection:
        console.print("[red]Collection name cannot be empty[/red]")
        return

    full_data = console.input("[cyan]Save full data? (y/N):[/cyan] ").strip().lower() in ['y', 'yes']

    days_input = console.input("[cyan]Number of days (default 365):[/cyan] ").strip()
    num_days = int(days_input) if days_input else 365

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Creating index ({num_days} days)...", total=100)

            for update in client.create_index(query, collection, full_data, num_days):
                if update['status'] == 'in_progress':
                    progress.update(task, completed=update['progress'], description=update.get('message', 'Creating...'))
                elif update['status'] == 'success':
                    progress.update(task, completed=100)
                    console.print(f"[green]✓[/green] {update['message']}")
                else:
                    console.print(f"[red]{update['message']}[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_list():
    try:
        with console.status("[cyan]Fetching collections...[/cyan]"):
            collections = client.list_collections()

        if not collections:
            console.print("[yellow]No collections found[/yellow]")
            return

        console.print(f"[bold cyan]Collections ({len(collections)}):[/bold cyan]")
        for i, col in enumerate(collections, 1):
            console.print(f"  [cyan]{i}.[/cyan] {col}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_stats():
    collection_name = prompt_collection("Collection name (leave empty for all statistics): ")

    try:
        if collection_name:
            with console.status(f"[cyan]Fetching {collection_name}...[/cyan]"):
                stats = client.get_database_stats()

            col_stats = None
            for col in stats['collections']:
                if col['name'] == collection_name:
                    col_stats = col
                    break

            if not col_stats:
                console.print(f"[red]Collection '{collection_name}' not found[/red]")
                return

            console.print(f"\n[bold cyan]Collection: {col_stats['name']}[/bold cyan]\n")

            stats_table = Table(show_header=False, box=None, padding=(0, 2))
            stats_table.add_column("Metric", style="cyan", width=20)
            stats_table.add_column("Value", style="white", width=30)

            stats_table.add_row("Documents:", f"{col_stats['count']:,}")
            stats_table.add_row("Date Range:", f"{col_stats['earliest_date']} to {col_stats['latest_date']}")

            console.print(stats_table)
        else:
            with console.status("[cyan]Calculating database statistics...[/cyan]"):
                stats = client.get_database_stats()

            console.print("\n[bold cyan]═══ Overall Database Statistics ═══[/bold cyan]\n")

            overall_table = Table(show_header=False, box=None, padding=(0, 2))
            overall_table.add_column("Metric", style="cyan", width=30)
            overall_table.add_column("Value", style="white", width=20)

            overall_table.add_row("Total Collections:", str(stats['total_collections']))
            overall_table.add_row("Total Documents:", f"{stats['total_documents']:,}")
            overall_table.add_row("Total Size:", f"{stats['total_size_mb']:.2f} MB")
            overall_table.add_row("Average Docs/Collection:", f"{stats['avg_docs_per_collection']:.0f}")

            console.print(overall_table)
            console.print()

            if stats['collections']:
                console.print("[bold cyan]═══ Collections (Ordered by Documents) ═══[/bold cyan]\n")

                collections_table = Table(show_header=True)
                collections_table.add_column("Collection", style="cyan", width=30)
                collections_table.add_column("Documents", style="green", width=15, justify="right")
                collections_table.add_column("Date Range", style="blue", width=30)

                for col in stats['collections']:
                    date_range = f"{col['earliest_date']} to {col['latest_date']}"
                    collections_table.add_row(
                        col['name'],
                        f"{col['count']:,}",
                        date_range
                    )

                console.print(collections_table)
            else:
                console.print("[yellow]No collections found[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_status():
    collection = prompt_collection("Collection name: ")
    if not collection:
        console.print("[red]Collection name cannot be empty[/red]")
        return

    try:
        with console.status(f"[cyan]Checking status of {collection}...[/cyan]"):
            status = client.get_index_status(collection)

        if status.get('exists'):
            console.print(f"[green]✓[/green] Collection: [cyan]{status['collection_name']}[/cyan]")
            console.print(f"  Status: [green]Exists[/green]")
            console.print(f"  Documents: [cyan]{status['total_docs']}[/cyan]")
        else:
            console.print(f"[yellow]Collection '{collection}' does not exist[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_delete():
    collection = prompt_collection("Collection name: ")
    if not collection:
        console.print("[red]Collection name cannot be empty[/red]")
        return

    confirm = console.input(f"[red]Are you sure you want to delete '{collection}'? (y/N):[/red] ").strip().lower()
    if confirm not in ['y', 'yes']:
        console.print("[yellow]Cancelled[/yellow]")
        return

    try:
        with console.status(f"[cyan]Deleting {collection}...[/cyan]"):
            result = client.delete_collection(collection)
        console.print(f"[green]✓[/green] {result.get('message', 'Deleted successfully')}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_health():
    try:
        with console.status("[cyan]Checking health...[/cyan]"):
            health = client.health_check()

        console.print("[bold cyan]API Health Status:[/bold cyan]")
        console.print(f"  Overall: [{'green' if health['status'] == 'healthy' else 'red'}]{health['status']}[/]")
        console.print(f"  Database: [{'green' if health['database'] == 'ok' else 'red'}]{health['database']}[/]")
        console.print(f"  Embedding Model: [{'green' if health['embedding_model'] == 'ok' else 'red'}]{health['embedding_model']}[/]")
        console.print(f"  Scheduler: [{'green' if health['scheduler'] == 'running' else 'yellow'}]{health['scheduler']}[/]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_info():
    try:
        with console.status("[cyan]Fetching embedding info...[/cyan]"):
            info = client.get_embedding_info()

        console.print("[bold cyan]Embedding Model Information:[/bold cyan]")
        console.print(f"  Model: [cyan]{info['model']}[/cyan]")
        console.print(f"  Dimensions: [cyan]{info['dimensions']}[/cyan]")
        console.print(f"  Max Sequence Length: [cyan]{info['max_seq_length']}[/cyan]")
        console.print(f"  Context Window: [cyan]{info['context_window']}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_jobs():
    try:
        with console.status("[cyan]Fetching scheduler jobs...[/cyan]"):
            jobs_data = client.get_scheduler_jobs()

        jobs = jobs_data.get('jobs', [])
        if not jobs:
            console.print("[yellow]No scheduled jobs found[/yellow]")
            return

        table = Table(title="Scheduler Jobs", title_style="bold cyan")
        table.add_column("ID", style="cyan", width=15)
        table.add_column("Name", style="white", width=30)
        table.add_column("Next Run", style="green", width=30)

        for job in jobs:
            table.add_row(
                job['id'],
                job['name'],
                job.get('next_run', 'N/A')
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
