#!/usr/bin/env python3
"""
LinkedIn Profile Finder API Client Example

This script demonstrates how to use the LinkedIn Profile Finder API
to search for LinkedIn profiles programmatically.
"""

import requests
import json
from typing import List, Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

def search_single_profile(name: str, title: str = None, company: str = None, location: str = None, max_results: int = 10) -> Dict[str, Any]:
    """
    Search for a single LinkedIn profile
    
    Args:
        name: Full name to search for
        title: Job title (optional)
        company: Company name (optional)
        location: Location (optional)
        max_results: Maximum number of results to return
    
    Returns:
        API response as dictionary
    """
    url = f"{API_BASE_URL}/search"
    
    payload = {
        "name": name,
        "max_results": max_results
    }
    
    if title:
        payload["title"] = title
    if company:
        payload["company"] = company
    if location:
        payload["location"] = location
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

def search_multiple_profiles(queries: List[Dict[str, Any]], max_results: int = 10) -> Dict[str, Any]:
    """
    Search for multiple LinkedIn profiles in batch
    
    Args:
        queries: List of search queries, each containing name, title, company, location
        max_results: Maximum number of results per query
    
    Returns:
        API response as dictionary
    """
    url = f"{API_BASE_URL}/search/batch"
    
    payload = {
        "queries": queries,
        "max_results": max_results
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

def check_api_health() -> bool:
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"API Status: {data['status']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"API is not available: {e}")
        return False

def print_search_results(results: Dict[str, Any]):
    """Pretty print search results"""
    if not results:
        print("No results to display")
        return
    
    print(f"\n{'='*60}")
    print(f"Search Results for: {results['query']['name']}")
    print(f"Total Results: {results['total_results']}")
    print(f"Search Time: {results['search_time']}s")
    print(f"Timestamp: {results['timestamp']}")
    print(f"{'='*60}")
    
    if not results['results']:
        print("No LinkedIn profiles found.")
        return
    
    for i, result in enumerate(results['results'], 1):
        print(f"\n{i}. Profile URL: {result['url']}")
        print(f"   Score: {result['score']:.2f}")
        if result['title']:
            print(f"   Title: {result['title']}")
        if result['snippet']:
            print(f"   Snippet: {result['snippet'][:100]}...")
        print("-" * 40)

def print_batch_results(results: Dict[str, Any]):
    """Pretty print batch search results"""
    if not results:
        print("No results to display")
        return
    
    print(f"\n{'='*60}")
    print(f"Batch Search Results")
    print(f"Total Searches: {results['total_searches']}")
    print(f"Total Profiles Found: {results['total_profiles_found']}")
    print(f"Batch Time: {results['batch_time']}s")
    print(f"Timestamp: {results['timestamp']}")
    print(f"{'='*60}")
    
    for i, search in enumerate(results['searches'], 1):
        print(f"\n{i}. Search: {search['query']['name']}")
        print(f"   Results Found: {search['total_results']}")
        
        if search['results']:
            best_result = search['results'][0]
            print(f"   Best Match: {best_result['url']} (Score: {best_result['score']:.2f})")
        else:
            print("   No profiles found")
        print("-" * 40)

def main():
    """Example usage of the LinkedIn Profile Finder API"""
    
    # Check if API is running
    if not check_api_health():
        print("Please start the API server first:")
        print("uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print("LinkedIn Profile Finder API Client Example")
    print("=" * 50)
    
    # Example 1: Single profile search
    print("\n1. Single Profile Search Example")
    print("-" * 30)
    
    single_result = search_single_profile(
        name="John Doe",
        title="Software Engineer",
        company="Google",
        location="San Francisco",
        max_results=5
    )
    
    print_search_results(single_result)
    
    # Example 2: Batch search
    print("\n\n2. Batch Search Example")
    print("-" * 30)
    
    batch_queries = [
        {
            "name": "Jane Smith",
            "title": "Product Manager",
            "company": "Microsoft"
        },
        {
            "name": "Bob Johnson",
            "title": "Data Scientist",
            "company": "Amazon"
        },
        {
            "name": "Alice Brown",
            "title": "UX Designer",
            "company": "Apple"
        }
    ]
    
    batch_result = search_multiple_profiles(batch_queries, max_results=3)
    print_batch_results(batch_result)
    
    # Example 3: Save results to file
    print("\n\n3. Saving Results to File")
    print("-" * 30)
    
    if single_result:
        with open("api_search_results.json", "w") as f:
            json.dump(single_result, f, indent=2)
        print("Single search results saved to api_search_results.json")
    
    if batch_result:
        with open("api_batch_results.json", "w") as f:
            json.dump(batch_result, f, indent=2)
        print("Batch search results saved to api_batch_results.json")

if __name__ == "__main__":
    main()
