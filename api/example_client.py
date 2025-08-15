#!/usr/bin/env python3
"""
Example client for LinkedIn Profile Finder API

This script demonstrates how to use the API to search for LinkedIn profiles.
"""

import requests
import json
import time
from typing import Dict, List, Optional

class LinkedInProfileFinderAPI:
    """Client for LinkedIn Profile Finder API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def search_profile(self, name: str, title: Optional[str] = None, 
                      company: Optional[str] = None, location: Optional[str] = None,
                      max_results: int = 10) -> Dict:
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
        search_data = {
            "name": name,
            "max_results": max_results
        }
        
        if title:
            search_data["title"] = title
        if company:
            search_data["company"] = company
        if location:
            search_data["location"] = location
        
        try:
            response = requests.post(f"{self.base_url}/api/search", json=search_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Search failed: {e}")
            return {"success": False, "error": str(e)}
    
    def bulk_search(self, searches: List[Dict], max_results_per_search: int = 10) -> Dict:
        """
        Perform bulk search for multiple profiles
        
        Args:
            searches: List of search dictionaries with 'name', 'title', 'company', 'location'
            max_results_per_search: Maximum results per search
            
        Returns:
            API response as dictionary
        """
        bulk_data = {
            "searches": searches,
            "max_results_per_search": max_results_per_search
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/bulk-search", json=bulk_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Bulk search failed: {e}")
            return {"success": False, "error": str(e)}
    
    def print_results(self, results: Dict):
        """Pretty print search results"""
        if not results.get("success"):
            print(f"❌ Search failed: {results.get('error', 'Unknown error')}")
            return
        
        print(f"\n✅ Search completed in {results.get('search_time', 0):.2f} seconds")
        print(f"📊 Found {results.get('total_found', 0)} LinkedIn profiles")
        
        for i, result in enumerate(results.get('results', []), 1):
            print(f"\n{i}. {result.get('title', 'No title')}")
            print(f"   URL: {result.get('url')}")
            print(f"   Score: {result.get('score', 0):.1f}")
            if result.get('snippet'):
                print(f"   Snippet: {result.get('snippet')[:100]}...")

def main():
    """Example usage of the API client"""
    
    # Initialize API client
    api = LinkedInProfileFinderAPI()
    
    # Check if API is running
    print("🔍 LinkedIn Profile Finder API Client")
    print("=" * 50)
    
    if not api.health_check():
        print("❌ API is not running. Please start the API first:")
        print("   cd api && python start.py")
        return
    
    print("✅ API is running and healthy!")
    
    # Example 1: Single search
    print("\n" + "=" * 50)
    print("Example 1: Single Profile Search")
    print("=" * 50)
    
    result = api.search_profile(
        name="John Doe",
        title="Software Engineer",
        company="Google",
        max_results=5
    )
    
    api.print_results(result)
    
    # Example 2: Bulk search
    print("\n" + "=" * 50)
    print("Example 2: Bulk Profile Search")
    print("=" * 50)
    
    searches = [
        {
            "name": "John Doe",
            "title": "Software Engineer",
            "company": "Google"
        },
        {
            "name": "Jane Smith",
            "title": "Product Manager",
            "company": "Microsoft"
        },
        {
            "name": "Bob Johnson",
            "title": "Data Scientist",
            "company": "Amazon"
        }
    ]
    
    bulk_result = api.bulk_search(searches, max_results_per_search=3)
    
    if bulk_result.get("success"):
        print(f"\n✅ Bulk search completed in {bulk_result.get('search_time', 0):.2f} seconds")
        print(f"📊 Processed {bulk_result.get('total_searches', 0)} searches")
        print(f"🎯 Found {bulk_result.get('total_profiles_found', 0)} total profiles")
        
        for i, search_result in enumerate(bulk_result.get('results', []), 1):
            search_data = search_result.get('search_data', {})
            print(f"\n{i}. Search for: {search_data.get('name')} at {search_data.get('company', 'Unknown')}")
            print(f"   Found: {search_result.get('total_found', 0)} profiles")
            
            if search_result.get('error'):
                print(f"   Error: {search_result.get('error')}")
    else:
        print(f"❌ Bulk search failed: {bulk_result.get('error', 'Unknown error')}")
    
    # Example 3: Interactive search
    print("\n" + "=" * 50)
    print("Example 3: Interactive Search")
    print("=" * 50)
    
    while True:
        print("\nEnter search details (or 'quit' to exit):")
        name = input("Name: ").strip()
        
        if name.lower() == 'quit':
            break
        
        if not name:
            print("Name is required!")
            continue
        
        title = input("Title (optional): ").strip() or None
        company = input("Company (optional): ").strip() or None
        location = input("Location (optional): ").strip() or None
        
        print(f"\n🔍 Searching for: {name}")
        if title:
            print(f"   Title: {title}")
        if company:
            print(f"   Company: {company}")
        if location:
            print(f"   Location: {location}")
        
        result = api.search_profile(name, title, company, location)
        api.print_results(result)

if __name__ == "__main__":
    main()

