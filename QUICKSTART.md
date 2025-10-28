# Quick Start Guide 🚀

## Get Started in 5 Minutes!

### Step 1: Set Up Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get your API key from: https://makersuite.google.com/app/apikey
```

Your `.env` should look like:
```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### Step 3: Run the Server

```bash
# Option 1: Use the start script
./start.sh

# Option 2: Run directly
python main.py

# Option 3: Use uvicorn
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### Step 4: Test the API

Open your browser and go to:
- **Interactive Docs**: http://localhost:8000/docs
- **API Root**: http://localhost:8000

Or use curl:
```bash
# Get a random quote
curl http://localhost:8000/api/quotes/random

# Generate a custom quote
curl -X POST http://localhost:8000/api/quotes/generate \
  -H "Content-Type: application/json" \
  -d '{"category":"motivation","topic":"success"}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/api/quotes/random` | Get random quote |
| POST | `/api/quotes/generate` | Generate custom quote |
| GET | `/api/quotes/categories` | List categories |

## Troubleshooting

### "Gemini API key not configured"
- Make sure you created a `.env` file
- Verify your API key is correct (get it from Google AI Studio)
- Restart the server after adding the key

### "Module not found" errors
- Activate your virtual environment
- Run `pip install -r requirements.txt`

### Port already in use
- Change the PORT in `.env` file
- Or kill the process using port 8000

## Next Steps

- Check the full [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Customize settings in `.env`
- Add your own quote categories in `app/api/models/quote_models.py`

---

<div align="center">
  <em>Built by AyaNexus 🦢</em>
</div>
