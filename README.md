# AI Quote Generator 🎯

A powerful AI-powered quote generator built with FastAPI. Generate inspirational, motivational, and creative quotes on demand using OpenAI's GPT models.

## Features ✨

- **AI-Powered Generation**: Uses Google's Gemini AI to create original, meaningful quotes
- **Multiple Categories**: Support for motivation, inspiration, wisdom, humor, love, and more
- **Customizable**: Specify topic, style, and length for personalized quotes
- **RESTful API**: Clean, well-documented API endpoints
- **Fast & Async**: Built with FastAPI for high performance
- **Interactive Docs**: Automatic Swagger UI and ReDoc documentation

## Project Structure 📁

```
ai_quote_generator/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   └── api/
│       ├── __init__.py
│       ├── controllers/       # Business logic
│       │   ├── __init__.py
│       │   └── quote_controller.py
│       ├── models/            # Pydantic models
│       │   ├── __init__.py
│       │   └── quote_models.py
│       ├── routes/            # API endpoints
│       │   ├── __init__.py
│       │   └── quote_routes.py
│       └── utils/             # Helper functions
│           ├── __init__.py
│           ├── ai_client.py
│           └── prompt_builder.py
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## Installation 🚀

### Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup Steps

1. **Clone the repository**
   ```bash
   cd ai_quote_generator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Usage 📖

### API Endpoints

Once the server is running, access the API at `http://localhost:8000`

#### 1. Generate Custom Quote
**POST** `/api/quotes/generate`

Generate a quote with custom parameters.

**Request Body:**
```json
{
  "category": "motivation",
  "topic": "perseverance",
  "style": "modern",
  "length": "medium"
}
```

**Response:**
```json
{
  "quote": "The path to success is paved with persistence...",
  "author": "AI Generated",
  "category": "motivation",
  "timestamp": "2025-10-23T10:30:00Z"
}
```

#### 2. Get Random Quote
**GET** `/api/quotes/random`

Generate a random inspirational quote.

**Response:**
```json
{
  "quote": "Every moment is a fresh beginning...",
  "author": "AI Generated",
  "category": "random",
  "timestamp": "2025-10-23T10:30:00Z"
}
```

#### 3. Get Available Categories
**GET** `/api/quotes/categories`

Get a list of all available quote categories.

**Response:**
```json
[
  "motivation",
  "inspiration",
  "wisdom",
  "humor",
  "love",
  "success",
  "life",
  "friendship",
  "happiness",
  "random"
]
```

#### 4. Health Check
**GET** `/health`

Check API health status.

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration ⚙️

Edit the `.env` file to customize settings:

```env
# API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
APP_NAME=AI Quote Generator
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# AI Model Settings
DEFAULT_MODEL=gemini-pro
MAX_TOKENS=150
TEMPERATURE=0.8
```

## Example Usage with cURL 💻

```bash
# Generate a custom quote
curl -X POST "http://localhost:8000/api/quotes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "motivation",
    "topic": "success",
    "style": "modern",
    "length": "short"
  }'

# Get a random quote
curl "http://localhost:8000/api/quotes/random"

# Get available categories
curl "http://localhost:8000/api/quotes/categories"
```

## Example Usage with Python 🐍

```python
import requests

# Generate custom quote
response = requests.post(
    "http://localhost:8000/api/quotes/generate",
    json={
        "category": "inspiration",
        "topic": "creativity",
        "style": "philosophical",
        "length": "medium"
    }
)
print(response.json())

# Get random quote
response = requests.get("http://localhost:8000/api/quotes/random")
print(response.json())
```

## Development 🛠️

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Running Tests

```bash
pytest tests/
```

## Docker Support 🐳

Build and run with Docker:

```bash
# Build image
docker build -t ai-quote-generator .

# Run container
docker run -p 8000:8000 --env-file .env ai-quote-generator
```

## API Models 📝

### QuoteRequest
- `category` (string): Category of quote (motivation, inspiration, wisdom, etc.)
- `topic` (string, optional): Specific topic for the quote
- `style` (string, optional): Writing style (e.g., 'Shakespeare', 'modern')
- `length` (string): Desired length ('short', 'medium', or 'long')

### QuoteResponse
- `quote` (string): The generated quote
- `author` (string): Author attribution (default: "AI Generated")
- `category` (string): Category of the quote
- `timestamp` (string): ISO 8601 timestamp

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License.

## Support 💬

If you encounter any issues or have questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI and Google Gemini AI