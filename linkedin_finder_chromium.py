#!/usr/bin/env python3
"""
LinkedIn Profile URL Finder - Chromium/Chrome Version

This version uses Selenium with Chrome or Chromium browser to search Google for LinkedIn profiles.
Supports both Chrome and Chromium, runs headless by default.

Features:
- Real browser automation (no blocking issues)
- Google search for LinkedIn profiles
- Smart matching based on name, title, and company
- Handles multiple search strategies
- Respectful rate limiting
- Headless operation (no visible browser window)
- Chrome and Chromium support

Usage:
    python linkedin_finder_chromium.py --name "John Doe" --title "Software Engineer" --company "Google"
    python linkedin_finder_chromium.py --csv leads.csv --out results.json
"""

import os
import re
import csv
import json
import time
import argparse
import random
from urllib.parse import quote_plus, urlparse, unquote
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
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

# -------------- Models --------------

@dataclass
class Query:
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None

@dataclass
class Result:
    url: str
    title: Optional[str]
    snippet: Optional[str]
    score: float

# -------------- Utilities --------------

def clean_text(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def is_profile_url(url: str) -> bool:
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
    """Setup Chrome/Chromium driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Add user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Run headless by default (no visible browser window)
    chrome_options.add_argument("--headless")
    
    # Additional headless options for better compatibility
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Windows Chrome/Chromium paths
    import platform
    if platform.system() == "Windows":
        # Common Windows Chrome/Chromium installation paths
        windows_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
            r"C:\Program Files\Chromium\Application\chrome.exe",
            r"C:\Program Files (x86)\Chromium\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Chromium\Application\chrome.exe".format(os.getenv('USERNAME', '')),
        ]
        
        # Try Windows paths first
        for path in windows_paths:
            if os.path.exists(path):
                try:
                    print(f"Trying to use Chrome at: {path}")
                    chrome_options.binary_location = path
                    
                    # Try with ChromeDriverManager first
                    try:
                        service = Service(ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                        print(f"✅ Successfully connected to Chrome at {path}")
                        break
                    except Exception as e:
                        print(f"ChromeDriverManager failed: {e}")
                        
                        # Try without service specification
                        try:
                            driver = webdriver.Chrome(options=chrome_options)
                            print(f"✅ Successfully connected to Chrome at {path} (direct)")
                            break
                        except Exception as e2:
                            print(f"Direct connection failed: {e2}")
                            continue
                except Exception as e:
                    print(f"Failed to use Chrome at {path}: {e}")
                    continue
        
        # If no Windows path worked, try the original approach
        if 'driver' not in locals():
            browser_executables = [
                "chrome",      # Google Chrome
                "chromium",    # Chromium
                "chromium-browser",  # Ubuntu/Debian Chromium
                "google-chrome",     # Linux Chrome
                "google-chrome-stable"  # Some Linux distributions
            ]
            
            for browser_exec in browser_executables:
                try:
                    print(f"Trying to use {browser_exec}...")
                    
                    # Set the browser executable path
                    chrome_options.binary_location = browser_exec
                    
                    # Try with ChromeDriverManager first
                    try:
                        service = Service(ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                        print(f"✅ Successfully connected to {browser_exec}")
                        break
                    except Exception as e:
                        print(f"ChromeDriverManager failed with {browser_exec}: {e}")
                        
                        # Try without service specification
                        try:
                            driver = webdriver.Chrome(options=chrome_options)
                            print(f"✅ Successfully connected to {browser_exec} (direct)")
                            break
                        except Exception as e2:
                            print(f"Direct connection failed with {browser_exec}: {e2}")
                            continue
                            
                except Exception as e:
                    print(f"Failed to use {browser_exec}: {e}")
                    continue
    else:
        # Non-Windows systems - use original approach
        browser_executables = [
            "chrome",      # Google Chrome
            "chromium",    # Chromium
            "chromium-browser",  # Ubuntu/Debian Chromium
            "google-chrome",     # Linux Chrome
            "google-chrome-stable"  # Some Linux distributions
        ]
        
        for browser_exec in browser_executables:
            try:
                print(f"Trying to use {browser_exec}...")
                
                # Set the browser executable path
                chrome_options.binary_location = browser_exec
                
                # Try with ChromeDriverManager first
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    print(f"✅ Successfully connected to {browser_exec}")
                    break
                except Exception as e:
                    print(f"ChromeDriverManager failed with {browser_exec}: {e}")
                    
                    # Try without service specification
                    try:
                        driver = webdriver.Chrome(options=chrome_options)
                        print(f"✅ Successfully connected to {browser_exec} (direct)")
                        break
                    except Exception as e2:
                        print(f"Direct connection failed with {browser_exec}: {e2}")
                        continue
                        
            except Exception as e:
                print(f"Failed to use {browser_exec}: {e}")
                continue
    
    if 'driver' not in locals() or driver is None:
        print("\n" + "="*60)
        print("BROWSER NOT FOUND!")
        print("="*60)
        print("Neither Chrome nor Chromium was found on your system.")
        print("\nTo fix this issue, please install one of the following:")
        print("\n1. Google Chrome:")
        print("   - Download from: https://www.google.com/chrome/")
        print("   - Or install via package manager:")
        print("     Ubuntu/Debian: sudo apt install google-chrome-stable")
        print("     CentOS/RHEL: sudo yum install google-chrome-stable")
        print("     macOS: brew install --cask google-chrome")
        print("\n2. Chromium (recommended for automation):")
        print("   - Ubuntu/Debian: sudo apt install chromium-browser")
        print("   - CentOS/RHEL: sudo yum install chromium")
        print("   - macOS: brew install chromium")
        print("   - Windows: Download from https://www.chromium.org/getting-involved/download-chromium")
        print("\n3. After installation, restart your terminal/command prompt")
        print("4. Run this script again")
        print("\nAlternative solutions:")
        print("- Manually download ChromeDriver from https://chromedriver.chromium.org/downloads")
        print("  and place it in your PATH")
        print("="*60)
        raise Exception("No compatible browser found. Please install Chrome or Chromium and try again.")
    
    # Remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

# -------------- Search Functions --------------

def build_search_queries(q: Query) -> List[str]:
    """Build multiple search queries to try different strategies"""
    queries = []
    
    # Strategy 1: Exact name with LinkedIn site restriction
    if q.title and q.company:
        queries.append(f'"{q.name}" "{q.title}" "{q.company}" site:linkedin.com/in')
    elif q.title:
        queries.append(f'"{q.name}" "{q.title}" site:linkedin.com/in')
    elif q.company:
        queries.append(f'"{q.name}" "{q.company}" site:linkedin.com/in')
    else:
        queries.append(f'"{q.name}" site:linkedin.com/in')
    
    # Strategy 2: Name + title + company without site restriction
    if q.title and q.company:
        queries.append(f'"{q.name}" "{q.title}" "{q.company}" linkedin')
    elif q.title:
        queries.append(f'"{q.name}" "{q.title}" linkedin')
    elif q.company:
        queries.append(f'"{q.name}" "{q.company}" linkedin')
    
    # Strategy 3: Simple name search
    queries.append(f'"{q.name}" linkedin profile')
    
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
                    print(f"    Found {len(filtered_elements)} results with selector: {selector}")
                    break
            except:
                continue
        
        if not result_elements:
            print(f"    No search results found with any selector")
            return results
        
        # Extract LinkedIn profiles from results
        for i, element in enumerate(result_elements[:max_results]):
            try:
                # Debug: print all links in this result
                all_links = element.find_elements(By.CSS_SELECTOR, "a")
                for link in all_links[:3]:  # Check first 3 links
                    href = link.get_attribute("href")
                    if href:
                        print(f"    Result {i+1} link: {href[:100]}...")
                
                url = extract_linkedin_url_from_google_result(element)
                if url:
                    title = extract_title_from_google_result(element)
                    snippet = extract_snippet_from_google_result(element)
                    
                    results.append({
                        "url": url,
                        "title": title,
                        "snippet": snippet
                    })
                    print(f"    Found LinkedIn profile: {url}")
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error during Google search: {e}")
    
    return results

# -------------- Scoring and Matching --------------

def score_result(res: Dict[str, Any], q: Query) -> float:
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
    name_tokens = [t.lower() for t in q.name.split() if t]
    name_text = title + " " + snippet
    
    # Exact name match
    if q.name.lower() in name_text:
        score += 3.0
    # Partial name match
    elif all(token in name_text for token in name_tokens):
        score += 2.0
    elif any(token in name_text for token in name_tokens):
        score += 1.0
    
    # Title matching
    if q.title:
        title_lower = q.title.lower()
        if title_lower in title or title_lower in snippet:
            score += 1.5
    
    # Company matching
    if q.company:
        company_lower = q.company.lower()
        if company_lower in title or company_lower in snippet:
            score += 1.5
    
    # Location matching
    if q.location:
        location_lower = q.location.lower()
        if location_lower in title or location_lower in snippet:
            score += 1.0
    
    # Penalize company pages
    if "/company/" in url:
        score -= 2.0
    
    return score

# -------------- Core Finder --------------

def find_profiles(q: Query, max_results_per_query: int = 10) -> List[Result]:
    """Find LinkedIn profiles using Google search with Selenium"""
    all_hits = []
    
    # Setup browser
    driver = setup_driver()
    
    try:
        # Build search queries
        queries = build_search_queries(q)
        
        for i, query in enumerate(queries):
            print(f"  Search {i+1}/{len(queries)}: {query}")
            
            # Search Google
            hits = search_google_with_selenium(driver, query, max_results_per_query)
            
            if hits:
                all_hits.extend(hits)
                print(f"    Found {len(hits)} LinkedIn profiles")
                
                # If we found good results, we can stop
                if len(hits) >= 3:
                    break
            else:
                print(f"    No LinkedIn profiles found")
            
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
        score = score_result(hit, q)
        if score > 0:  # Only include valid LinkedIn profiles
            results.append(Result(
                url=hit["url"],
                title=hit.get("title"),
                snippet=hit.get("snippet"),
                score=score
            ))
    
    # Sort by score (descending)
    results.sort(key=lambda r: r.score, reverse=True)
    
    return results

# -------------- IO Helpers --------------

def load_queries_from_csv(path: str) -> List[Query]:
    out = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append(Query(
                name=row.get("name", "").strip(),
                title=(row.get("title") or "").strip() or None,
                company=(row.get("company") or "").strip() or None,
                location=(row.get("location") or "").strip() or None,
            ))
    return out

def save_results(path: str, data: List[Dict[str, Any]]) -> None:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".json", ""):
        with open(path or "results.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif ext == ".csv":
        if not data:
            headers = ["name", "title", "company", "location", "url", "result_title", "snippet", "score"]
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
            return
        headers = list(data[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    else:
        raise ValueError("Unsupported output format. Use .json or .csv")

# -------------- CLI --------------

def main():
    ap = argparse.ArgumentParser(description="Find LinkedIn profile URLs via Google search using Chrome/Chromium browser automation.")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--name", help="Full name, e.g., 'John Doe'")
    group.add_argument("--csv", help="CSV file with headers: name,title,company,location")

    ap.add_argument("--title", help="Current title (optional), e.g., 'Software Engineer'")
    ap.add_argument("--company", help="Company name (optional), e.g., 'Google'")
    ap.add_argument("--location", help="Location (optional), e.g., 'San Francisco'")
    ap.add_argument("--max-results", type=int, default=10, help="Max results per search query")
    ap.add_argument("--out", default="results.json", help="Output file (.json or .csv)")
    ap.add_argument("--sleep", type=float, default=2.0, help="Delay between queries (seconds)")

    args = ap.parse_args()

    queries: List[Query]
    if args.csv:
        queries = load_queries_from_csv(args.csv)
    else:
        queries = [Query(name=args.name, title=args.title, company=args.company, location=args.location)]

    all_output_rows: List[Dict[str, Any]] = []

    for qi, q in enumerate(queries, 1):
        print(f"[{qi}/{len(queries)}] Searching: {q.name} | {q.title or ''} | {q.company or ''} | {q.location or ''}")
        
        results = find_profiles(q, max_results_per_query=args.max_results)

        if results:
            best = results[0]
            print(f"  Best match: {best.url} (score: {best.score:.1f})")
            print(f"  Found {len(results)} total profiles")
        else:
            print("  No LinkedIn profiles found")

        for r in results:
            all_output_rows.append({
                "name": q.name,
                "title": q.title or "",
                "company": q.company or "",
                "location": q.location or "",
                "url": r.url,
                "result_title": r.title or "",
                "snippet": r.snippet or "",
                "score": r.score,
            })

        # Polite pause between queries
        if qi < len(queries):
            time.sleep(args.sleep + random.uniform(0.5, 1.5))

    save_results(args.out, all_output_rows)
    print(f"Saved {len(all_output_rows)} rows -> {args.out}")

if __name__ == "__main__":
    main()
