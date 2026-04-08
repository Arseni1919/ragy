import os
import zvec
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./ragy_db")
EMBEDDING_DIM = 768  # google/embeddinggemma-300m


class ZvecCollection:
    """Wrapper around zvec collection matching ChromaDB interface"""

    def __init__(self, zvec_collection, name: str):
        self._collection = zvec_collection
        self.name = name
        self._doc_ids = set()  # Track document IDs for count

    def add(self, ids: List[str], documents: List[str],
            embeddings: List[List[float]], metadatas: List[Dict]) -> None:
        """Add documents matching ChromaDB interface"""
        docs = []
        for doc_id, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
            # Store document text in required '_content' field
            # Extract known metadata fields, set missing ones to None
            fields_dict = {
                '_content': doc,
                'date': meta.get('date'),
                'url': meta.get('url'),
                'title': meta.get('title'),
                'query': meta.get('query'),
                'source': meta.get('source'),
                'score': meta.get('score'),
            }

            docs.append(zvec.Doc(
                id=doc_id,
                vectors={"embedding": emb},
                fields=fields_dict
            ))
            self._doc_ids.add(doc_id)

        self._collection.insert(docs)

    def get(self, ids: Optional[List[str]] = None,
            limit: Optional[int] = None,
            include: List[str] = [],
            where: Optional[Dict] = None) -> Dict:
        """
        Get documents matching ChromaDB interface.

        Note: 'where' filtering not implemented in zvec wrapper yet
        """
        if where is not None:
            raise NotImplementedError("Metadata filtering ('where') not yet implemented for zvec")

        # If specific IDs requested
        if ids:
            results = []
            for doc_id in ids:
                try:
                    fetch_result = self._collection.fetch(ids=doc_id)
                    # fetch() returns dict: {id: {doc_data}}
                    if fetch_result and doc_id in fetch_result:
                        results.append(fetch_result[doc_id])
                except:
                    pass  # Skip missing IDs
        else:
            # Get all documents by querying with random vector
            # This is a workaround since zvec doesn't have a "get all" method
            import numpy as np
            random_vec = np.random.rand(EMBEDDING_DIM).tolist()

            # Get large number of results (zvec max topk is 1024)
            max_results = limit if limit else 1024
            max_results = min(max_results, 1024)  # zvec max limit
            results = self._collection.query(
                zvec.VectorQuery("embedding", vector=random_vec),
                topk=max_results
            )

        # Apply limit if specified
        if limit and not ids:
            results = results[:limit]

        # Convert to ChromaDB format
        # Results can be either Doc objects (from query) or dicts (from fetch)
        result_ids = [r.id if hasattr(r, 'id') else r['id'] for r in results]
        result_docs = [r.field('_content') if hasattr(r, 'field') else r['fields']['_content'] for r in results]
        result_metas = []
        result_embs = []

        for r in results:
            # Extract metadata (remove _content field, exclude None values)
            fields = r.fields if hasattr(r, 'fields') else r['fields']
            meta = {k: v for k, v in fields.items()
                    if k != '_content' and v is not None}
            result_metas.append(meta)

            if 'embeddings' in include:
                vec = r.vector('embedding') if hasattr(r, 'vector') else r['vectors']['embedding']
                result_embs.append(vec)

        response = {'ids': result_ids}

        if 'documents' in include or not include:
            response['documents'] = result_docs
        if 'metadatas' in include or not include:
            response['metadatas'] = result_metas
        if 'embeddings' in include:
            response['embeddings'] = result_embs

        return response

    def query(self, query_embeddings: List[List[float]],
              n_results: int,
              include: List[str] = []) -> Dict:
        """
        Vector similarity search - CRITICAL METHOD

        MUST return ChromaDB format:
        {
            'ids': [['id1', 'id2', ...]],         # Double-nested!
            'documents': [['doc1', 'doc2', ...]],
            'metadatas': [[{meta1}, {meta2}, ...]],
            'distances': [[0.5, 0.6, ...]]
        }
        """
        query_embedding = query_embeddings[0]  # Extract first query

        zvec_results = self._collection.query(
            zvec.VectorQuery("embedding", vector=query_embedding),
            topk=n_results
        )

        # Convert zvec format to ChromaDB nested list format
        ids = [[r.id for r in zvec_results]]
        documents = [[r.field('_content') for r in zvec_results]]

        # Extract metadata (remove _content field, exclude None values)
        metadatas = [[{k: v for k, v in r.fields.items()
                      if k != '_content' and v is not None}
                      for r in zvec_results]]

        # Convert zvec scores to ChromaDB distances
        # zvec score is similarity (higher = more similar)
        # ChromaDB distance is L2 distance (lower = more similar)
        # Convert: distance = 1 / (1 + score) to maintain relative ordering
        distances = [[1.0 / (1.0 + r.score) for r in zvec_results]]

        result = {'ids': ids}

        if 'documents' in include:
            result['documents'] = documents
        if 'metadatas' in include:
            result['metadatas'] = metadatas
        if 'distances' in include:
            result['distances'] = distances

        return result

    def count(self) -> int:
        """Return total document count"""
        # Try zvec stats first
        try:
            stats = self._collection.stats
            if hasattr(stats, 'num_docs'):
                return stats.num_docs
            # Try to access stats as dict
            if isinstance(stats, dict) and 'num_docs' in stats:
                return stats['num_docs']
        except:
            pass

        # Fallback: count by querying
        try:
            # Query with random vector to get all docs (up to 1024)
            import numpy as np
            random_vec = np.random.rand(EMBEDDING_DIM).tolist()
            results = self._collection.query(
                zvec.VectorQuery("embedding", vector=random_vec),
                topk=1024
            )
            return len(results)
        except:
            # Last resort: track IDs we've added in this session
            return len(self._doc_ids)


class ZvecClient:
    """Wrapper around zvec matching ChromaDB client interface"""

    def __init__(self, path: str):
        self.path = path
        Path(path).mkdir(parents=True, exist_ok=True)
        self._collections = {}
        self._load_existing_collections()

    def get_or_create_collection(self, name: str) -> ZvecCollection:
        """Get existing or create new collection"""
        if name in self._collections:
            return self._collections[name]

        collection_path = os.path.join(self.path, name)

        # Try to open existing collection
        if os.path.exists(collection_path):
            try:
                zvec_col = zvec.open(path=collection_path)
                wrapper = ZvecCollection(zvec_col, name)
                self._collections[name] = wrapper
                return wrapper
            except:
                pass  # If open fails, create new

        # Define schema with all common metadata fields
        # zvec requires all fields to be pre-defined
        common_fields = [
            zvec.FieldSchema("_content", zvec.DataType.STRING, nullable=False),  # Document text
            zvec.FieldSchema("date", zvec.DataType.STRING, nullable=True),      # ISO date string
            zvec.FieldSchema("url", zvec.DataType.STRING, nullable=True),       # Source URL
            zvec.FieldSchema("title", zvec.DataType.STRING, nullable=True),     # Document title
            zvec.FieldSchema("query", zvec.DataType.STRING, nullable=True),     # Search query
            zvec.FieldSchema("source", zvec.DataType.STRING, nullable=True),    # Data source
            zvec.FieldSchema("score", zvec.DataType.FLOAT, nullable=True),      # Relevance score
        ]

        schema = zvec.CollectionSchema(
            name=name,
            fields=common_fields,
            vectors=zvec.VectorSchema(
                "embedding",
                zvec.DataType.VECTOR_FP32,
                EMBEDDING_DIM
            )
        )

        # Create collection
        zvec_col = zvec.create_and_open(path=collection_path, schema=schema)

        wrapper = ZvecCollection(zvec_col, name)
        self._collections[name] = wrapper
        return wrapper

    def get_collection(self, name: str) -> ZvecCollection:
        """Get existing collection or raise ValueError"""
        if name in self._collections:
            return self._collections[name]

        # Try to load from disk
        collection_path = os.path.join(self.path, name)
        if os.path.exists(collection_path):
            try:
                zvec_col = zvec.open(path=collection_path)
                wrapper = ZvecCollection(zvec_col, name)
                self._collections[name] = wrapper
                return wrapper
            except:
                pass

        raise ValueError(f"Collection {name} not found")

    def list_collections(self) -> List[Any]:
        """
        Return list of collection objects with .name attribute.
        Must match ChromaDB's return format.
        """
        class CollectionInfo:
            def __init__(self, name: str):
                self.name = name

        # Scan directory for collection folders
        collections = []
        if os.path.exists(self.path):
            for item in os.listdir(self.path):
                item_path = os.path.join(self.path, item)
                if os.path.isdir(item_path):
                    collections.append(CollectionInfo(item))

        return collections

    def delete_collection(self, name: str) -> None:
        """Delete a collection"""
        if name in self._collections:
            # Remove from cache
            del self._collections[name]

        # Delete directory
        import shutil
        collection_path = os.path.join(self.path, name)
        if os.path.exists(collection_path):
            shutil.rmtree(collection_path)

    def _load_existing_collections(self):
        """Load existing collections from disk"""
        if not os.path.exists(self.path):
            return

        for item in os.listdir(self.path):
            item_path = os.path.join(self.path, item)
            if os.path.isdir(item_path):
                # Collection directory found, add to registry
                # Don't load immediately - wait for get_collection() or get_or_create()
                pass


# Module-level client instance (matches ChromaDB pattern)
client = ZvecClient(path=DB_PATH)
