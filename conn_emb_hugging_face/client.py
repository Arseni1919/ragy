import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# New model: google/embeddinggemma-300m (768 dimensions)
MODEL = os.getenv("HF_EMB_MODEL", "google/embeddinggemma-300m")
HF_TOKEN = os.getenv("HF_TOKEN")

model = SentenceTransformer(MODEL, token=HF_TOKEN)

# Old model (commented out for reference)
# MODEL_OLD = "sentence-transformers/all-MiniLM-L6-v2"  # 384 dimensions
# model_old = SentenceTransformer(MODEL_OLD)

def get_query_embedding(text: str) -> list[float]:
    """Get embedding for search queries using encode_query method"""
    embedding = model.encode_query(text)
    return embedding.tolist()

def get_document_embedding(text: str) -> list[float]:
    """Get embedding for documents using encode_document method"""
    embedding = model.encode_document(text)
    return embedding.tolist()

def get_embedding(text: str) -> list[float]:
    """
    Backward compatibility: defaults to document embedding.
    DEPRECATED: Use get_query_embedding() or get_document_embedding() explicitly.
    """
    return get_document_embedding(text)

def compute_similarity(query_embedding: list[float], document_embeddings: list[list[float]]) -> list[float]:
    """
    Compute similarity scores using model's built-in similarity method.
    Returns similarity scores (higher = more similar).
    """
    import torch
    query_tensor = torch.tensor(query_embedding).unsqueeze(0)
    doc_tensor = torch.tensor(document_embeddings)
    similarities = model.similarity(query_tensor, doc_tensor)
    return similarities[0].tolist()
