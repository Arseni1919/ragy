#!/usr/bin/env python3
"""Test script for yfinance integration"""

from ragy_cli.api_client import APIClient

def test_search_yfinance():
    print("\n=== Testing yfinance Search API ===")
    client = APIClient()

    try:
        result = client.search_yfinance("apple stock", max_results=3)
        print(f"✓ Query: {result['query']}")
        print(f"✓ Results: {len(result['results'])} found")

        for i, item in enumerate(result['results'], 1):
            print(f"\n  Result {i}:")
            print(f"    Title: {item.get('title', 'N/A')[:60]}")
            print(f"    URL: {item.get('url', 'N/A')[:80]}")
            content = item.get('raw_content', '')
            if 'Related Tickers' in content:
                print(f"    Has tickers: Yes")

        print("\n✓ yfinance search API test PASSED")
        return True
    except Exception as e:
        print(f"\n✗ yfinance search API test FAILED: {e}")
        return False


def test_create_job_with_source():
    print("\n=== Testing Job Creation with Source ===")
    client = APIClient()

    try:
        result = client.create_scheduled_job(
            query="nvidia ai",
            collection="test_nvidia_col",
            interval_type="day",
            interval_amount=1,
            source="yfinance"
        )

        print(f"✓ Job ID: {result['job_id']}")
        print(f"✓ Source: {result['source']}")
        print(f"✓ Query: {result['query']}")
        print(f"✓ Collection: {result['collection_name']}")

        print("\n✓ Job creation with source test PASSED")
        return result['job_id']
    except Exception as e:
        print(f"\n✗ Job creation test FAILED: {e}")
        return None


def test_get_jobs_with_source():
    print("\n=== Testing Get Jobs (Verify Source Field) ===")
    client = APIClient()

    try:
        result = client.get_user_jobs()
        jobs = result.get('jobs', [])

        print(f"✓ Total jobs: {len(jobs)}")

        yfinance_jobs = [j for j in jobs if j.get('source') == 'yfinance']
        print(f"✓ yfinance jobs: {len(yfinance_jobs)}")

        for job in yfinance_jobs:
            print(f"\n  Job {job['job_id']}:")
            print(f"    Query: {job['query']}")
            print(f"    Source: {job['source']}")
            print(f"    Collection: {job['collection_name']}")

        print("\n✓ Get jobs with source test PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Get jobs test FAILED: {e}")
        return False


def test_cleanup(job_id):
    print("\n=== Cleanup: Deleting Test Job ===")
    client = APIClient()

    try:
        result = client.delete_scheduled_job(job_id)
        print(f"✓ {result['message']}")
        print("\n✓ Cleanup PASSED")
        return True
    except Exception as e:
        print(f"\n✗ Cleanup FAILED: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("YFINANCE INTEGRATION TEST SUITE")
    print("=" * 60)

    # Test 1: Search yfinance
    test1 = test_search_yfinance()

    # Test 2: Create job with yfinance source
    job_id = test_create_job_with_source()

    # Test 3: Get jobs and verify source field
    test3 = test_get_jobs_with_source()

    # Cleanup
    if job_id:
        test_cleanup(job_id)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Search yfinance API: {'✓ PASSED' if test1 else '✗ FAILED'}")
    print(f"Create job with source: {'✓ PASSED' if job_id else '✗ FAILED'}")
    print(f"Get jobs with source: {'✓ PASSED' if test3 else '✗ FAILED'}")
    print("=" * 60)

    if test1 and job_id and test3:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
