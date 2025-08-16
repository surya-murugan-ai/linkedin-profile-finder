#!/usr/bin/env python3
"""
LinkedIn Profile Finder API

FastAPI wrapper for the LinkedIn profile finder functionality.
Provides REST endpoints to search for LinkedIn profiles.

Usage:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import json
import time
from datetime import datetime

# Add parent directory to path to import linkedin_finder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_finder import Query, Result, find_profiles

# -------------- Pydantic Models --------------

class SearchRequest(BaseModel):
    name: str = Field(..., description="Full name to search for", example="John Doe")
    title: Optional[str] = Field(None, description="Current job title", example="Software Engineer")
    company: Optional[str] = Field(None, description="Company name", example="Google")
    location: Optional[str] = Field(None, description="Location", example="San Francisco")
    max_results: int = Field(10, description="Maximum results per search query", ge=1, le=50)

class BatchSearchRequest(BaseModel):
    queries: List[SearchRequest] = Field(..., description="List of search queries")
    max_results: int = Field(10, description="Maximum results per search query", ge=1, le=50)

class SearchResult(BaseModel):
    url: str = Field(..., description="LinkedIn profile URL")
    title: Optional[str] = Field(None, description="Profile title from search result")
    snippet: Optional[str] = Field(None, description="Profile snippet from search result")
    score: float = Field(..., description="Match score (higher is better)")

class SearchResponse(BaseModel):
    query: SearchRequest
    results: List[SearchResult]
    total_results: int
    search_time: float
    timestamp: str

class BatchSearchResponse(BaseModel):
    searches: List[SearchResponse]
    total_searches: int
    total_profiles_found: int
    batch_time: float
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# -------------- FastAPI App --------------

app = FastAPI(
    title="LinkedIn Profile Finder API",
    description="API for finding LinkedIn profile URLs using Google search",
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

# -------------- API Endpoints --------------

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/search", response_model=SearchResponse)
async def search_profile(request: SearchRequest):
    """
    Search for a single LinkedIn profile
    
    This endpoint searches for LinkedIn profiles using Google search with the provided criteria.
    Returns the best matching profiles sorted by relevance score.
    """
    try:
        start_time = time.time()
        
        # Convert to internal Query object
        query = Query(
            name=request.name,
            title=request.title,
            company=request.company,
            location=request.location
        )
        
        # Perform search
        results = find_profiles(query, max_results_per_query=request.max_results)
        
        # Convert results to response format
        search_results = [
            SearchResult(
                url=result.url,
                title=result.title,
                snippet=result.snippet,
                score=result.score
            )
            for result in results
        ]
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            query=request,
            results=search_results,
            total_results=len(search_results),
            search_time=round(search_time, 2),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/batch", response_model=BatchSearchResponse)
async def search_profiles_batch(request: BatchSearchRequest):
    """
    Search for multiple LinkedIn profiles in batch
    
    This endpoint processes multiple search queries and returns results for each.
    Useful for bulk processing of leads.
    """
    try:
        start_time = time.time()
        searches = []
        total_profiles = 0
        
        for i, search_request in enumerate(request.queries):
            try:
                # Convert to internal Query object
                query = Query(
                    name=search_request.name,
                    title=search_request.title,
                    company=search_request.company,
                    location=search_request.location
                )
                
                # Perform search
                results = find_profiles(query, max_results_per_query=request.max_results)
                
                # Convert results to response format
                search_results = [
                    SearchResult(
                        url=result.url,
                        title=result.title,
                        snippet=result.snippet,
                        score=result.score
                    )
                    for result in results
                ]
                
                searches.append(SearchResponse(
                    query=search_request,
                    results=search_results,
                    total_results=len(search_results),
                    search_time=0,  # Individual search time not tracked in batch
                    timestamp=datetime.now().isoformat()
                ))
                
                total_profiles += len(search_results)
                
                # Add delay between searches to be respectful
                if i < len(request.queries) - 1:
                    time.sleep(2)
                    
            except Exception as e:
                # Continue with other searches even if one fails
                searches.append(SearchResponse(
                    query=search_request,
                    results=[],
                    total_results=0,
                    search_time=0,
                    timestamp=datetime.now().isoformat()
                ))
        
        batch_time = time.time() - start_time
        
        return BatchSearchResponse(
            searches=searches,
            total_searches=len(searches),
            total_profiles_found=total_profiles,
            batch_time=round(batch_time, 2),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch search failed: {str(e)}")

@app.get("/docs")
async def get_docs():
    """API documentation endpoint"""
    return {"message": "Visit /docs for interactive API documentation"}

# -------------- Error Handlers --------------

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "detail": "The requested endpoint does not exist"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": "An unexpected error occurred"}

# -------------- Main --------------

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
