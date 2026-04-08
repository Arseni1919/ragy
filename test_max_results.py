#!/usr/bin/env python3
"""Test max_results parameter in yfinance search"""

from ragy_cli.api_client import APIClient

client = APIClient()

print("Testing max_results parameter fix\n")
print("=" * 60)

# Test 1: max_results=1
print("\nTest 1: max_results=1")
result = client.search_yfinance("apple", max_results=1)
print(f"Query: {result['query']}")
print(f"Results returned: {len(result['results'])}")
print(f"Expected: 1")
print(f"Status: {'✓ PASS' if len(result['results']) == 1 else '✗ FAIL'}")

# Test 2: max_results=3
print("\nTest 2: max_results=3")
result = client.search_yfinance("nvidia", max_results=3)
print(f"Query: {result['query']}")
print(f"Results returned: {len(result['results'])}")
print(f"Expected: 3")
print(f"Status: {'✓ PASS' if len(result['results']) == 3 else '✗ FAIL'}")

# Test 3: max_results=5 (default)
print("\nTest 3: max_results=5 (default)")
result = client.search_yfinance("tesla", max_results=5)
print(f"Query: {result['query']}")
print(f"Results returned: {len(result['results'])}")
print(f"Expected: 5 or less (depends on yfinance data)")
print(f"Status: {'✓ PASS' if len(result['results']) <= 5 else '✗ FAIL'}")

print("\n" + "=" * 60)
print("All tests completed!")
