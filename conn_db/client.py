import chromadb
from pathlib import Path

DB_PATH = "./ragy_db"
Path(DB_PATH).mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=DB_PATH)
