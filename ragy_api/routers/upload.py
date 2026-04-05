import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from conn_emb_hugging_face.client import get_document_embedding
from conn_db.client import client as db_client

router = APIRouter()

@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    collection_name: str = Form(...)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
    if 'content' not in df.columns or 'date' not in df.columns:
        raise HTTPException(
            status_code=400,
            detail=f"CSV must have 'content' and 'date' columns. Found: {', '.join(df.columns)}"
        )
    try:
        collection = db_client.get_or_create_collection(name=collection_name)
        existing_count = collection.count()
        uploaded = 0
        for idx, row in df.iterrows():
            content = str(row['content'])
            date = str(row['date'])
            embedding = get_document_embedding(content)
            doc_id = str(existing_count + idx)
            metadata = {"date": date}
            for col in df.columns:
                if col not in ['content', 'date']:
                    metadata[col] = str(row[col])
            collection.add(
                ids=[doc_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            uploaded += 1
        return {
            "status": "success",
            "uploaded": uploaded,
            "total_documents": collection.count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
