# LinkedIn Profile Finder API

A FastAPI-based REST API that wraps the LinkedIn Profile Finder functionality, allowing you to search for LinkedIn profiles programmatically via HTTP requests.

## Features

- **Single Profile Search**: Search for individual LinkedIn profiles
- **Batch Search**: Process multiple search queries in one request
- **Real Browser Automation**: Uses Selenium with Chrome for reliable results
- **Smart Scoring**: Results are scored and ranked by relevance
- **RESTful API**: Clean HTTP endpoints with JSON responses
- **Interactive Documentation**: Auto-generated API docs with Swagger UI
- **CORS Support**: Ready for web applications
- **Error Handling**: Comprehensive error responses

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Web Interface**: Open `api/index.html` in your browser

## API Endpoints

### Health Check

```http
GET /health
```

Returns API status and version information.

### Single Profile Search

```http
POST /search
```

**Request Body:**
```json
{
  "name": "John Doe",
  "title": "Software Engineer",
  "company": "Google",
  "location": "San Francisco",
  "max_results": 10
}
```

**Response:**
```json
{
  "query": {
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Google",
    "location": "San Francisco",
    "max_results": 10
  },
  "results": [
    {
      "url": "https://linkedin.com/in/johndoe",
      "title": "John Doe - Software Engineer at Google",
      "snippet": "Software Engineer with 5+ years of experience...",
      "score": 8.5
    }
  ],
  "total_results": 1,
  "search_time": 3.2,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Batch Profile Search

```http
POST /search/batch
```

**Request Body:**
```json
{
  "queries": [
    {
      "name": "John Doe",
      "title": "Software Engineer",
      "company": "Google"
    },
    {
      "name": "Jane Smith",
      "title": "Product Manager",
      "company": "Microsoft"
    }
  ],
  "max_results": 5
}
```

**Response:**
```json
{
  "searches": [
    {
      "query": {...},
      "results": [...],
      "total_results": 1,
      "search_time": 0,
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "total_searches": 2,
  "total_profiles_found": 2,
  "batch_time": 8.5,
  "timestamp": "2024-01-15T10:30:00"
}
```

## Usage Examples

### Python Client

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

### JavaScript/Node.js

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

// Batch search
const batchResponse = await fetch('http://localhost:8000/search/batch', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        queries: [
            {name: 'John Doe', title: 'Software Engineer'},
            {name: 'Jane Smith', title: 'Product Manager'}
        ]
    })
});
```

### cURL

```bash
# Single search
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Google"
  }'

# Batch search
curl -X POST "http://localhost:8000/search/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      {"name": "John Doe", "title": "Software Engineer"},
      {"name": "Jane Smith", "title": "Product Manager"}
    ]
  }'
```

## Configuration

### Environment Variables

You can configure the API using environment variables:

```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export API_RELOAD=true
export API_LOG_LEVEL=info
```

### Chrome Browser Requirements

The API requires Google Chrome to be installed on the system. If Chrome is not found, you'll get a helpful error message with installation instructions.

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Server-side error (e.g., Chrome not found)

Error responses include details about what went wrong:

```json
{
  "detail": "Search failed: Chrome browser not found. Please install Google Chrome and try again."
}
```

## Rate Limiting

The API includes built-in delays between searches to be respectful to Google's servers:

- Single searches: No additional delay
- Batch searches: 2-second delay between queries
- Configurable delays in the underlying search logic

## Development

### Running in Development Mode

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Running in Production

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing the API

1. **Using the Web Interface**: Open `api/index.html` in your browser
2. **Using the Python Client**: Run `python api/client_example.py`
3. **Using the API Docs**: Visit http://localhost:8000/docs

### Project Structure

```
api/
├── main.py              # FastAPI application
├── client_example.py    # Python client example
├── index.html          # Web interface
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Chrome Browser Not Found**
   - Install Google Chrome from https://www.google.com/chrome/
   - Restart your terminal after installation

2. **API Not Responding**
   - Check if the server is running: `curl http://localhost:8000/health`
   - Check server logs for error messages

3. **CORS Errors in Web Applications**
   - The API includes CORS middleware configured for all origins
   - For production, configure specific origins in `api/main.py`

4. **Slow Search Performance**
   - Searches use real browser automation and can take 3-10 seconds
   - Batch searches include delays between queries
   - Consider running searches in parallel for better performance

### Debug Mode

To run with debug logging:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

## Security Considerations

- The API currently allows all CORS origins (`*`) - configure properly for production
- No authentication is implemented - add authentication for production use
- Consider rate limiting for public APIs
- Monitor Chrome browser instances to prevent resource leaks

## License

This API is part of the LinkedIn Profile Finder project. See the main project README for license information.
