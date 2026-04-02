import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./ragy_db")
Path(DB_PATH).mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=DB_PATH)
