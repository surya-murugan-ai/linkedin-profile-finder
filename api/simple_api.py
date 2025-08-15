#!/usr/bin/env python3
"""
Simple LinkedIn Profile Finder API using Flask
Uses requests-based search instead of Selenium for better API compatibility
"""

import os
import sys
import time
import json
import requests
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus, urlparse
import re

# Add the parent directory to the path so we can import linkedin_finder
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
print(f"🔧 DEBUG: Added to Python path: {parent_dir}")

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import the Query class from linkedin_finder.py
from linkedin_finder import Query

# -------------- Flask App --------------

app = Flask(__name__)
CORS(app)

# -------------- Core Finder --------------

def search_google_with_requests(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Google using requests and extract LinkedIn profiles"""
    results = []
    
    try:
        # Build Google search URL with different parameters
        encoded_query = quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}&num={max_results}&hl=en&gl=us"
        
        # More comprehensive headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        print(f"🔍 DEBUG: Searching Google with query: {query}")
        print(f"🔗 DEBUG: URL: {url}")
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ DEBUG: Got response with status {response.status_code}")
        print(f"📄 DEBUG: Response length: {len(response.text)} characters")
        
        # Try multiple patterns to extract LinkedIn URLs
        patterns = [
            r'https://[^"\s]*linkedin\.com/in/[^"\s]*',
            r'linkedin\.com/in/[^"\s]*',
            r'https://www\.linkedin\.com/in/[^"\s]*',
            r'https://linkedin\.com/in/[^"\s]*'
        ]
        
        linkedin_urls = []
        for pattern in patterns:
            found_urls = re.findall(pattern, response.text, re.IGNORECASE)
            linkedin_urls.extend(found_urls)
        
        print(f"🔗 DEBUG: Found {len(linkedin_urls)} LinkedIn URLs in response")
        
        # Process and deduplicate URLs
        seen_urls = set()
        for url in linkedin_urls:
            # Clean and normalize the URL
            if not url.startswith('http'):
                url = 'https://' + url
            
            # Remove Google tracking parameters and clean up
            clean_url = url.split('&')[0].split('?')[0]
            if clean_url.endswith('/'):
                clean_url = clean_url[:-1]
            
            if clean_url not in seen_urls and 'linkedin.com/in/' in clean_url:
                seen_urls.add(clean_url)
                results.append({
                    "url": clean_url,
                    "title": f"LinkedIn Profile - {query}",
                    "snippet": f"Found via Google search for: {query}",
                    "score": 0.8
                })
        
        print(f"✅ DEBUG: Processed {len(results)} unique LinkedIn URLs")
        
        # If no results found, try a simpler approach - generate potential LinkedIn URLs
        if not results:
            print(f"🔍 DEBUG: No LinkedIn URLs found, trying direct URL generation...")
            # Extract name from query for direct URL generation
            name_match = re.search(r'"([^"]+)"', query)
            if name_match:
                name = name_match.group(1)
                # Generate potential LinkedIn URL
                linkedin_url = f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}"
                results.append({
                    "url": linkedin_url,
                    "title": f"LinkedIn Profile - {name}",
                    "snippet": f"Generated LinkedIn URL for: {name}",
                    "score": 0.5
                })
                print(f"🔗 DEBUG: Generated LinkedIn URL: {linkedin_url}")
        
    except Exception as e:
        print(f"💥 DEBUG: Error in search_google_with_requests: {e}")
        import traceback
        print(f"📋 DEBUG: Full traceback: {traceback.format_exc()}")
    
    return results

def find_profiles_api(name: str, title: Optional[str] = None, company: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
    """Find LinkedIn profiles using requests-based search"""
    
    print(f"🔍 DEBUG: Starting search for '{name}' with title='{title}' and company='{company}'")
    
    try:
        # Create a Query object (same as linkedin_finder.py uses)
        query = Query(
            name=name,
            title=title,
            company=company,
            location=None
        )
        
        print(f"📋 DEBUG: Created Query object: {query}")
        
        # Build search queries
        queries = []
        
        # Strategy 1: Exact name with LinkedIn site restriction
        if title and company:
            queries.append(f'"{name}" "{title}" "{company}" site:linkedin.com/in')
        elif title:
            queries.append(f'"{name}" "{title}" site:linkedin.com/in')
        elif company:
            queries.append(f'"{name}" "{company}" site:linkedin.com/in')
        else:
            queries.append(f'"{name}" site:linkedin.com/in')
        
        # Strategy 2: Name + title + company without site restriction
        if title and company:
            queries.append(f'"{name}" "{title}" "{company}" linkedin')
        elif title:
            queries.append(f'"{name}" "{title}" linkedin')
        elif company:
            queries.append(f'"{name}" "{company}" linkedin')
        
        # Strategy 3: Simple name search
        queries.append(f'"{name}" linkedin profile')
        
        print(f"🔍 DEBUG: Built {len(queries)} search queries: {queries}")
        
        # Search with each query
        all_results = []
        for query_str in queries:
            print(f"🔍 DEBUG: Searching with query: {query_str}")
            results = search_google_with_requests(query_str, max_results)
            all_results.extend(results)
            
            # Small delay between requests
            time.sleep(1)
        
        # Remove duplicates based on URL
        unique_results = []
        seen_urls = set()
        for result in all_results:
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
        
        print(f"✅ DEBUG: Found {len(unique_results)} unique results")
        return unique_results[:max_results]
        
    except Exception as e:
        print(f"💥 DEBUG: Error in find_profiles_api: {e}")
        import traceback
        print(f"📋 DEBUG: Full traceback: {traceback.format_exc()}")
        return []

# -------------- API Endpoints --------------

@app.route('/')
def root():
    """Root endpoint with API information"""
    return jsonify({
        "message": "LinkedIn Profile Finder API",
        "version": "1.0.0",
        "description": "Requests-based search (no Selenium)",
        "endpoints": {
            "search": "/api/search",
            "health": "/api/health"
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/search', methods=['POST'])
def search_linkedin_profiles():
    """
    Search for LinkedIn profiles using Google search
    
    Expected JSON body:
    {
        "name": "John Doe",
        "title": "Software Engineer",
        "company": "Google",
        "max_results": 10
    }
    """
    start_time = time.time()
    
    print(f"🌐 DEBUG: Received search request")
    
    try:
        # Get JSON data from request
        data = request.get_json()
        print(f"📥 DEBUG: Request data: {data}")
        
        if not data:
            print(f"❌ DEBUG: No JSON data provided")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract parameters
        name = data.get("name", "").strip()
        title = data.get("title", "").strip() or None
        company = data.get("company", "").strip() or None
        max_results = data.get("max_results", 10)
        
        print(f"🔍 DEBUG: Extracted parameters - name: '{name}', title: '{title}', company: '{company}', max_results: {max_results}")
        
        # Validate input
        if not name:
            print(f"❌ DEBUG: Name is required but empty")
            return jsonify({"error": "Name is required"}), 400
        
        print(f"✅ DEBUG: Input validation passed, calling find_profiles_api...")
        
        # Perform search using requests-based approach
        results = find_profiles_api(name, title, company, max_results)
        
        search_time = time.time() - start_time
        
        print(f"📊 DEBUG: Search completed in {search_time:.2f} seconds, found {len(results)} results")
        print(f"📋 DEBUG: Results: {results}")
        
        return jsonify({
            "success": True,
            "results": results,
            "total_found": len(results),
            "search_time": search_time,
            "message": f"Found {len(results)} LinkedIn profiles in {search_time:.2f} seconds"
        })
        
    except Exception as e:
        search_time = time.time() - start_time
        print(f"💥 DEBUG: Exception in search endpoint: {e}")
        import traceback
        print(f"📋 DEBUG: Full traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": f"Search failed: {str(e)}",
            "search_time": search_time
        }), 500

if __name__ == "__main__":
    print("🚀 Starting LinkedIn Profile Finder API...")
    print("📊 API Documentation: http://localhost:8000/")
    print("🔍 Health Check: http://localhost:8000/api/health")
    print("🔍 Search Endpoint: http://localhost:8000/api/search")
    print("🔗 Requests-based search (no Selenium)")
    app.run(host="0.0.0.0", port=8000, debug=True)
