<div align="center">

# Swan - Quote Generator
Because sometimes, the right words can light the stars inside you | [Website](https://www.swanexus.dev)


![Swan](./assets/Swan.png)

</div>

A powerful full-stack AI-powered quote generator with a stunning React frontend and FastAPI backend. Generate inspirational, motivational, and creative quotes on demand using Google's Gemini AI.

## Features

### Backend
- **AI-Powered Generation**: Uses Google's Gemini AI to create original, meaningful quotes
- **Bilingual Support**: Generate quotes in English and Arabic (AR) with proper language handling
- **Multiple Categories**: Support for motivation, inspiration, wisdom, humor, love, success, life, friendship, happiness, and random
- **Customizable**: Specify topic, style, language, and length for personalized quotes
- **RESTful API**: Clean, well-documented API endpoints
- **Fast & Async**: Built with FastAPI for high performance
- **Interactive Docs**: Automatic Swagger UI documentation
- **Serverless Ready**: Optimized for Vercel deployment with Mangum adapter

### Frontend
- **Modern React UI**: Beautiful, responsive interface built with React 18
- **Language Selection**: Easy language switching between English and Arabic quote generation
- **Animated Background**: Dynamic particle effects for visual appeal
- **Mobile-First Design**: Fully responsive layout optimized for all devices
- **Tailwind CSS**: Modern, utility-first styling with custom purple theme
- **Real-time Feedback**: Loading states and error handling
- **Copy to Clipboard**: Easy quote sharing functionality
- **Smooth Animations**: Framer Motion for fluid transitions

## Project Structure

```
ai_quote_generator/
├── app/
│   ├── __init__.py
│   ├── config.py                # Configuration settings
│   ├── main.py                  # FastAPI app with CORS & static serving
│   └── api/
│       ├── __init__.py
│       ├── controllers/         # Business logic
│       │   ├── __init__.py
│       │   └── quote_controller.py
│       ├── models/              # Pydantic models
│       │   ├── __init__.py
│       │   └── quote_models.py
│       ├── routes/              # API endpoints
│       │   ├── __init__.py
│       │   └── quote_routes.py
│       └── utils/               # Helper functions
│           ├── __init__.py
│           ├── ai_client.py
│           └── prompt_builder.py
├── static/                      # React frontend
│   ├── package.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   └── components/
│   │       ├── AnimatedBackground.js  # Canvas-based particle effects
│   │       ├── QuoteGenerator.js      # Main UI component
│   │       ├── FluidCursor.js         # Custom cursor effects
│   │       └── Navigation.js
│   └── build/                   # Production build (served by FastAPI)
├── api/
│   └── index.py                 # Vercel serverless entry point
├── main.py                      # Local development entry point
├── Dockerfile                   # Multi-stage production container
├── docker-compose.yml           # Development environment
├── docker-compose.prod.yml      # Production environment
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/1AyaNabil1/Swan_Quote_Generator.git
   cd ai_quote_generator
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   APP_NAME=Swan Quote Generator
   APP_VERSION=1.0.0
   DEBUG=True
   ```

### Frontend Setup

1. **Navigate to the static directory**
   ```bash
   cd static
   ```

2. **Install npm dependencies**
   ```bash
   npm install
   ```

3. **Build the React app**
   ```bash
   npm run build
   ```

4. **Return to the root directory**
   ```bash
   cd ..
   ```

### Running the Application

#### Option 1: Local Development (Backend Only)
```bash
python3 main.py
```
The API will be available at `http://localhost:8000`

#### Option 2: Full Stack Development
```bash
# Terminal 1 - Run FastAPI backend
python3 main.py

# Terminal 2 - Run React dev server
cd static
npm start
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

#### Option 3: Production Mode (Integrated)
```bash
# Build React app first
cd static
npm run build
cd ..

# Run FastAPI with built frontend
python3 main.py
```
Access the full application at `http://localhost:8000`

#### Option 4: Docker
```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up
```

## Usage

### Web Interface

Once the application is running, open your browser to `http://localhost:8000` to access the beautiful Swan interface:

1. **Select a Category**: Choose from motivation, inspiration, wisdom, humor, love, success, life, friendship, happiness, or random
2. **Select Language**: Choose English or (Arabic) for quote generation
3. **Add Optional Topic**: Specify a specific topic like "perseverance" or "courage"
4. **Add Optional Style**: Define a writing style like "Shakespeare" or "modern"
5. **Generate**: Click the "Generate Quote" button
6. **Copy & Share**: Use the "Copy Quote" button to copy the generated quote to your clipboard

The interface features:
- Bilingual quote generation (English/Arabic)
- Beautiful Arabic fonts (Amiri for quotes, Cairo for UI) automatically applied for Arabic text
- Responsive mobile-first design
- Animated particle background
- Smooth transitions and hover effects
- Real-time loading states
- Error handling with user-friendly messages

### API Endpoints

The backend provides RESTful API endpoints accessible at `http://localhost:8000`

#### 1. Generate Custom Quote
**POST** `/api/quotes/generate`

Generate a quote with custom parameters.

**Request Body:**
```json
{
  "category": "motivation",
  "topic": "perseverance",
  "style": "modern",
  "length": "medium",
  "language": "en"
}
```

**Note**: `language` can be `"en"` (English) or `"ar"` (Arabic)

**Response:**
```json
{
  "quote": "The path to success is paved with persistence...",
  "author": "Swan",
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
  "author": "Swan",
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

- **Swagger UI**: http://localhost:8000/docs (available in development mode)

### Frontend Technologies

- **React 18**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework with custom purple theme
- **Framer Motion**: Smooth animations and transitions
- **Canvas API**: Custom particle animation background
- **Responsive Design**: Mobile-first approach with breakpoints for tablets and desktops

## Configuration

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
MAX_TOKENS=2048
TEMPERATURE=0.8
```

## Example Usage with cURL

```bash
# Generate a custom quote in English
curl -X POST "http://localhost:8000/api/quotes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "motivation",
    "topic": "success",
    "style": "modern",
    "length": "short",
    "language": "en"
  }'

# Generate a quote in Arabic
curl -X POST "http://localhost:8000/api/quotes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "motivation",
    "topic": "نجاح",
    "language": "ar"
  }'

# Get a random quote
curl "http://localhost:8000/api/quotes/random"

# Get available categories
curl "http://localhost:8000/api/quotes/categories"
```

## Example Usage with Python

```python
import requests

# Generate custom quote in English
response = requests.post(
    "http://localhost:8000/api/quotes/generate",
    json={
        "category": "inspiration",
        "topic": "creativity",
        "style": "philosophical",
        "length": "medium",
        "language": "en"
    }
)
print(response.json())

# Generate custom quote in Arabic
response = requests.post(
    "http://localhost:8000/api/quotes/generate",
    json={
        "category": "inspiration",
        "topic": "إبداع",
        "language": "ar"
    }
)
print(response.json())

# Get random quote
response = requests.get("http://localhost:8000/api/quotes/random")
print(response.json())
```

## Development

### Code Quality & Linting

This project uses **Ruff** - a fast Python linter and formatter written in Rust.

#### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

#### Running Ruff

**Check for linting issues:**
```bash
ruff check .
```

**Auto-fix issues:**
```bash
ruff check --fix .
```

**Format code:**
```bash
ruff format .
```

**Check and fix everything:**
```bash
ruff check --fix . && ruff format .
```

#### Ruff Configuration

The project is configured via `pyproject.toml` with the following rules:
- Line length: 100 characters
- Target: Python 3.11+
- Import sorting (isort)
- Code modernization (pyupgrade)
- Bug detection (flake8-bugbear)
- Code simplification rules
- Auto-fix enabled for all rules

### Running in Development Mode

#### Backend Development
```bash
# Auto-reload on file changes
python3 main.py
```
The `--reload` flag is built into `main.py` for development.

#### Frontend Development
```bash
cd static
npm start
```
React dev server with hot-reload at `http://localhost:3000`

#### Full Stack Development
Run both backend and frontend simultaneously:
```bash
# Terminal 1
python3 main.py

# Terminal 2
cd static && npm start
```

### Building for Production

```bash
# Build React frontend
cd static
npm run build
cd ..

# The FastAPI app will automatically serve the built frontend
python3 main.py
```

### Running Tests

```bash
# Python tests
pytest tests/

# Frontend tests
cd static
npm test
```

## Docker Support

### Development Environment
```bash
docker-compose up
```

### Production Environment
```bash
# Build and run optimized production container
docker-compose -f docker-compose.prod.yml up --build
```

### Manual Docker Commands
```bash
# Build image
docker build -t swan-quote-generator .

# Run container
docker run -p 8000:8000 --env-file .env swan-quote-generator
```

The Dockerfile uses multi-stage builds for optimized image size and security.

## Deployment

### Vercel Deployment

This application is optimized for Vercel serverless deployment:

1. **Prerequisites**: Vercel account and CLI installed
   ```bash
   npm i -g vercel
   ```

2. **Configure Environment Variables**
   Add `GEMINI_API_KEY` to your Vercel project settings

3. **Deploy**
   ```bash
   vercel --prod
   ```

The `api/index.py` file provides the Mangum adapter for serverless compatibility.

### Traditional Hosting

For traditional hosting (VPS, cloud VM):

1. Build the frontend:
   ```bash
   cd static && npm run build && cd ..
   ```

2. Run with gunicorn or uvicorn:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. Use nginx as a reverse proxy (recommended)

## UI Features

### Animated Background
- Dynamic particle system using HTML5 Canvas
- Smooth animations with 60fps performance
- Responsive to screen size changes
- Purple-themed particles with pulsing effects

### Responsive Design
- **Mobile**: Vertical layout with controls at top
- **Tablet**: Optimized spacing and font sizes
- **Desktop**: Two-column layout with quote display and controls side-by-side

### Color Scheme
- **Primary Purple**: `#9333ea`
- **Purple Accent**: `#a78bfa`
- **Purple Light**: `#c4b5fd`
- **Background**: Black with gradient overlays
- **Text**: White with varying opacity levels

## API Models

### QuoteRequest
- `category` (string): Category of quote (motivation, inspiration, wisdom, etc.)
- `topic` (string, optional): Specific topic for the quote
- `style` (string, optional): Writing style (e.g., 'Shakespeare', 'modern')
- `length` (string): Desired length ('short', 'medium', or 'long')
- `language` (string, optional): Language for quote generation - 'en' (English) or 'ar' (Arabic). Defaults to 'en'

### QuoteResponse
- `quote` (string): The generated quote
- `author` (string): Author attribution (default: "Swan")
- `category` (string): Category of the quote
- `timestamp` (string): ISO 8601 timestamp

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly (backend and frontend)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Google Gemini AI**: AI model for quote generation
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI framework
- **Tailwind CSS**: Utility-first CSS
- **Framer Motion**: Animation library
- **HTML5 Canvas**: Custom animations

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Render**: Serverless deployment platform

## License

This project is open source and available under the MIT License.

## Credits & Links

- **Built by**: [AyaNexus](https://ayanexus.dev/) 🦢
- **GitHub Repository**: [Swan_Quote_Generator](https://github.com/1AyaNabil1/Swan_Quote_Generator)
- **Live Demo**: [Swan](https://swanexus.dev)
- **Powered by**: Google Gemini AI

---

<div align="center">
  <p><em>Built by AyaNexus 🦢</em></p>
</div>
