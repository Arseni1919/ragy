from conn_emb_ollama.client import get_embedding

print("Testing Ollama embedding client...")

text = "Python programming"
print(f"✓ Input text: '{text}'")

embedding = get_embedding(text)
print(f"✓ Embedding generated")
print(f"✓ Dimensions: {len(embedding)}")
print(f"✓ First 5 values: {embedding[:5]}")
print(f"✓ Data type: {type(embedding)}")

print("\n✅ All tests passed!")
