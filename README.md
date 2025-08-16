# LinkedIn Profile Finder 🔍

A powerful Python tool that finds LinkedIn profile URLs using real browser automation, similar to Apify's LinkedIn Profile Search. This tool searches Google for LinkedIn profiles and returns accurate results with confidence scoring.

## ✨ Features

- **Real Browser Automation** - Uses Selenium with Chrome/Chromium to avoid blocking issues
- **Multiple Search Strategies** - Tries different query formats for better results
- **Smart Matching** - Scores results based on name, title, and company matches
- **Bulk Processing** - Support for CSV input files
- **Respectful Rate Limiting** - Built-in delays to avoid being blocked
- **High Accuracy** - Finds actual LinkedIn profiles, not just guessed URLs
- **Multiple Versions** - Standard, Fast, and Chromium variants for different use cases
- **REST API** - FastAPI-based web service for programmatic access
- **Web Interface** - Simple HTML interface for easy testing

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Chrome browser installed
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd linkedin_profile_finder
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\Activate.ps1
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Command Line Interface

#### Standard Version (Recommended)
```bash
# Basic search with name only
python linkedin_finder.py --name "John Doe"

# Search with title and company
python linkedin_finder.py --name "John Doe" --title "Software Engineer" --company "Google"

# Search with location
python linkedin_finder.py --name "Jane Smith" --title "Product Manager" --company "Microsoft" --location "Seattle"
```

#### Fast Version (Optimized for Speed)
```bash
# Uses fewer search strategies for faster results
python linkedin_finder_fast.py --name "John Doe" --title "Software Engineer" --company "Google"
```

#### Chromium Version (Headless Mode)
```bash
# Runs in headless mode for server environments
python linkedin_finder_chromium.py --name "John Doe" --title "Software Engineer" --company "Google"
```

### Bulk Search from CSV

Create a CSV file with headers: `name,title,company,location`

```csv
name,title,company,location
John Doe,Software Engineer,Google,San Francisco
Jane Smith,Product Manager,Microsoft,Seattle
Bob Johnson,Data Scientist,Amazon,New York
```

Then run:
```bash
python linkedin_finder.py --csv leads.csv --out results.json
```

### Advanced Options

```bash
# Limit results per search
python linkedin_finder.py --name "John Doe" --max-results 5

# Change output format
python linkedin_finder.py --name "John Doe" --out results.csv

# Adjust delay between searches
python linkedin_finder.py --name "John Doe" --sleep 3.0
```

## 🌐 Web API

### Start the API Server

```bash
# Standard API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Fast API (optimized)
uvicorn api.main_fast:app --reload --host 0.0.0.0 --port 8000

# Chromium API (headless)
uvicorn api.main_chromium:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

- **Health Check**: `GET /health`
- **Single Search**: `POST /search`
- **Batch Search**: `POST /search/batch`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Web Interface**: Open `api/index.html` in your browser

### API Usage Examples

#### Python Client
```python
import requests

# Single search
response = requests.post("http://localhost:8000/search", json={
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Google"
})

results = response.json()
print(f"Found {results['total_results']} profiles")

# Batch search
batch_response = requests.post("http://localhost:8000/search/batch", json={
    "queries": [
        {"name": "John Doe", "title": "Software Engineer"},
        {"name": "Jane Smith", "title": "Product Manager"}
    ]
})
```

#### JavaScript/Node.js
```javascript
// Single search
const response = await fetch('http://localhost:8000/search', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        name: 'John Doe',
        title: 'Software Engineer',
        company: 'Google'
    })
});

const results = await response.json();
console.log(`Found ${results.total_results} profiles`);
```

#### cURL
```bash
# Single search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Google"
  }'
```

## 📊 Output Format

Results are saved in JSON or CSV format with the following fields:

```json
[
  {
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Google",
    "location": "San Francisco",
    "url": "https://www.linkedin.com/in/johndoe123",
    "result_title": "John Doe - Software Engineer - Google",
    "snippet": "San Francisco, California, United States · Software Engineer · Google...",
    "score": 8.0
  }
]
```

### Score Explanation

- **8.0+**: Excellent match (exact name + title + company)
- **5.0-7.9**: Good match (name + partial title/company)
- **2.0-4.9**: Fair match (name only or partial matches)
- **< 2.0**: Poor match (likely not the right person)

## 🔧 Configuration

### Environment Variables

Set these optional environment variables:

```bash
# For SerpAPI integration (alternative search method)
export SERPAPI_API_KEY="your_serpapi_key_here"
```

### Browser Options

The tool automatically:
- Downloads and manages ChromeDriver
- Uses realistic browser settings
- Implements anti-detection measures
- Runs in visible mode (can be made headless)

## 📁 Project Structure

```
linkedin_profile_finder/
├── linkedin_finder.py              # Main script (standard version)
├── linkedin_finder_fast.py         # Fast optimized version
├── linkedin_finder_chromium.py     # Chromium/headless version
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── .gitignore                     # Git ignore rules
├── results.json                   # Output file (example)
├── venv/                          # Virtual environment (ignored by git)
├── api/                           # Web API components
│   ├── main.py                    # Standard FastAPI app
│   ├── main_fast.py               # Fast API version
│   ├── main_chromium.py           # Chromium API version
│   ├── index.html                 # Web interface
│   ├── client_example.py          # Python client example
│   └── README.md                  # API documentation
├── start_api.py                   # API startup script
├── start_api_chromium.py          # Chromium API startup script
├── check_chrome.py                # Chrome installation checker
└── test_chrome.py                 # Chrome functionality tester
```

## 🛠️ How It Works

1. **Query Building**: Creates multiple search strategies
   - `"John Doe" "Software Engineer" "Google" site:linkedin.com/in`
   - `"John Doe" "Software Engineer" "Google" linkedin`
   - `"John Doe" linkedin profile`

2. **Google Search**: Uses Selenium to search Google with real browser

3. **Result Extraction**: Parses search results to find LinkedIn profile URLs

4. **Scoring**: Evaluates each result based on:
   - Name matching (exact vs partial)
   - Title matching
   - Company matching
   - Location matching

5. **Output**: Returns ranked results with confidence scores

## 🔄 Version Comparison

| Feature | Standard | Fast | Chromium |
|---------|----------|------|----------|
| Search Strategies | 3 | 1-2 | 3 |
| Speed | Medium | Fast | Medium |
| Browser Mode | Visible | Headless | Headless |
| Use Case | Development | Production | Server |
| Memory Usage | Higher | Lower | Lower |

## 🔒 Privacy & Ethics

- **Respectful Usage**: Built-in delays to avoid overwhelming servers
- **Public Data Only**: Only searches publicly available information
- **No Login Required**: Doesn't require LinkedIn login
- **Terms Compliance**: Designed to respect website terms of service

## 🐛 Troubleshooting

### Common Issues

1. **Chrome not found**
   - Ensure Chrome browser is installed
   - The tool will automatically download ChromeDriver
   - Run `python check_chrome.py` to verify installation

2. **No results found**
   - Try different search terms
   - Check if the person has a public LinkedIn profile
   - Verify spelling of name, title, and company

3. **Browser crashes**
   - Close other Chrome instances
   - Restart the script
   - Try the Chromium version for better stability

4. **Slow performance**
   - Use the Fast version for quicker results
   - Reduce `--max-results` value
   - Increase `--sleep` delay

5. **API not responding**
   - Check if the server is running: `curl http://localhost:8000/health`
   - Check server logs for error messages
   - Verify Chrome installation

### Debug Mode

For debugging, the script shows detailed logs:
- Search queries being used
- Number of results found
- URLs being extracted
- Confidence scores

### Testing Tools

```bash
# Test Chrome installation
python test_chrome.py

# Check Chrome availability
python check_chrome.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Users are responsible for:
- Complying with LinkedIn's Terms of Service
- Respecting privacy laws and regulations
- Using the tool ethically and responsibly

## 🆘 Support

If you encounter issues or have questions:
- Check the troubleshooting section above
- Review the logs for error messages
- Create an issue in the repository
- Check the API documentation at `api/README.md`

---

**Made with ❤️ for legitimate business use**
