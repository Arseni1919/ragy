from conn_llm.client import generate_response

print("=" * 60)
print("Interactive Chat with Memory")
print("=" * 60)
print("Type your messages below. Type 'exit' or 'quit' to end.\n")

messages = None

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        print("\nGoodbye!")
        break

    if not user_input:
        continue

    print("Assistant: ", end="", flush=True)
    response, messages = generate_response(user_input, messages)
    print(response)
    print()
