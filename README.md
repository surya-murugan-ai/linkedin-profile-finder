# LinkedIn Profile Finder 🔍

A powerful Python tool that finds LinkedIn profile URLs using real browser automation, similar to Apify's LinkedIn Profile Search. This tool searches Google for LinkedIn profiles and returns accurate results with confidence scoring.

## ✨ Features

- **Real Browser Automation** - Uses Selenium with Chrome to avoid blocking issues
- **Multiple Search Strategies** - Tries different query formats for better results
- **Smart Matching** - Scores results based on name, title, and company matches
- **Bulk Processing** - Support for CSV input files
- **Respectful Rate Limiting** - Built-in delays to avoid being blocked
- **High Accuracy** - Finds actual LinkedIn profiles, not just guessed URLs

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

### Single Person Search

```bash
# Basic search with name only
python linkedin_finder.py --name "John Doe"

# Search with title and company
python linkedin_finder.py --name "John Doe" --title "Software Engineer" --company "Google"

# Search with location
python linkedin_finder.py --name "Jane Smith" --title "Product Manager" --company "Microsoft" --location "Seattle"
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
├── linkedin_finder.py      # Main script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── results.json           # Output file (example)
└── venv/                  # Virtual environment (ignored by git)
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

2. **No results found**
   - Try different search terms
   - Check if the person has a public LinkedIn profile
   - Verify spelling of name, title, and company

3. **Browser crashes**
   - Close other Chrome instances
   - Restart the script

4. **Slow performance**
   - Reduce `--max-results` value
   - Increase `--sleep` delay

### Debug Mode

For debugging, the script shows detailed logs:
- Search queries being used
- Number of results found
- URLs being extracted
- Confidence scores

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

---

**Made with ❤️ for legitimate business use**
