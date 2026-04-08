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


def handle_search_web():
    from rich.panel import Panel
    from ragy_api.constants import AVAILABLE_SOURCES, SOURCE_DESCRIPTIONS

    source_completer = WordCompleter(AVAILABLE_SOURCES, ignore_case=True)
    session = PromptSession(completer=source_completer)

    try:
        source_desc = ", ".join([f"{src} ({SOURCE_DESCRIPTIONS[src]})" for src in AVAILABLE_SOURCES])
        console.print(f"[dim]Available sources: {source_desc}[/dim]")
        source = session.prompt("[cyan]Data source:[/cyan] ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return

    if source not in AVAILABLE_SOURCES:
        console.print(f"[red]Invalid source. Must be one of: {', '.join(AVAILABLE_SOURCES)}[/red]")
        return

    query = console.input("[cyan]Search query:[/cyan] ").strip()
    if not query:
        console.print("[red]Query cannot be empty[/red]")
        return

    max_results_input = console.input("[cyan]Max results (default 5):[/cyan] ").strip()
    max_results = int(max_results_input) if max_results_input.isdigit() else 5

    try:
        source_label = SOURCE_DESCRIPTIONS.get(source, source)
        with console.status(f"[cyan]Searching {source_label} for '{query}'...[/cyan]"):
            if source == "bright_data":
                result = client.search_bright_data(query, max_results)
            elif source == "tavily":
                result = client.search_web(query, max_results)
            elif source == "yfinance":
                result = client.search_yfinance(query, max_results)
            else:
                console.print(f"[red]Unknown source: {source}[/red]")
                return

        console.print(f"\n[green]✓[/green] Found {len(result['results'])} results for: [cyan]{result['query']}[/cyan]\n")

        if not result.get('results'):
            console.print("[yellow]No results found[/yellow]")
            return

        for i, item in enumerate(result['results'], 1):
            title = item.get('title', 'N/A')
            url = item.get('url', 'N/A')
            content = item.get('raw_content', item.get('content', 'N/A'))

            panel_content = f"[bold]{title}[/bold]\n\n"
            panel_content += f"[dim]{content}[/dim]\n\n"
            panel_content += f"[blue]🔗 {url}[/blue]"

            panel = Panel(
                panel_content,
                title=f"Result {i}",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(panel)
            console.print()

        console.print(f"[dim]Total: {len(result['results'])} results via {source_label}[/dim]")

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

    days_input = console.input("[cyan]Number of days (default 365):[/cyan] ").strip()
    num_days = int(days_input) if days_input else 365

    from ragy_api.constants import AVAILABLE_SOURCES, get_sources_prompt

    source_completer = WordCompleter(AVAILABLE_SOURCES, ignore_case=True)
    source_session = PromptSession(completer=source_completer)

    console.print(f"\n[cyan]{get_sources_prompt()}[/cyan]")
    console.print("[dim]Tip: Use Tab for autocomplete[/dim]\n")

    while True:
        try:
            source = source_session.prompt("Data source: ").strip().lower()
            if source in AVAILABLE_SOURCES:
                break
            console.print(f"[red]Invalid source. Choose: {', '.join(AVAILABLE_SOURCES)}[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Cancelled[/yellow]")
            return

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

            for update in client.create_index(query, collection, num_days, source):
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


def render_timeline(distribution: dict) -> None:
    import plotext as plt
    from datetime import datetime

    dates = distribution.get('dates', [])
    counts = distribution.get('counts', [])

    if not dates or not counts:
        return

    x_values = list(range(len(dates)))

    num_labels = min(8, len(dates))
    if num_labels > 0:
        step = max(1, len(dates) // num_labels)
        label_indices = list(range(0, len(dates), step))
        if label_indices[-1] != len(dates) - 1:
            label_indices.append(len(dates) - 1)

        x_labels = [dates[i] for i in label_indices]
        x_coords = [i for i in label_indices]
    else:
        x_labels = []
        x_coords = []

    plt.clear_figure()
    plt.theme('clear')
    plt.plot(x_values, counts)
    plt.xticks(x_coords, x_labels)
    plt.title("Document Distribution Over Time")
    plt.xlabel("Date")
    plt.ylabel("Documents")
    plt.plot_size(width=None, height=15)
    plt.show()


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

            try:
                distribution = client.get_collection_distribution(collection_name)
                console.print()
                render_timeline(distribution)
            except Exception as e:
                console.print(f"[yellow]Could not load timeline: {e}[/yellow]")

            try:
                collection_details = client.get_collection(collection_name)
                sample_data = collection_details.get('sample_data', [])

                if sample_data:
                    console.print(f"\n[bold cyan]Sample Documents (first 5):[/bold cyan]\n")

                    docs_table = Table(show_header=True)
                    docs_table.add_column("#", style="dim", width=3, no_wrap=True)
                    docs_table.add_column("Date", style="cyan", width=18, no_wrap=True)
                    docs_table.add_column("Content", style="white", width=81)

                    for i, doc in enumerate(sample_data, 1):
                        docs_table.add_row(str(i), doc['date'], doc['content'])

                    console.print(docs_table)
            except Exception as e:
                console.print(f"[yellow]Could not load sample documents: {e}[/yellow]")
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
        with console.status("[cyan]Fetching scheduled jobs...[/cyan]"):
            jobs_data = client.get_user_jobs()

        jobs = jobs_data.get('jobs', [])
        if not jobs:
            console.print("[yellow]No scheduled jobs found[/yellow]")
            console.print("[dim]Create a job with: create_job[/dim]")
            return

        table = Table(title="Scheduled Jobs", title_style="bold cyan")
        table.add_column("ID", style="cyan", width=5, justify="right")
        table.add_column("Query", style="white", width=22)
        table.add_column("Collection", style="blue", width=18)
        table.add_column("Source", style="magenta", width=8)
        table.add_column("Interval", style="green", width=12)
        table.add_column("Next Run", style="yellow", width=20)
        table.add_column("Runs", style="dim", width=6, justify="right")

        for job in jobs:
            interval_desc = f"{job['interval_amount']} {job['interval_type']}{'s' if job['interval_amount'] > 1 else ''}"
            next_run = job.get('next_run', 'N/A')
            if next_run and next_run != 'N/A':
                next_run = next_run[:19] if len(next_run) > 19 else next_run

            table.add_row(
                str(job['job_id']),
                job['query'][:20] + "..." if len(job['query']) > 22 else job['query'],
                job['collection_name'][:16] + "..." if len(job['collection_name']) > 18 else job['collection_name'],
                job.get('source', 'tavily'),
                interval_desc,
                next_run,
                str(job['run_count'])
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_sample():
    collection_name = prompt_collection("Collection name: ")
    if not collection_name:
        console.print("[red]Collection name cannot be empty[/red]")
        return

    index_input = console.input("[cyan]Document index (0-based):[/cyan] ").strip()
    if not index_input:
        console.print("[red]Index cannot be empty[/red]")
        return

    try:
        index = int(index_input)
        if index < 0:
            console.print("[red]Index must be non-negative[/red]")
            return
    except ValueError:
        console.print("[red]Index must be a number[/red]")
        return

    try:
        with console.status(f"[cyan]Fetching document {index} from {collection_name}...[/cyan]"):
            doc = client.get_sample_document(collection_name, index)

        if not doc:
            console.print(f"[yellow]Document at index {index} not found[/yellow]")
            return

        console.print(f"\n[bold cyan]Document at Index {index} in {collection_name}[/bold cyan]\n")

        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("Field", style="cyan", width=20)
        info_table.add_column("Value", style="white", width=80)

        info_table.add_row("ID:", doc.get('id', 'N/A'))
        content = doc.get('content', '')
        truncated_content = content[:400] + ("..." if len(content) > 400 else "")
        info_table.add_row("Content (400 chars):", truncated_content)

        console.print(info_table)

        embedding = doc.get('embedding', [])
        if embedding:
            console.print(f"\n[bold cyan]Embedding (first 10 values):[/bold cyan]")
            console.print(f"[dim][{', '.join(map(str, embedding[:10]))}, ...][/dim]")
            console.print(f"[dim]Total dimensions: {len(embedding)}[/dim]\n")

        metadata = doc.get('metadata', {})
        if metadata:
            console.print(f"[bold cyan]Metadata:[/bold cyan]")

            meta_table = Table(show_header=False, box=None, padding=(0, 2))
            meta_table.add_column("Key", style="cyan", width=20)
            meta_table.add_column("Value", style="white", width=80)

            for key, value in metadata.items():
                meta_table.add_row(key, str(value))

            console.print(meta_table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_create_job():
    console.print("[bold cyan]Create Scheduled Job[/bold cyan]\n")

    query = console.input("[cyan]Search query:[/cyan] ").strip()
    if not query:
        console.print("[red]Query cannot be empty[/red]")
        return

    collection = prompt_collection("Collection name (will be created if doesn't exist): ")
    if not collection:
        console.print("[red]Collection name cannot be empty[/red]")
        return

    try:
        collections = client.list_collections()
        if collection not in collections:
            console.print(f"[yellow]Note: Collection '{collection}' doesn't exist yet. It will be created on first job run.[/yellow]")
    except:
        pass

    from ragy_api.constants import AVAILABLE_SOURCES, get_sources_prompt

    source_completer = WordCompleter(AVAILABLE_SOURCES, ignore_case=True)
    source_session = PromptSession(completer=source_completer)

    console.print(f"\n[cyan]{get_sources_prompt()}[/cyan]")
    console.print("[dim]Tip: Use Tab for autocomplete[/dim]\n")

    while True:
        try:
            source = source_session.prompt("Data source: ").strip().lower()
            if source in AVAILABLE_SOURCES:
                break
            console.print(f"[red]Invalid source. Choose: {', '.join(AVAILABLE_SOURCES)}[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Cancelled[/yellow]")
            return

    interval_types = ['minute', 'hour', 'day', 'week', 'month', 'year']
    interval_completer = WordCompleter(interval_types, ignore_case=True)
    interval_session = PromptSession(completer=interval_completer)

    console.print("\n[cyan]Available intervals: minute, hour, day, week, month, year[/cyan]")
    console.print("[dim]Tip: Use Tab for autocomplete[/dim]\n")

    while True:
        try:
            interval_type = interval_session.prompt("Interval type: ").strip().lower()
            if interval_type in interval_types:
                break
            console.print("[red]Invalid interval type. Choose: minute, hour, day, week, month, or year[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Cancelled[/yellow]")
            return

    if interval_type in ['month', 'year']:
        interval_amount = 1
        if interval_type == 'month':
            console.print("[dim]Job will run on the 1st of every month at midnight UTC[/dim]")
        else:
            console.print("[dim]Job will run on January 1st every year at midnight UTC[/dim]")
    else:
        while True:
            amount_input = console.input(f"[cyan]Run every how many {interval_type}s? (1-1000):[/cyan] ").strip()
            try:
                interval_amount = int(amount_input)
                if 1 <= interval_amount <= 1000:
                    break
                console.print("[red]Amount must be between 1 and 1000[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")

    console.print("\n[bold cyan]Job Summary:[/bold cyan]")
    console.print(f"  Query: [white]{query}[/white]")
    console.print(f"  Collection: [white]{collection}[/white]")
    console.print(f"  Source: [white]{source}[/white]")
    if interval_type in ['month', 'year']:
        console.print(f"  Schedule: [white]Every {interval_type}[/white]")
    else:
        plural = 's' if interval_amount > 1 else ''
        console.print(f"  Schedule: [white]Every {interval_amount} {interval_type}{plural}[/white]")
    console.print(f"  Action: [white]Run query and save results with timestamp[/white]\n")

    confirm = console.input("[cyan]Create this job? (Y/n):[/cyan] ").strip().lower()
    if confirm and confirm not in ['y', 'yes', '']:
        console.print("[yellow]Cancelled[/yellow]")
        return

    try:
        with console.status("[cyan]Creating job...[/cyan]"):
            result = client.create_scheduled_job(query, collection, interval_type, interval_amount, source)

        console.print(f"[green]✓[/green] {result['message']}")
        console.print(f"[dim]Job ID: {result['job_id']}[/dim]")
        console.print(f"[dim]Source: {result['source']}[/dim]")
        console.print(f"[dim]Use 'delete_job' to remove this job[/dim]")

    except Exception as e:
        console.print(f"[red]Error creating job: {e}[/red]")


def handle_delete_job():
    try:
        with console.status("[cyan]Fetching jobs...[/cyan]"):
            jobs_data = client.get_user_jobs()

        jobs = jobs_data.get('jobs', [])
        if not jobs:
            console.print("[yellow]No scheduled jobs found[/yellow]")
            return

        table = Table(title="Scheduled Jobs", title_style="bold cyan")
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Query", style="white", width=30)
        table.add_column("Collection", style="blue", width=20)
        table.add_column("Interval", style="green", width=15)

        for job in jobs:
            interval_desc = f"{job['interval_amount']} {job['interval_type']}{'s' if job['interval_amount'] > 1 else ''}"
            table.add_row(
                str(job['job_id']),
                job['query'],
                job['collection_name'],
                interval_desc
            )

        console.print(table)
        console.print()

        job_id_input = console.input("[cyan]Enter Job ID to delete:[/cyan] ").strip()
        if not job_id_input:
            console.print("[yellow]Cancelled[/yellow]")
            return

        try:
            job_id = int(job_id_input)
        except ValueError:
            console.print("[red]Invalid job ID[/red]")
            return

        job_to_delete = next((j for j in jobs if j['job_id'] == job_id), None)
        if not job_to_delete:
            console.print(f"[red]Job ID {job_id} not found[/red]")
            return

        console.print(f"[yellow]About to delete:[/yellow]")
        console.print(f"  Query: {job_to_delete['query']}")
        console.print(f"  Collection: {job_to_delete['collection_name']}")

        confirm = console.input("\n[red]Are you sure? (y/N):[/red] ").strip().lower()
        if confirm not in ['y', 'yes']:
            console.print("[yellow]Cancelled[/yellow]")
            return

        with console.status("[cyan]Deleting job...[/cyan]"):
            result = client.delete_scheduled_job(job_id)

        console.print(f"[green]✓[/green] {result['message']}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_head_index():
    collection_name = prompt_collection("Collection name: ")
    if not collection_name:
        console.print("[red]Collection name cannot be empty[/red]")
        return

    try:
        with console.status(f"[cyan]Fetching first 5 documents from {collection_name}...[/cyan]"):
            result = client.get_head_documents(collection_name, limit=5)

        documents = result.get('documents', [])

        if not documents:
            console.print(f"[yellow]Collection {collection_name} is empty[/yellow]")
            return

        console.print(f"\n[bold cyan]First {len(documents)} documents from {collection_name}[/bold cyan]\n")

        docs_table = Table(show_header=True)
        docs_table.add_column("Index", style="dim", width=6, no_wrap=True)
        docs_table.add_column("ID", style="yellow", width=10, no_wrap=True)
        docs_table.add_column("Date", style="cyan", width=20, no_wrap=True)
        docs_table.add_column("Content", style="white", width=75)

        for doc in documents:
            index_str = str(doc['index'])
            doc_id = doc['id']
            date_str = doc.get('metadata', {}).get('date', 'N/A')
            content = doc.get('content', '')
            truncated = content[:200] if len(content) > 200 else content
            docs_table.add_row(index_str, doc_id, date_str, truncated)

        console.print(docs_table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_tail_index():
    collection_name = prompt_collection("Collection name: ")
    if not collection_name:
        console.print("[red]Collection name cannot be empty[/red]")
        return

    try:
        with console.status(f"[cyan]Fetching last 5 documents from {collection_name}...[/cyan]"):
            result = client.get_tail_documents(collection_name, limit=5)

        documents = result.get('documents', [])

        if not documents:
            console.print(f"[yellow]Collection {collection_name} is empty[/yellow]")
            return

        console.print(f"\n[bold cyan]Last {len(documents)} documents from {collection_name}[/bold cyan]\n")

        docs_table = Table(show_header=True)
        docs_table.add_column("Index", style="dim", width=6, no_wrap=True)
        docs_table.add_column("ID", style="yellow", width=10, no_wrap=True)
        docs_table.add_column("Date", style="cyan", width=20, no_wrap=True)
        docs_table.add_column("Content", style="white", width=75)

        for doc in documents:
            index_str = str(doc['index'])
            doc_id = doc['id']
            date_str = doc.get('metadata', {}).get('date', 'N/A')
            content = doc.get('content', '')
            truncated = content[:200] if len(content) > 200 else content
            docs_table.add_row(index_str, doc_id, date_str, truncated)

        console.print(docs_table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def handle_change_emb_model():
    import os
    from pathlib import Path

    console.print("\n[bold cyan]═══ Change Embedding Model ═══[/bold cyan]\n")

    env_path = Path(".env")
    if not env_path.exists():
        console.print("[red]Error: .env file not found[/red]")
        return

    current_model = os.getenv("HF_EMB_MODEL", "google/embeddinggemma-300m")

    console.print(f"[cyan]Current model:[/cyan] {current_model}\n")

    console.print("[yellow]About Embedding Models:[/yellow]")
    console.print("  • Embedding models convert text to vectors for similarity search")
    console.print("  • Popular models:")
    console.print("    - all-MiniLM-L6-v2 (fast, 384 dims)")
    console.print("    - google/embeddinggemma-300m (high quality, 768 dims)")
    console.print("    - BAAI/bge-small-en-v1.5 (good balance, 384 dims)")
    console.print("  • Find models at: https://huggingface.co/models?pipeline_tag=sentence-similarity\n")

    new_model = console.input("[cyan]Enter new model name (or press Enter to cancel):[/cyan] ").strip()

    if not new_model:
        console.print("[yellow]Cancelled[/yellow]")
        return

    try:
        env_content = env_path.read_text()
        lines = env_content.split('\n')
        updated = False

        for i, line in enumerate(lines):
            if line.startswith('HF_EMB_MODEL=') or line.startswith('# HF_EMB_MODEL='):
                lines[i] = f'HF_EMB_MODEL="{new_model}"'
                updated = True
                break

        if not updated:
            lines.append(f'HF_EMB_MODEL="{new_model}"')

        env_path.write_text('\n'.join(lines))

        console.print(f"\n[green]✓ Updated HF_EMB_MODEL to:[/green] {new_model}")
        console.print("\n[yellow]⚠ IMPORTANT - Next Steps:[/yellow]")
        console.print("  1. Exit this CLI with: [cyan]shutdown[/cyan]")
        console.print("  2. Restart the CLI: [cyan]uv run ragy[/cyan]")
        console.print("  3. The new embedding model will be loaded on startup")
        console.print("\n[dim]Note: All existing indexes were created with the old model.")
        console.print("You may want to recreate indexes for consistency.[/dim]\n")

    except Exception as e:
        console.print(f"[red]Error updating .env file: {e}[/red]")

def _fetch_xray_data(query: str, collection_name: str) -> dict | None:
    try:
        with console.status(f"[cyan]Analyzing {collection_name}...[/cyan]"):
            return client.extract_all_for_xray(query, collection_name)
    except Exception as e:
        console.print(f"[red]Error fetching data from {collection_name}: {e}[/red]")
        return None

def _prepare_timeline_data(results: list, top_k: int) -> dict | None:
    from datetime import datetime
    if not results:
        return None
    top_results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
    top_dates = {r['date'] for r in top_results}
    results_sorted = sorted(results, key=lambda x: x['date'])
    dates = [r['date'] for r in results_sorted]
    scores = [r['score'] if r['date'] in top_dates else 0 for r in results_sorted]
    date_objs = []
    for d in dates:
        try:
            date_str = d[:10] if len(d) >= 10 else d
            date_objs.append(datetime.strptime(date_str, '%Y-%m-%d'))
        except Exception as e:
            console.print(f"[red]Error parsing date '{d}': {e}[/red]")
            continue
    if not date_objs:
        return None
    start_date = date_objs[0]
    x_values = [(d - start_date).days for d in date_objs]
    return {
        'dates': dates,
        'scores': scores,
        'x_values': x_values,
        'top_results': top_results
    }

def _plot_timeline(timeline_data: dict, collection_name: str):
    import plotext as plt
    dates = timeline_data['dates']
    scores = timeline_data['scores']
    x_values = timeline_data['x_values']
    plt.clear_figure()
    plt.plot(x_values, scores, color='red')
    num_labels = min(8, len(dates))
    if num_labels > 0:
        step = max(1, len(dates) // num_labels)
        label_indices = list(range(0, len(dates), step))
        if label_indices[-1] != len(dates) - 1:
            label_indices.append(len(dates) - 1)
        x_labels = [dates[i] for i in label_indices]
        x_coords = [x_values[i] for i in label_indices]
        plt.xticks(x_coords, x_labels)
    plt.title(f"Collection: {collection_name}")
    plt.xlabel("Timeline (Dates)")
    plt.ylabel("Similarity Score")
    plt.plot_size(width=None, height=15)
    plt.show()

def _display_results_table(top_results: list, query: str, top_k: int, collection_name: str):
    console.print(f"\n[bold cyan]Top {top_k} Results from {collection_name}[/bold cyan]\n")
    table = Table(title=f"Query: {query}", title_style="bold cyan")
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Score", style="green", width=8)
    table.add_column("Content", style="white", width=80)
    for r in top_results:
        date_display = r['date'][:10] if len(r['date']) >= 10 else r['date']
        table.add_row(
            date_display,
            f"{r['score']:.3f}",
            r['content'][:78] + "..." if len(r['content']) > 80 else r['content']
        )
    console.print(table)

def handle_xray():
    collection = prompt_collection("Collection (leave empty for all): ")
    query = console.input("[cyan]Query:[/cyan] ").strip()
    if not query:
        console.print("[red]Query cannot be empty[/red]")
        return
    top_k_input = console.input("[cyan]Top K (default 10):[/cyan] ").strip()
    top_k = int(top_k_input) if top_k_input else 10
    if not collection:
        try:
            collections = client.list_collections()
            if not collections:
                console.print("[yellow]No collections found in database[/yellow]")
                return
            console.print(f"[cyan]Processing all {len(collections)} collections (plots only)...[/cyan]\n")
        except Exception as e:
            console.print(f"[red]Error listing collections: {e}[/red]")
            return
        show_tables = False
    else:
        collections = [collection]
        show_tables = True
    for col_name in collections:
        data = _fetch_xray_data(query, col_name)
        if not data:
            continue
        results = data.get('results', [])
        if not results:
            console.print(f"[yellow]No results found in {col_name}[/yellow]\n")
            continue
        timeline_data = _prepare_timeline_data(results, top_k)
        if not timeline_data:
            console.print(f"[yellow]No valid dates in {col_name}[/yellow]\n")
            continue
        _plot_timeline(timeline_data, col_name)
        if show_tables:
            _display_results_table(timeline_data['top_results'], query, top_k, col_name)
        console.print()

def handle_upload_csv():
    from pathlib import Path
    file_path = console.input("[cyan]CSV file path (drag file here):[/cyan] ").strip().strip("'\"")
    if not file_path:
        console.print("[red]File path cannot be empty[/red]")
        return
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return
    if not path.suffix.lower() == '.csv':
        console.print("[red]File must be a CSV file[/red]")
        return
    collection_name = prompt_collection("Collection name (new or existing): ")
    if not collection_name:
        console.print("[red]Collection name cannot be empty[/red]")
        return
    try:
        with console.status(f"[cyan]Uploading CSV to '{collection_name}'...[/cyan]"):
            result = client.upload_csv(str(path), collection_name)
        console.print(f"[green]✓[/green] Uploaded {result['uploaded']} documents to '{collection_name}'")
        console.print(f"[dim]Total documents in collection: {result['total_documents']}[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
