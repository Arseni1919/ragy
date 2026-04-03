from conn_db.client import client as db_client
from conn_emb_hugging_face.client import MODEL, model
from conn_tavily.client import client as tavily_client


def get_db_client():
    return db_client


def get_embedding_model():
    return model, MODEL


def get_tavily_client():
    return tavily_client
