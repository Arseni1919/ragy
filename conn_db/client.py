import os
from dotenv import load_dotenv

load_dotenv()

DB_PROVIDER = os.getenv("DB_PROVIDER", "chromadb")
DB_PATH = os.getenv("DB_PATH", "./ragy_db")

if DB_PROVIDER == "zvec":
    print(f"[Database] Using zvec at {DB_PATH}")
    from conn_zvec.client import client

elif DB_PROVIDER == "chromadb":
    print(f"[Database] Using ChromaDB at {DB_PATH}")
    import chromadb
    from pathlib import Path

    Path(DB_PATH).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_PATH)

else:
    raise ValueError(f"Unknown DB_PROVIDER: {DB_PROVIDER}. Must be 'chromadb' or 'zvec'")

# Export client - all other code imports from here
__all__ = ["client"]
