import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL = os.getenv("HF_EMB_MODEL", "all-MiniLM-L6-v2")
model = SentenceTransformer(MODEL)

def get_embedding(text: str) -> list[float]:
    embedding = model.encode(text)
    return embedding.tolist()
