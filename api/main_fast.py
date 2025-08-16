#!/usr/bin/env python3
"""
FastAPI application for LinkedIn Profile Finder - FAST VERSION
Optimized for speed with reduced search strategies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from linkedin_finder_fast import Query, Result, find_profiles

# -------------- API Models --------------

class SearchRequest(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    max_results: Optional[int] = 10

class SearchResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    total_found: int
    message: str

class BatchSearchRequest(BaseModel):
    queries: List[SearchRequest]

class BatchSearchResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    total_found: int
    message: str

class HealthResponse(BaseModel):
    status: str
    message: str

# -------------- FastAPI App --------------

app = FastAPI(
    title="LinkedIn Profile Finder API - Fast Version",
    description="API for finding LinkedIn profile URLs using Google search with Chromium/Chrome headless browser - OPTIMIZED for speed",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------- API Endpoints --------------

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="LinkedIn Profile Finder API is running - Fast Version"
    )

@app.post("/search", response_model=SearchResponse)
async def search_profile(request: SearchRequest):
    """Search for a single LinkedIn profile"""
    try:
        print(f"🔍 Searching for: {request.name} | {request.title or ''} | {request.company or ''}")
        
        # Create query object
        query = Query(
            name=request.name,
            title=request.title,
            company=request.company,
            location=request.location
        )
        
        # Find profiles
        results = find_profiles(query, max_results_per_query=request.max_results or 10)
        
        # Convert results to dict format
        result_dicts = []
        for result in results:
            result_dicts.append({
                "url": result.url,
                "title": result.title,
                "snippet": result.snippet,
                "score": result.score
            })
        
        return SearchResponse(
            success=True,
            results=result_dicts,
            total_found=len(result_dicts),
            message=f"Found {len(result_dicts)} LinkedIn profiles for {request.name}"
        )
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/batch", response_model=BatchSearchResponse)
async def search_profiles_batch(request: BatchSearchRequest):
    """Search for multiple LinkedIn profiles in batch"""
    try:
        print(f"�� Batch search for {len(request.queries)} profiles")
        
        all_results = []
        
        for i, query_request in enumerate(request.queries, 1):
            print(f"  [{i}/{len(request.queries)}] Searching: {query_request.name}")
            
            # Create query object
            query = Query(
                name=query_request.name,
                title=query_request.title,
                company=query_request.company,
                location=query_request.location
            )
            
            # Find profiles
            results = find_profiles(query, max_results_per_query=query_request.max_results or 10)
            
            # Convert results to dict format
            for result in results:
                all_results.append({
                    "name": query_request.name,
                    "title": query_request.title,
                    "company": query_request.company,
                    "location": query_request.location,
                    "url": result.url,
                    "result_title": result.title,
                    "snippet": result.snippet,
                    "score": result.score
                })
        
        return BatchSearchResponse(
            success=True,
            results=all_results,
            total_found=len(all_results),
            message=f"Found {len(all_results)} LinkedIn profiles across {len(request.queries)} searches"
        )
        
    except Exception as e:
        print(f"❌ Error during batch search: {e}")
        raise HTTPException(status_code=500, detail=f"Batch search failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "api.main_fast:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
