import os
from dotenv import load_dotenv
import ollama

load_dotenv()

MODEL = os.getenv("OLLAMA_EMB_MODEL", "nomic-embed-text")

def get_embedding(text: str) -> list[float]:
    try:
        response = ollama.embeddings(model=MODEL, prompt=text)
        return response["embedding"]
    except Exception as e:
        raise RuntimeError(
            f"Failed to get embedding. Ensure Ollama is running and model '{MODEL}' is pulled.\n"
            f"Install: https://ollama.ai/download\n"
            f"Pull model: ollama pull {MODEL}\n"
            f"Error: {e}"
        )
