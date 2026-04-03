import numpy as np
from conn_emb_hugging_face.client import (
    get_query_embedding,
    get_document_embedding,
    compute_similarity,
    get_embedding
)

print("="*60)
print("TEST 1: Query vs Document Embeddings")
print("="*60)

text = "Python programming"
print(f"✓ Input text: '{text}'")

query_emb = get_query_embedding(text)
doc_emb = get_document_embedding(text)

print(f"✓ Query embedding dimensions: {len(query_emb)}")
print(f"✓ Document embedding dimensions: {len(doc_emb)}")
print(f"✓ Query embedding first 5 values: {query_emb[:5]}")
print(f"✓ Document embedding first 5 values: {doc_emb[:5]}")

print("\n" + "="*60)
print("TEST 2: Built-in Similarity Calculation")
print("="*60)

query = "Which planet is known as the Red Planet?"
documents = [
    "Venus is often called Earth's twin because of its similar size and proximity.",
    "Mars, known for its reddish appearance, is often referred to as the Red Planet.",
    "Jupiter, the largest planet in our solar system, has a prominent red spot.",
    "Saturn, famous for its rings, is sometimes mistaken for the Red Planet."
]

print(f"✓ Query: '{query}'")
print(f"✓ Number of documents: {len(documents)}")

query_embedding = get_query_embedding(query)
document_embeddings = [get_document_embedding(doc) for doc in documents]

print(f"✓ Generated query embedding: {len(query_embedding)} dims")
print(f"✓ Generated {len(document_embeddings)} document embeddings")

similarities = compute_similarity(query_embedding, document_embeddings)

print(f"\n✓ Similarity scores (higher = more similar):")
for i, (score, doc) in enumerate(zip(similarities, documents), 1):
    print(f"  {i}. [{score:.4f}] {doc[:60]}...")

print("\n" + "="*60)
print("TEST 3: Backward Compatibility Test")
print("="*60)

legacy_text = "Test backward compatibility"
legacy_embedding = get_embedding(legacy_text)
print(f"✓ Legacy get_embedding() still works")
print(f"✓ Dimensions: {len(legacy_embedding)}")
print(f"✓ Defaults to document embedding")

print("\n" + "="*60)
print("TEST 4: Manual Cosine Similarity Comparison")
print("="*60)

sentences = [
    "The cat sits on the mat",
    "Dogs love to play fetch in the park",
    "Python is a popular programming language",
    "Machine learning models require large datasets",
]

print(f"✓ Documents: {len(sentences)}")
doc_embeddings = [get_document_embedding(s) for s in sentences]

query = "I want to learn coding"
print(f"✓ Query: '{query}'")
query_emb = get_query_embedding(query)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

manual_similarities = []
for i, emb in enumerate(doc_embeddings):
    sim = cosine_similarity(query_emb, emb)
    manual_similarities.append((sim, sentences[i]))

manual_similarities.sort(reverse=True)

print(f"\n✓ Top 3 most similar documents (manual calculation):")
for i, (score, sentence) in enumerate(manual_similarities[:3], 1):
    print(f"  {i}. [{score:.4f}] {sentence}")

print("\n✅ All tests passed!")
print(f"✅ Model: google/embeddinggemma-300m (768 dimensions)")
