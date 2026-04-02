from conn_llm.client import generate_response

print("TEST 1: List Collections")
query = "What collections do I have in my database?"
print(f"Query: {query}")
response, _ = generate_response(query)
print(f"Response: {response}\n")

print("TEST 2: Ragy Extractor")
query = "What were the major technology developments in March 2026?"
print(f"Query: {query}")
response, _ = generate_response(query)
print(f"Response: {response}\n")

print("TEST 3: Tavily Search")
query = "What is the latest tech news today?"
print(f"Query: {query}")
response, _ = generate_response(query)
print(f"Response: {response}\n")

print("TEST 4: No Tools Needed")
query = "What is Python programming?"
print(f"Query: {query}")
response, _ = generate_response(query)
print(f"Response: {response}")
