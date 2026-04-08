#!/usr/bin/env python3
"""
Clean Migration to zvec Format (Automatic)

This script:
1. Verifies backup exists
2. Removes ALL data from ./ragy_db/
3. Creates fresh zvec database
4. Verifies installation
"""

import os
import sys
import json
import shutil
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
from rich.table import Table

console = Console()


def verify_backup():
    """Verify backup exists"""
    console.print("\n[bold cyan]Step 1: Verifying Backup[/bold cyan]")
    console.print("=" * 60)

    backup_dir = Path("./chromadb_backup")
    if not backup_dir.exists():
        console.print("[bold red]❌ Backup not found![/bold red]")
        return False

    backup_files = list(backup_dir.glob("*.json"))
    backup_files = [f for f in backup_files if not f.name.startswith('_')]

    stats_file = backup_dir / "_export_stats.json"
    if stats_file.exists():
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        console.print(f"[green]✓[/green] Backup verified!")
        console.print(f"  Collections: {stats['total_collections']}")
        console.print(f"  Documents: {stats['total_documents']:,}")
    else:
        console.print(f"[green]✓[/green] Backup found: {len(backup_files)} files")

    return True


def clean_ragy_db():
    """Remove all data from ./ragy_db/"""
    console.print("\n[bold cyan]Step 2: Cleaning ./ragy_db/[/bold cyan]")
    console.print("=" * 60)

    ragy_db = Path("./ragy_db")
    if not ragy_db.exists():
        console.print("[yellow]Directory doesn't exist, will be created[/yellow]")
        return True

    items = list(ragy_db.iterdir())
    console.print(f"\nDeleting {len(items)} items from ./ragy_db/...")

    for item in tqdm(items, desc="Removing"):
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        except Exception as e:
            console.print(f"[yellow]Warning: {item.name}: {e}[/yellow]")

    console.print("[bold green]✓[/bold green] ./ragy_db/ cleaned")
    return True


def import_to_zvec():
    """Import backup to fresh zvec"""
    console.print("\n[bold cyan]Step 3: Creating Fresh zvec Database[/bold cyan]")
    console.print("=" * 60)

    os.environ['DB_PROVIDER'] = 'zvec'
    os.environ['DB_PATH'] = './ragy_db'

    for mod in ['conn_db.client', 'conn_zvec.client']:
        if mod in sys.modules:
            del sys.modules[mod]

    from conn_db.client import client

    backup_dir = Path("./chromadb_backup")
    backup_files = list(backup_dir.glob("*.json"))
    backup_files = [f for f in backup_files if not f.name.startswith('_')]

    console.print(f"\nImporting {len(backup_files)} collections...")

    total_docs = 0

    for backup_file in tqdm(backup_files, desc="Importing"):
        col_name = backup_file.stem

        try:
            with open(backup_file, 'r') as f:
                data = json.load(f)

            if data['count'] == 0:
                continue

            col = client.get_or_create_collection(col_name)

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

            final_count = col.count()
            total_docs += final_count

        except Exception as e:
            console.print(f"\n[red]Error: {col_name}: {e}[/red]")

    console.print(f"\n[bold green]✓[/bold green] Import complete: {total_docs:,} documents")
    return total_docs


def verify_installation():
    """Verify clean installation"""
    console.print("\n[bold cyan]Step 4: Verifying Installation[/bold cyan]")
    console.print("=" * 60)

    os.environ['DB_PROVIDER'] = 'zvec'

    for mod in ['conn_db.client', 'conn_zvec.client']:
        if mod in sys.modules:
            del sys.modules[mod]

    from conn_db.client import client

    # Check directory
    ragy_db = Path("./ragy_db")
    items = list(ragy_db.iterdir())
    zvec_dirs = [item for item in items if item.is_dir()]

    console.print(f"\n./ragy_db/ contents:")
    console.print(f"  Total items: {len(items)}")
    console.print(f"  zvec collections: {len(zvec_dirs)}")

    # List collections
    collections = client.list_collections()
    console.print(f"\nCollections accessible: {len(collections)}")

    # Count documents
    total = 0
    for col_info in collections:
        col = client.get_collection(col_info.name)
        total += col.count()

    console.print(f"Total documents: {total:,}")

    # Test search
    console.print(f"\nTesting vector search...")
    for col_info in collections[:5]:
        col = client.get_collection(col_info.name)
        if col.count() > 0:
            sample = col.get(limit=1, include=["embeddings"])
            if sample['embeddings']:
                results = col.query(
                    query_embeddings=[sample['embeddings'][0]],
                    n_results=2,
                    include=["documents", "distances"]
                )
                console.print(f"  ✓ Search working on {col_info.name}")
                console.print(f"    Nested lists: {'✓' if isinstance(results['ids'][0], list) else '✗'}")
                break

    console.print(f"\n[bold green]✓[/bold green] Verification complete!")
    return True


def main():
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
    console.print("[bold yellow]Clean Migration to Pure zvec (AUTO)[/bold yellow]")
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")

    try:
        if not verify_backup():
            return 1

        console.print("\n[bold yellow]⚠️  Will delete ./ragy_db/ and recreate with zvec[/bold yellow]")
        console.print("[dim]Backup exists in ./chromadb_backup/[/dim]")

        clean_ragy_db()
        total_docs = import_to_zvec()
        verify_installation()

        console.print("\n[bold yellow]" + "=" * 60 + "[/bold yellow]")
        console.print("[bold green]✅ CLEAN MIGRATION COMPLETE![/bold green]")
        console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")

        console.print("\n[bold]Summary:[/bold]")
        console.print("  • Old ./ragy_db/: [red]DELETED[/red]")
        console.print("  • New ./ragy_db/: [green]PURE ZVEC[/green]")
        console.print(f"  • Documents: {total_docs:,}")
        console.print("  • Backup: ./chromadb_backup/ (safe)")

        console.print("\n[bold cyan]Ready to use![/bold cyan]")
        console.print("  Start API: uv run uvicorn ragy_api.main:app --reload")
        console.print("  Should see: [Database] Using zvec at ./ragy_db")

        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
