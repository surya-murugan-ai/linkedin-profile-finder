# LinkedIn Profile Finder API

A FastAPI-based REST API that finds LinkedIn profile URLs using Google search with intelligent matching and scoring.

## Features

- 🔍 **Smart Search**: Multiple search strategies to find LinkedIn profiles
- 🎯 **Intelligent Scoring**: Relevance scoring based on name, title, company, and location matches
- 🚀 **Fast Performance**: Async operations with Selenium web automation
- 📊 **Bulk Operations**: Support for multiple searches in a single request
- 🔒 **Input Validation**: Comprehensive request validation with Pydantic
- 📚 **Auto Documentation**: Interactive API docs with Swagger/OpenAPI
- 🛡️ **Error Handling**: Robust error handling and logging

## Quick Start

### 1. Install Dependencies

```bash
pip install -r api_requirements.txt
```

### 2. Run the API

```bash
cd api
python start.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### 1. Single Search

**POST** `/api/search`

Search for a single LinkedIn profile.

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
  "success": true,
  "results": [
    {
      "url": "https://linkedin.com/in/johndoe",
      "title": "John Doe - Software Engineer at Google",
      "snippet": "Software Engineer at Google with 5+ years of experience...",
      "score": 8.5
    }
  ],
  "total_found": 1,
  "search_time": 12.34,
  "message": "Found 1 LinkedIn profiles in 12.34 seconds"
}
```

### 2. Bulk Search

**POST** `/api/bulk-search`

Search for multiple LinkedIn profiles in a single request.

**Request Body:**
```json
{
  "searches": [
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
  "max_results_per_search": 10
}
```

### 3. Health Check

**GET** `/api/health`

Check if the API is running properly.

## Usage Examples

### Python Example

```python
import requests

# Single search
response = requests.post("http://localhost:8000/api/search", json={
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Google",
    "max_results": 5
})

results = response.json()
print(f"Found {results['total_found']} profiles")

# Bulk search
bulk_response = requests.post("http://localhost:8000/api/bulk-search", json={
    "searches": [
        {"name": "John Doe", "title": "Engineer", "company": "Google"},
        {"name": "Jane Smith", "title": "Manager", "company": "Microsoft"}
    ]
})
```

### cURL Example

```bash
# Single search
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Google"
  }'

# Health check
curl "http://localhost:8000/api/health"
```

### JavaScript Example

```javascript
// Single search
const response = await fetch('http://localhost:8000/api/search', {
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
console.log(`Found ${results.total_found} profiles`);
```

## Configuration

Copy `env.example` to `.env` and modify the settings:

```bash
cp env.example .env
```

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload for development (default: false)
- `RATE_LIMIT_PER_MINUTE`: Rate limiting (default: 30)
- `MAX_RESULTS_PER_SEARCH`: Max results per search (default: 10)
- `MAX_BULK_SEARCHES`: Max searches in bulk request (default: 50)

## Scoring System

The API uses a sophisticated scoring system to rank results:

- **Base Score**: 2.0 points for valid LinkedIn profile URLs
- **Name Matching**: 
  - Exact match: +3.0 points
  - All name tokens: +2.0 points
  - Partial match: +1.0 points
- **Title Matching**: +1.5 points
- **Company Matching**: +1.5 points
- **Location Matching**: +1.0 points
- **Penalties**: -2.0 points for company pages

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid input)
- `500`: Internal server error

Error responses include detailed error messages:

```json
{
  "detail": "Search failed: Chrome driver not found"
}
```

## Rate Limiting

The API includes built-in rate limiting to prevent abuse:

- Default: 30 requests per minute
- Configurable via environment variables
- Returns 429 status code when limit exceeded

## Development

### Running in Development Mode

```bash
# Enable auto-reload
export RELOAD=true
python start.py
```

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY api_requirements.txt .
RUN pip install -r api_requirements.txt

COPY api/ .

EXPOSE 8000
CMD ["python", "start.py"]
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### Common Issues

1. **Chrome Driver Not Found**
   - The API automatically downloads ChromeDriver
   - Ensure Chrome browser is installed
   - Check internet connection for driver download

2. **No Results Found**
   - Try different search terms
   - Check if the person has a public LinkedIn profile
   - Verify name spelling and company name

3. **Rate Limiting**
   - Reduce request frequency
   - Use bulk search for multiple queries
   - Implement proper caching

### Logs

Check the console output for detailed logs and error messages.

## License

This project is for educational purposes. Please respect LinkedIn's terms of service and use responsibly.

## Disclaimer

This API is for educational and legitimate business purposes only. Users are responsible for complying with LinkedIn's terms of service and applicable laws.

