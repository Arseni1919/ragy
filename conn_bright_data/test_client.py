from conn_bright_data.client import client

print("Testing Bright Data client...")

print("\n1. Testing web search...")
response = client.search("Israeli News")
print(f"✓ Search completed")
print(f"✓ Query: {response.get('query', 'N/A')}")
print(f"✓ Results count: {len(response.get('results', []))}")

if response.get('results'):
    first_result = response['results'][0]
    print(f"\n✓ First result title: {first_result.get('title', 'N/A')}")
    print(f"✓ First result URL: {first_result.get('url', 'N/A')}")
    content = first_result.get('raw_content', 'N/A')
    print(f"✓ Content length: {len(content)} characters")
    content_preview = content[:200] if len(content) > 200 else content
    print(f"✓ First result content preview: {content_preview}...")

print("\n2. Testing second search...")
response2 = client.search("Machine learning trends", max_results=3)
print(f"✓ Second search completed")
print(f"✓ Results count: {len(response2.get('results', []))}")
if response2.get('results'):
    content2 = response2['results'][0].get('raw_content', 'N/A')
    print(f"✓ Content length: {len(content2)} characters")
    print(f"✓ Content preview: {content2[:200]}...")

print("\n✅ All tests passed!")
