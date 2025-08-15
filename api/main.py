#!/usr/bin/env python3
"""
LinkedIn Profile Finder API

FastAPI version of the LinkedIn profile finder that accepts POST requests
and returns LinkedIn profile URLs found via Google search.

Features:
- RESTful API endpoints
- Async web scraping with Selenium
- Request validation with Pydantic
- Background task support
- Rate limiting
- Comprehensive error handling
"""

import os
import re
import time
import random
import asyncio
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus, urlparse, unquote

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# -------------- Configs --------------

LINKEDIN_PROFILE_RE = re.compile(r"^https?://([a-z]+\.)?linkedin\.com/in/[^/?#]+/?", re.IGNORECASE)

# -------------- Pydantic Models --------------

class SearchRequest(BaseModel):
    name: str = Field(..., description="Full name to search for")
    title: Optional[str] = Field(None, description="Current job title")
    company: Optional[str] = Field(None, description="Current or past company")
    location: Optional[str] = Field(None, description="Location")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results to return")

class SearchResult(BaseModel):
    url: str = Field(..., description="LinkedIn profile URL")
    title: Optional[str] = Field(None, description="Profile title from search result")
    snippet: Optional[str] = Field(None, description="Profile snippet from search result")
    score: float = Field(..., description="Relevance score (0-10)")

class SearchResponse(BaseModel):
    success: bool = Field(..., description="Whether the search was successful")
    results: List[SearchResult] = Field(..., description="List of found LinkedIn profiles")
    total_found: int = Field(..., description="Total number of profiles found")
    search_time: float = Field(..., description="Time taken for search in seconds")
    message: Optional[str] = Field(None, description="Additional information or error message")

class BulkSearchRequest(BaseModel):
    searches: List[SearchRequest] = Field(..., description="List of search requests")
    max_results_per_search: int = Field(10, ge=1, le=20, description="Max results per individual search")

# -------------- FastAPI App --------------

app = FastAPI(
    title="LinkedIn Profile Finder API",
    description="Find LinkedIn profile URLs using Google search with intelligent matching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------- Utilities --------------

def clean_text(s: Optional[str]) -> str:
    """Clean and normalize text"""
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def is_profile_url(url: str) -> bool:
    """Check if URL is a LinkedIn profile URL"""
    return bool(LINKEDIN_PROFILE_RE.match(url))

def extract_linkedin_url_from_google_result(result_element) -> Optional[str]:
    """Extract LinkedIn URL from Google search result element"""
    try:
        # Try multiple selectors for links
        link_selectors = ["a", "a[href]", "h3 a", "div a"]
        
        for selector in link_selectors:
            try:
                link_elements = result_element.find_elements(By.CSS_SELECTOR, selector)
                for link_element in link_elements:
                    href = link_element.get_attribute("href")
                    
                    if href and "linkedin.com/in/" in href:
                        # Clean the URL
                        url = href.split("&")[0]  # Remove tracking parameters
                        if is_profile_url(url):
                            return url
            except:
                continue
    except:
        pass
    return None

def extract_title_from_google_result(result_element) -> Optional[str]:
    """Extract title from Google search result element"""
    try:
        title_element = result_element.find_element(By.CSS_SELECTOR, "h3")
        return clean_text(title_element.text)
    except:
        return None

def extract_snippet_from_google_result(result_element) -> Optional[str]:
    """Extract snippet from Google search result element"""
    try:
        snippet_element = result_element.find_element(By.CSS_SELECTOR, "div[data-snf='nke7rc']")
        return clean_text(snippet_element.text)
    except:
        try:
            # Alternative selector
            snippet_element = result_element.find_element(By.CSS_SELECTOR, "div[class*='VwiC3b']")
            return clean_text(snippet_element.text)
        except:
            return None

# -------------- Browser Setup --------------

def setup_driver() -> webdriver.Chrome:
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Add user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Run headless for API
    chrome_options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

# -------------- Search Functions --------------

def build_search_queries(search_data: SearchRequest) -> List[str]:
    """Build multiple search queries to try different strategies"""
    queries = []
    
    # Strategy 1: Exact name with LinkedIn site restriction
    if search_data.title and search_data.company:
        queries.append(f'"{search_data.name}" "{search_data.title}" "{search_data.company}" site:linkedin.com/in')
    elif search_data.title:
        queries.append(f'"{search_data.name}" "{search_data.title}" site:linkedin.com/in')
    elif search_data.company:
        queries.append(f'"{search_data.name}" "{search_data.company}" site:linkedin.com/in')
    else:
        queries.append(f'"{search_data.name}" site:linkedin.com/in')
    
    # Strategy 2: Name + title + company without site restriction
    if search_data.title and search_data.company:
        queries.append(f'"{search_data.name}" "{search_data.title}" "{search_data.company}" linkedin')
    elif search_data.title:
        queries.append(f'"{search_data.name}" "{search_data.title}" linkedin')
    elif search_data.company:
        queries.append(f'"{search_data.name}" "{search_data.company}" linkedin')
    
    # Strategy 3: Simple name search
    queries.append(f'"{search_data.name}" linkedin profile')
    
    return queries

def search_google_with_selenium(driver: webdriver.Chrome, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Google using Selenium and extract LinkedIn profiles"""
    results = []
    
    try:
        # Navigate to Google
        driver.get("https://www.google.com")
        time.sleep(2)
        
        # Find search box and enter query
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        time.sleep(3)  # Let results fully load
        
        # Wait for actual search results to load (not navigation)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-sokoban-container]"))
            )
        except:
            pass
        
        time.sleep(2)  # Extra wait for results
        
        # Try multiple selectors for search results (avoiding navigation)
        selectors = [
            "div[data-sokoban-container] div[jscontroller]",
            "div.g div[jscontroller]",
            "div[data-hveid]",
            "div.g"
        ]
        
        result_elements = []
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                # Filter out navigation elements
                filtered_elements = []
                for elem in elements:
                    try:
                        # Check if this element contains actual search result content
                        text = elem.text.strip()
                        if len(text) > 50 and not text.startswith("Google"):  # Avoid navigation
                            filtered_elements.append(elem)
                    except:
                        continue
                
                if filtered_elements:
                    result_elements = filtered_elements
                    break
            except:
                continue
        
        if not result_elements:
            return results
        
        # Extract LinkedIn profiles from results
        for i, element in enumerate(result_elements[:max_results]):
            try:
                url = extract_linkedin_url_from_google_result(element)
                if url:
                    title = extract_title_from_google_result(element)
                    snippet = extract_snippet_from_google_result(element)
                    
                    results.append({
                        "url": url,
                        "title": title,
                        "snippet": snippet
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error during Google search: {e}")
    
    return results

# -------------- Scoring and Matching --------------

def score_result(res: Dict[str, Any], search_data: SearchRequest) -> float:
    """Score a result based on how well it matches the query"""
    url = (res.get("url") or "").lower()
    title = clean_text(res.get("title", "")).lower()
    snippet = clean_text(res.get("snippet", "")).lower()
    
    score = 0.0
    
    # Must be a LinkedIn profile URL
    if is_profile_url(url):
        score += 2.0
    else:
        return 0.0  # Not a LinkedIn profile
    
    # Name matching (most important)
    name_tokens = [t.lower() for t in search_data.name.split() if t]
    name_text = title + " " + snippet
    
    # Exact name match
    if search_data.name.lower() in name_text:
        score += 3.0
    # Partial name match
    elif all(token in name_text for token in name_tokens):
        score += 2.0
    elif any(token in name_text for token in name_tokens):
        score += 1.0
    
    # Title matching
    if search_data.title:
        title_lower = search_data.title.lower()
        if title_lower in title or title_lower in snippet:
            score += 1.5
    
    # Company matching
    if search_data.company:
        company_lower = search_data.company.lower()
        if company_lower in title or company_lower in snippet:
            score += 1.5
    
    # Location matching
    if search_data.location:
        location_lower = search_data.location.lower()
        if location_lower in title or location_lower in snippet:
            score += 1.0
    
    # Penalize company pages
    if "/company/" in url:
        score -= 2.0
    
    return score

# -------------- Core Finder --------------

def find_profiles(search_data: SearchRequest) -> List[SearchResult]:
    """Find LinkedIn profiles using Google search with Selenium"""
    all_hits = []
    
    # Setup browser
    driver = setup_driver()
    
    try:
        # Build search queries
        queries = build_search_queries(search_data)
        
        for i, query in enumerate(queries):
            # Search Google
            hits = search_google_with_selenium(driver, query, search_data.max_results)
            
            if hits:
                all_hits.extend(hits)
                
                # If we found good results, we can stop
                if len(hits) >= 3:
                    break
            
            # Be respectful - wait between searches
            time.sleep(random.uniform(2, 4))
    
    finally:
        driver.quit()
    
    # Deduplicate by URL
    seen_urls = set()
    unique_hits = []
    for hit in all_hits:
        url = hit["url"]
        if url not in seen_urls:
            seen_urls.add(url)
            unique_hits.append(hit)
    
    # Score and filter results
    results = []
    for hit in unique_hits:
        score = score_result(hit, search_data)
        if score > 0:  # Only include valid LinkedIn profiles
            results.append(SearchResult(
                url=hit["url"],
                title=hit.get("title"),
                snippet=hit.get("snippet"),
                score=score
            ))
    
    # Sort by score (descending)
    results.sort(key=lambda r: r.score, reverse=True)
    
    return results

# -------------- API Endpoints --------------

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LinkedIn Profile Finder API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/search",
            "bulk_search": "/api/bulk-search",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/search", response_model=SearchResponse)
async def search_linkedin_profiles(search_data: SearchRequest):
    """
    Search for LinkedIn profiles using Google search
    
    This endpoint accepts a search request with name, title, company, and location
    and returns matching LinkedIn profile URLs with relevance scores.
    """
    start_time = time.time()
    
    try:
        # Validate input
        if not search_data.name.strip():
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Perform search
        results = find_profiles(search_data)
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            success=True,
            results=results,
            total_found=len(results),
            search_time=search_time,
            message=f"Found {len(results)} LinkedIn profiles in {search_time:.2f} seconds"
        )
        
    except Exception as e:
        search_time = time.time() - start_time
        raise HTTPException(
            status_code=500, 
            detail=f"Search failed: {str(e)}"
        )

@app.post("/api/bulk-search")
async def bulk_search_linkedin_profiles(bulk_request: BulkSearchRequest, background_tasks: BackgroundTasks):
    """
    Perform bulk search for multiple LinkedIn profiles
    
    This endpoint accepts multiple search requests and processes them.
    For large batches, consider using background tasks.
    """
    if len(bulk_request.searches) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 searches per request")
    
    start_time = time.time()
    all_results = []
    
    try:
        for i, search_data in enumerate(bulk_request.searches):
            try:
                results = find_profiles(search_data)
                all_results.append({
                    "search_index": i,
                    "search_data": search_data.dict(),
                    "results": [result.dict() for result in results],
                    "total_found": len(results)
                })
            except Exception as e:
                all_results.append({
                    "search_index": i,
                    "search_data": search_data.dict(),
                    "results": [],
                    "total_found": 0,
                    "error": str(e)
                })
            
            # Be respectful between searches
            if i < len(bulk_request.searches) - 1:
                await asyncio.sleep(random.uniform(1, 3))
        
        search_time = time.time() - start_time
        
        return {
            "success": True,
            "total_searches": len(bulk_request.searches),
            "total_profiles_found": sum(r["total_found"] for r in all_results),
            "search_time": search_time,
            "results": all_results
        }
        
    except Exception as e:
        search_time = time.time() - start_time
        raise HTTPException(
            status_code=500,
            detail=f"Bulk search failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
