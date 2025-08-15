#!/usr/bin/env python3
"""
Test script for LinkedIn Profile Finder API
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_single_search():
    """Test single search endpoint"""
    print("\nTesting single search...")
    
    search_data = {
        "name": "John Doe",
        "title": "Software Engineer",
        "company": "Google",
        "max_results": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/search", json=search_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single search successful")
            print(f"   Found {result['total_found']} profiles")
            print(f"   Search time: {result['search_time']:.2f} seconds")
            
            if result['results']:
                print("   Top result:")
                top_result = result['results'][0]
                print(f"     URL: {top_result['url']}")
                print(f"     Score: {top_result['score']}")
                print(f"     Title: {top_result['title']}")
            
            return True
        else:
            print(f"❌ Single search failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Single search error: {e}")
        return False

def test_bulk_search():
    """Test bulk search endpoint"""
    print("\nTesting bulk search...")
    
    bulk_data = {
        "searches": [
            {
                "name": "John Doe",
                "title": "Software Engineer",
                "company": "Google"
            },
            {
                "name": "Jane Smith",
                "title": "Product Manager",
                "company": "Microsoft"
            }
        ],
        "max_results_per_search": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/bulk-search", json=bulk_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Bulk search successful")
            print(f"   Total searches: {result['total_searches']}")
            print(f"   Total profiles found: {result['total_profiles_found']}")
            print(f"   Search time: {result['search_time']:.2f} seconds")
            
            return True
        else:
            print(f"❌ Bulk search failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Bulk search error: {e}")
        return False

def test_invalid_request():
    """Test invalid request handling"""
    print("\nTesting invalid request...")
    
    # Test with missing name
    invalid_data = {
        "title": "Software Engineer",
        "company": "Google"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/search", json=invalid_data)
        
        if response.status_code == 422:  # Validation error
            print("✅ Invalid request properly rejected")
            return True
        else:
            print(f"❌ Invalid request not properly handled: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid request test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 LinkedIn Profile Finder API Tests")
    print("=" * 50)
    
    # Wait a moment for API to be ready
    print("Waiting for API to be ready...")
    time.sleep(2)
    
    tests = [
        test_health,
        test_single_search,
        test_bulk_search,
        test_invalid_request
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API logs for details.")

if __name__ == "__main__":
    main()

