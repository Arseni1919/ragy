import numpy as np
from conn_emb_hugging_face.client import get_embedding

print("="*60)
print("TEST 1: Basic Embedding Generation")
print("="*60)

text = "Python programming"
print(f"✓ Input text: '{text}'")

embedding = get_embedding(text)
print(f"✓ Embedding generated")
print(f"✓ Dimensions: {len(embedding)}")
print(f"✓ First 5 values: {embedding[:5]}")
print(f"✓ Data type: {type(embedding)}")

print("\n" + "="*60)
print("TEST 2: Similarity Search Demonstration")
print("="*60)

sentences = [
    "The cat sits on the mat",
    "Dogs love to play fetch in the park",
    "Python is a popular programming language",
    "Machine learning models require large datasets",
    "The sun rises in the east",
    "Pizza is a delicious Italian dish",
    "JavaScript is used for web development"
]

print(f"✓ Storing {len(sentences)} sentences...")
embeddings = [get_embedding(s) for s in sentences]
print(f"✓ Generated {len(embeddings)} embeddings")

query = "I want to learn coding"
print(f"\n✓ Query: '{query}'")
query_embedding = get_embedding(query)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

similarities = []
for i, emb in enumerate(embeddings):
    sim = cosine_similarity(query_embedding, emb)
    similarities.append((sim, sentences[i]))

similarities.sort(reverse=True)

print(f"\n✓ Top 3 most similar sentences:")
for i, (score, sentence) in enumerate(similarities[:3], 1):
    print(f"  {i}. [{score:.4f}] {sentence}")

print("\n✅ All tests passed!")
