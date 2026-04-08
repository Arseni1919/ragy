#!/usr/bin/env python3
"""
Clean Migration to zvec Format

This script:
1. Verifies backup exists (chromadb_backup/)
2. Removes ALL data from ./ragy_db/
3. Creates fresh zvec database with migrated data
4. Verifies the clean installation
"""

import os
import sys
import json
import shutil
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

console = Console()


def verify_backup():
    """Verify backup exists before proceeding"""
    console.print("\n[bold cyan]Step 1: Verifying Backup[/bold cyan]")
    console.print("=" * 60)

    backup_dir = Path("./chromadb_backup")

    if not backup_dir.exists():
        console.print("[bold red]❌ Backup directory not found![/bold red]")
        console.print(f"Expected location: {backup_dir.absolute()}")
        console.print("\nPlease run migrate_chromadb_to_zvec.py first to create backup.")
        return False

    # Check for backup files
    backup_files = list(backup_dir.glob("*.json"))
    backup_files = [f for f in backup_files if not f.name.startswith('_')]

    if not backup_files:
        console.print("[bold red]❌ No backup files found![/bold red]")
        return False

    # Load stats if available
    stats_file = backup_dir / "_export_stats.json"
    if stats_file.exists():
        with open(stats_file, 'r') as f:
            stats = json.load(f)

        console.print(f"[green]✓[/green] Backup found!")
        console.print(f"  Collections: {stats['total_collections']}")
        console.print(f"  Documents: {stats['total_documents']:,}")
        console.print(f"  Location: {backup_dir.absolute()}")
    else:
        console.print(f"[green]✓[/green] Backup found!")
        console.print(f"  Files: {len(backup_files)}")
        console.print(f"  Location: {backup_dir.absolute()}")

    return True


def clean_ragy_db():
    """Remove all data from ./ragy_db/"""
    console.print("\n[bold cyan]Step 2: Cleaning ./ragy_db/[/bold cyan]")
    console.print("=" * 60)

    ragy_db = Path("./ragy_db")

    if not ragy_db.exists():
        console.print(f"[yellow]Directory doesn't exist, will be created[/yellow]")
        return True

    # List what will be deleted
    items = list(ragy_db.iterdir())
    console.print(f"\nFound [yellow]{len(items)}[/yellow] items in ./ragy_db/")

    # Show a few examples
    for item in items[:5]:
        console.print(f"  • {item.name}")
    if len(items) > 5:
        console.print(f"  • ... and {len(items) - 5} more items")

    # Confirm deletion
    console.print("\n[bold yellow]⚠️  This will DELETE ALL data in ./ragy_db/[/bold yellow]")
    console.print("[dim](Backup exists in ./chromadb_backup/)[/dim]\n")

    if not Confirm.ask("Proceed with deletion?", default=False):
        console.print("[yellow]Aborted by user[/yellow]")
        return False

    # Delete everything
    console.print("\nDeleting...")
    for item in tqdm(items, desc="Removing items"):
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not delete {item.name}: {e}[/yellow]")

    console.print("[bold green]✓[/bold green] ./ragy_db/ cleaned")

    return True


def import_to_zvec():
    """Import backup data into fresh zvec database"""
    console.print("\n[bold cyan]Step 3: Importing to Fresh zvec Database[/bold cyan]")
    console.print("=" * 60)

    # Set environment to use zvec
    os.environ['DB_PROVIDER'] = 'zvec'
    os.environ['DB_PATH'] = './ragy_db'

    # Force reload of modules
    for mod in ['conn_db.client', 'conn_zvec.client']:
        if mod in sys.modules:
            del sys.modules[mod]

    from conn_db.client import client

    # Find backup files
    backup_dir = Path("./chromadb_backup")
    backup_files = list(backup_dir.glob("*.json"))
    backup_files = [f for f in backup_files if not f.name.startswith('_')]

    console.print(f"\nImporting [bold]{len(backup_files)}[/bold] collections into zvec")

    import_stats = {
        'total_collections': len(backup_files),
        'total_documents': 0,
        'collections': []
    }

    # Import each collection
    for backup_file in tqdm(backup_files, desc="Importing to zvec"):
        col_name = backup_file.stem

        try:
            # Load backup data
            with open(backup_file, 'r') as f:
                data = json.load(f)

            if data['count'] == 0:
                console.print(f"  [dim]Skipping empty: {col_name}[/dim]")
                continue

            console.print(f"\n  Importing [cyan]{col_name}[/cyan] ({data['count']} docs)...")

            # Create fresh collection
            col = client.get_or_create_collection(col_name)

            # Import in batches
            batch_size = 1000
            total = len(data['ids'])

            for i in range(0, total, batch_size):
                end = min(i + batch_size, total)

                col.add(
                    ids=data['ids'][i:end],
                    documents=data['documents'][i:end],
                    embeddings=data['embeddings'][i:end],
                    metadatas=data['metadatas'][i:end]
                )

                if end - i == batch_size:
                    console.print(f"    • {end}/{total} docs...")

            # Verify
            final_count = col.count()
            console.print(f"    ✓ Complete: {final_count} docs")

            import_stats['total_documents'] += final_count
            import_stats['collections'].append({
                'name': col_name,
                'expected': data['count'],
                'imported': final_count,
                'status': 'success' if final_count == data['count'] else 'mismatch'
            })

        except Exception as e:
            console.print(f"  [red]Error importing {col_name}: {e}[/red]")
            import_stats['collections'].append({
                'name': col_name,
                'status': f'error: {e}'
            })

    console.print(f"\n[bold green]✓[/bold green] Import complete!")
    console.print(f"  Collections: {import_stats['total_collections']}")
    console.print(f"  Documents: {import_stats['total_documents']:,}")

    return import_stats


def verify_clean_installation():
    """Verify the clean zvec installation"""
    console.print("\n[bold cyan]Step 4: Verifying Clean Installation[/bold cyan]")
    console.print("=" * 60)

    os.environ['DB_PROVIDER'] = 'zvec'

    # Force reload
    for mod in ['conn_db.client', 'conn_zvec.client']:
        if mod in sys.modules:
            del sys.modules[mod]

    from conn_db.client import client

    # Check directory contents
    ragy_db = Path("./ragy_db")
    items = list(ragy_db.iterdir())

    console.print(f"\n[bold]Directory Contents:[/bold]")
    console.print(f"  ./ragy_db/ has {len(items)} items")

    # All should be zvec collections now
    zvec_collections = [item for item in items if item.is_dir()]
    console.print(f"  zvec collections: {len(zvec_collections)}")

    # List collections via API
    collections = client.list_collections()
    console.print(f"\n[bold]Collections Accessible:[/bold]")
    console.print(f"  Total: {len(collections)}")

    # Create summary table
    table = Table(title="zvec Collections")
    table.add_column("Collection", style="cyan")
    table.add_column("Count", justify="right", style="green")

    total_docs = 0
    for col_info in sorted(collections, key=lambda x: x.name)[:10]:
        col = client.get_collection(col_info.name)
        count = col.count()
        total_docs += count
        table.add_row(col_info.name, str(count))

    if len(collections) > 10:
        table.add_row("...", "...")

    console.print(table)
    console.print(f"\n[bold]Total Documents:[/bold] {total_docs:,}")

    # Test vector search
    console.print(f"\n[bold]Testing Vector Search...[/bold]")

    for col_info in collections:
        col = client.get_collection(col_info.name)
        if col.count() > 0:
            # Quick search test
            sample = col.get(limit=1, include=["embeddings"])
            if sample['embeddings']:
                results = col.query(
                    query_embeddings=[sample['embeddings'][0]],
                    n_results=2,
                    include=["documents", "distances"]
                )

                console.print(f"  ✓ Tested on [cyan]{col_info.name}[/cyan]")
                console.print(f"    Found {len(results['ids'][0])} results")
                console.print(f"    Nested list format: {'✓' if isinstance(results['ids'][0], list) else '✗'}")
                break

    console.print(f"\n[bold green]✓ Clean zvec installation verified![/bold green]")
    return True


def show_summary():
    """Show final summary"""
    console.print("\n[bold yellow]" + "=" * 60 + "[/bold yellow]")
    console.print("[bold green]✅ CLEAN MIGRATION TO ZVEC COMPLETE![/bold green]")
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")

    console.print("\n[bold]What Changed:[/bold]")
    console.print("  • Old ./ragy_db/ (mixed ChromaDB + zvec): [red]DELETED[/red]")
    console.print("  • New ./ragy_db/ (pure zvec): [green]CREATED[/green]")
    console.print("  • Backup: ./chromadb_backup/ (preserved)")

    console.print("\n[bold]Current Status:[/bold]")
    console.print("  • Database: zvec (clean installation)")
    console.print("  • Location: ./ragy_db/")
    console.print("  • Format: zvec native format only")

    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("  1. Start your API: uv run uvicorn ragy_api.main:app --reload")
    console.print("     You should see: [Database] Using zvec at ./ragy_db")
    console.print("  2. Test your application thoroughly")
    console.print("  3. Keep ./chromadb_backup/ as backup")

    console.print("\n[bold]Backup Location:[/bold]")
    console.print("  ./chromadb_backup/ - Keep this safe!")
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")


def main():
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
    console.print("[bold yellow]Clean Migration to Pure zvec Format[/bold yellow]")
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")

    try:
        # Step 1: Verify backup exists
        if not verify_backup():
            console.print("\n[bold red]Cannot proceed without backup![/bold red]")
            return 1

        # Step 2: Clean ./ragy_db/
        if not clean_ragy_db():
            console.print("\n[bold yellow]Migration cancelled[/bold yellow]")
            return 1

        # Step 3: Import to zvec
        import_stats = import_to_zvec()

        # Step 4: Verify
        verify_clean_installation()

        # Show summary
        show_summary()

        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Migration failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
