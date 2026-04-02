from conn_llm.client import generate_response

query = "what collections do I have in my db?"
print(f"Query: {query}")

response, messages = generate_response(query)
print(f"Response: {response}")
