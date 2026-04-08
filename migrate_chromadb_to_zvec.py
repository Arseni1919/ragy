#!/usr/bin/env python3
"""
Migrate all data from ChromaDB to zvec

This script:
1. Exports all collections from ChromaDB to JSON backups
2. Imports all data into zvec
3. Verifies data integrity
4. Provides detailed progress reporting
"""

import os
import sys
import json
import importlib
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()


def export_from_chromadb():
    """Export all data from ChromaDB to JSON files"""
    console.print("\n[bold cyan]Step 1: Exporting from ChromaDB[/bold cyan]")
    console.print("=" * 60)

    # Set environment to use ChromaDB
    os.environ['DB_PROVIDER'] = 'chromadb'

    # Force reload of modules
    if 'conn_db.client' in sys.modules:
        del sys.modules['conn_db.client']

    from conn_db.client import client

    # Get all collections
    collections = client.list_collections()
    console.print(f"\nFound [bold]{len(collections)}[/bold] collections to export")

    # Create backup directory
    backup_dir = Path("./chromadb_backup")
    backup_dir.mkdir(exist_ok=True)

    export_stats = {
        'timestamp': datetime.now().isoformat(),
        'total_collections': len(collections),
        'total_documents': 0,
        'collections': []
    }

    # Export each collection
    for col_info in tqdm(collections, desc="Exporting collections"):
        col_name = col_info.name

        try:
            col = client.get_collection(col_name)
            count = col.count()

            if count == 0:
                console.print(f"  [yellow]Skipping empty collection:[/yellow] {col_name}")
                export_stats['collections'].append({
                    'name': col_name,
                    'count': 0,
                    'status': 'skipped_empty'
                })
                continue

            # Get all data - ChromaDB get() without parameters returns all
            console.print(f"\n  Exporting [cyan]{col_name}[/cyan] ({count} documents)...")

            data = col.get(include=["documents", "embeddings", "metadatas"])

            # Prepare export data
            export_data = {
                "name": col_name,
                "count": count,
                "ids": data['ids'],
                "documents": data['documents'],
                "embeddings": [[float(x) for x in emb] for emb in data['embeddings']],
                "metadatas": data['metadatas']
            }

            # Save to JSON
            filename = backup_dir / f"{col_name}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f)

            console.print(f"    ✓ Exported to {filename}")

            export_stats['total_documents'] += count
            export_stats['collections'].append({
                'name': col_name,
                'count': count,
                'status': 'exported'
            })

        except Exception as e:
            console.print(f"  [red]Error exporting {col_name}:[/red] {e}")
            export_stats['collections'].append({
                'name': col_name,
                'count': 0,
                'status': f'error: {e}'
            })

    # Save export stats
    with open(backup_dir / '_export_stats.json', 'w') as f:
        json.dump(export_stats, f, indent=2)

    console.print(f"\n[bold green]✓ Export complete![/bold green]")
    console.print(f"  Total collections: {export_stats['total_collections']}")
    console.print(f"  Total documents: {export_stats['total_documents']:,}")
    console.print(f"  Backup location: {backup_dir.absolute()}")

    return export_stats


def import_to_zvec():
    """Import all JSON files to zvec"""
    console.print("\n[bold cyan]Step 2: Importing to zvec[/bold cyan]")
    console.print("=" * 60)

    # Set environment to use zvec
    os.environ['DB_PROVIDER'] = 'zvec'

    # Force reload of modules
    for mod in ['conn_db.client', 'conn_zvec.client']:
        if mod in sys.modules:
            del sys.modules[mod]

    from conn_db.client import client

    # Find backup files
    backup_dir = Path("./chromadb_backup")
    backup_files = list(backup_dir.glob("*.json"))
    backup_files = [f for f in backup_files if not f.name.startswith('_')]

    console.print(f"\nFound [bold]{len(backup_files)}[/bold] backup files to import")

    import_stats = {
        'timestamp': datetime.now().isoformat(),
        'total_collections': len(backup_files),
        'total_documents': 0,
        'collections': []
    }

    # Import each collection
    for backup_file in tqdm(backup_files, desc="Importing collections"):
        col_name = backup_file.stem

        try:
            # Load backup data
            with open(backup_file, 'r') as f:
                data = json.load(f)

            if data['count'] == 0:
                console.print(f"  [yellow]Skipping empty collection:[/yellow] {col_name}")
                import_stats['collections'].append({
                    'name': col_name,
                    'count': 0,
                    'status': 'skipped_empty'
                })
                continue

            console.print(f"\n  Importing [cyan]{col_name}[/cyan] ({data['count']} documents)...")

            # Create collection
            col = client.get_or_create_collection(col_name)

            # Import in batches (zvec may have limits)
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
                    console.print(f"    • Imported {end}/{total} documents...")

            # Verify count
            final_count = col.count()
            console.print(f"    ✓ Import complete: {final_count} documents")

            if final_count != data['count']:
                console.print(f"    [yellow]Warning: Count mismatch! Expected {data['count']}, got {final_count}[/yellow]")

            import_stats['total_documents'] += final_count
            import_stats['collections'].append({
                'name': col_name,
                'expected': data['count'],
                'imported': final_count,
                'status': 'success' if final_count == data['count'] else 'count_mismatch'
            })

        except Exception as e:
            console.print(f"  [red]Error importing {col_name}:[/red] {e}")
            import_stats['collections'].append({
                'name': col_name,
                'status': f'error: {e}'
            })
            import traceback
            traceback.print_exc()

    # Save import stats
    with open(backup_dir / '_import_stats.json', 'w') as f:
        json.dump(import_stats, f, indent=2)

    console.print(f"\n[bold green]✓ Import complete![/bold green]")
    console.print(f"  Total collections: {import_stats['total_collections']}")
    console.print(f"  Total documents: {import_stats['total_documents']:,}")

    return import_stats


def verify_migration(export_stats, import_stats):
    """Verify migration was successful"""
    console.print("\n[bold cyan]Step 3: Verification[/bold cyan]")
    console.print("=" * 60)

    # Create comparison table
    table = Table(title="Migration Verification")
    table.add_column("Collection", style="cyan")
    table.add_column("ChromaDB", justify="right", style="yellow")
    table.add_column("zvec", justify="right", style="green")
    table.add_column("Status", style="bold")

    export_dict = {c['name']: c['count'] for c in export_stats['collections'] if c['status'] == 'exported'}
    import_dict = {c['name']: c.get('imported', 0) for c in import_stats['collections'] if c['status'] in ['success', 'count_mismatch']}

    all_collections = set(export_dict.keys()) | set(import_dict.keys())

    mismatches = []
    for col_name in sorted(all_collections):
        export_count = export_dict.get(col_name, 0)
        import_count = import_dict.get(col_name, 0)

        if export_count == import_count and export_count > 0:
            status = "✓"
            style = "green"
        elif export_count == 0:
            status = "Empty"
            style = "dim"
        else:
            status = "✗ Mismatch"
            style = "red"
            mismatches.append((col_name, export_count, import_count))

        table.add_row(
            col_name,
            str(export_count),
            str(import_count),
            status,
            style=style
        )

    console.print(table)

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Collections exported: {len(export_dict)}")
    console.print(f"  Collections imported: {len(import_dict)}")
    console.print(f"  Total documents (ChromaDB): {export_stats['total_documents']:,}")
    console.print(f"  Total documents (zvec): {import_stats['total_documents']:,}")

    if mismatches:
        console.print(f"\n[yellow]⚠ Found {len(mismatches)} mismatches:[/yellow]")
        for name, exp, imp in mismatches:
            console.print(f"    {name}: {exp} → {imp}")
        return False
    else:
        console.print(f"\n[bold green]✅ All data migrated successfully![/bold green]")
        return True


def test_vector_search():
    """Test vector search on migrated data"""
    console.print("\n[bold cyan]Step 4: Testing Vector Search[/bold cyan]")
    console.print("=" * 60)

    os.environ['DB_PROVIDER'] = 'zvec'

    # Force reload
    for mod in ['conn_db.client', 'conn_zvec.client']:
        if mod in sys.modules:
            del sys.modules[mod]

    from conn_db.client import client

    # Find a non-empty collection
    collections = client.list_collections()

    for col_info in collections:
        col = client.get_collection(col_info.name)
        if col.count() > 0:
            console.print(f"\nTesting vector search on [cyan]{col_info.name}[/cyan]...")

            # Get a sample document
            sample = col.get(limit=1, include=["embeddings", "documents", "metadatas"])

            if sample['embeddings']:
                # Query with the same embedding
                results = col.query(
                    query_embeddings=[sample['embeddings'][0]],
                    n_results=3,
                    include=["documents", "metadatas", "distances"]
                )

                # Verify nested list format
                assert isinstance(results['ids'], list), "ids should be list"
                assert isinstance(results['ids'][0], list), "ids[0] should be list (nested)"
                assert len(results['ids']) == 1, "Should have 1 query result"

                console.print(f"  ✓ Found {len(results['ids'][0])} results")
                console.print(f"  ✓ Nested list format verified")
                console.print(f"  ✓ Top result distance: {results['distances'][0][0]:.4f}")

                console.print(f"\n[bold green]✓ Vector search working correctly![/bold green]")
                return True

    console.print("[yellow]⚠ No non-empty collections found for testing[/yellow]")
    return False


def main():
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
    console.print("[bold yellow]ChromaDB to zvec Data Migration[/bold yellow]")
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")

    try:
        # Step 1: Export from ChromaDB
        export_stats = export_from_chromadb()

        # Step 2: Import to zvec
        import_stats = import_to_zvec()

        # Step 3: Verify
        success = verify_migration(export_stats, import_stats)

        # Step 4: Test vector search
        if success:
            test_vector_search()

        console.print("\n[bold yellow]" + "=" * 60 + "[/bold yellow]")
        if success:
            console.print("[bold green]✅ MIGRATION COMPLETE AND VERIFIED![/bold green]")
            console.print("\n[bold cyan]Next steps:[/bold cyan]")
            console.print("  1. Test your application with zvec")
            console.print("  2. Backup ChromaDB data is in ./chromadb_backup/")
            console.print("  3. You can delete ./ragy_db/ (ChromaDB data) once verified")
        else:
            console.print("[bold red]⚠ MIGRATION COMPLETED WITH ISSUES[/bold red]")
            console.print("\n[bold cyan]Review the mismatches above and:[/bold cyan]")
            console.print("  1. Check ./chromadb_backup/ for exported data")
            console.print("  2. You can re-run specific collections if needed")
        console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")

        return 0 if success else 1

    except Exception as e:
        console.print(f"\n[bold red]❌ Migration failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
