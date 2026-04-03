from conn_tavily.client import client

print("Testing Tavily client...")

response = client.search("Python programming")
print(f"✓ Search completed")
print(f"✓ Query: {response.get('query', 'N/A')}")
print(f"✓ Results count: {len(response.get('results', []))}")

if response.get('results'):
    first_result = response['results'][0]
    print(f"✓ First result title: {first_result.get('title', 'N/A')}")
    print("---")
    print(f"✓ First result URL: {first_result.get('url', 'N/A')}")
    print("---")
    print(f"✓ First result score: {first_result.get('score', 'N/A')}")
    print("---")
    print(f"✓ First result content: {first_result.get('content', 'N/A')}")
    print("---")
    print(f"✓ First result raw content: {first_result.get('raw_content', 'N/A')}")
    print("---")
    print(dir(first_result))
    print(first_result.keys())

print("\n✅ All tests passed!")
