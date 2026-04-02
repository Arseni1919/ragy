from conn_llm.client import generate_response

print("Multi-turn conversation test\n")

print("Turn 1:")
query1 = "What collections do I have?"
print(f"User: {query1}")
response, messages = generate_response(query1)
print(f"Assistant: {response}\n")

print("Turn 2:")
query2 = "Tell me more about the first one"
print(f"User: {query2}")
response, messages = generate_response(query2, messages)
print(f"Assistant: {response}\n")

print("Turn 3:")
query3 = "What year is it today?"
print(f"User: {query3}")
response, messages = generate_response(query3, messages)
print(f"Assistant: {response}")
