# LinkedIn Profile Finder - Chrome Extension

A Chrome extension that finds LinkedIn profile URLs using Google search with smart matching and confidence scoring.

## Features

-  **Real Google Search** - Uses actual Google search results
-  **Smart Matching** - Scores results based on name, title, and company
-  **Confidence Scoring** - Shows how well each result matches
-  **Export Options** - Export results as JSON or CSV
-  **Beautiful UI** - Modern, responsive design
-  **Form Persistence** - Remembers your last search

## Installation

1. **Download the extension files** to a folder on your computer
2. **Open Chrome** and go to `chrome://extensions/`
3. **Enable "Developer mode"** (toggle in top right)
4. **Click "Load unpacked"** and select the extension folder
5. **Pin the extension** to your toolbar for easy access

## Usage

1. **Click the extension icon** in your Chrome toolbar
2. **Fill in the search form:**
   - Full Name (required)
   - Job Title (optional)
   - Company (optional)
   - Location (optional)
   - Max Results (5-20)
3. **Click "Search Profiles"**
4. **View results** with confidence scores
5. **Export results** as JSON or CSV

## How It Works

The extension:
1. Creates multiple search strategies
2. Searches Google for LinkedIn profiles
3. Extracts and scores results
4. Returns ranked profiles with confidence scores

## Score Explanation

- **8.0+**: Excellent match (exact name + title + company)
- **5.0-7.9**: Good match (name + partial title/company)
- **2.0-4.9**: Fair match (name only or partial matches)
- **< 2.0**: Poor match (likely not the right person)

## Privacy & Ethics

- Only searches publicly available information
- Respectful rate limiting to avoid overwhelming servers
- No LinkedIn login required
- Designed to respect website terms of service

## Troubleshooting

- **No results found**: Try different search terms or check if the person has a public LinkedIn profile
- **Extension not working**: Make sure you have the latest version of Chrome
- **Slow performance**: Reduce the max results number

## Support

For issues or questions, check the main project repository.

---

**Made with  for legitimate business use**
