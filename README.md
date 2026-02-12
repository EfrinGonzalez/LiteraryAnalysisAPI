# Literary Analysis API

FastAPI backend for analyzing text, URLs, and images with advanced sentiment analysis and keyword extraction. Fully **open-source** and **offline** - no external APIs required.

## Features

- 📝 **Text Analysis**: Analyze plain text with sentiment analysis and keyword extraction
- 🌐 **URL Analysis**: Fetch and analyze web articles with SSRF protection
- 🖼️ **Image Analysis**: Extract text from images using OCR and analyze it
- 🧠 **Tiered Sentiment Analysis**:
  - **Fast Mode**: VADER lexicon-based sentiment (instant results)
  - **Smart Mode**: Transformer-based analysis (optional, requires additional dependencies)
- 🔑 **Keyword Extraction**: TF-IDF based keyword identification
- 💾 **Persistent Storage**: SQLite database stores all analysis results
- 🔒 **SSRF Protection**: Built-in security against malicious URL requests
- 🚀 **RESTful v1 API**: Well-structured endpoints with proper validation

## Installation

### Prerequisites

- Python 3.8+
- Tesseract OCR (for image analysis)

#### Install Tesseract

- **macOS**: `brew install tesseract`
- **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
- **Windows**: Download from [GitHub](https://github.com/tesseract-ocr/tesseract)

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/EfrinGonzalez/LiteraryAnalysisAPI.git
cd LiteraryAnalysisAPI

# Install Python dependencies
pip install -r requirements.txt
```

### Optional: Smart Mode (Transformer-based Sentiment)

For the smart mode, uncomment the following lines in `requirements.txt` and reinstall:

```txt
transformers>=4.30.0
torch>=2.0.0
```

**Note**: These dependencies are large (~2GB) and require more computational resources. If not installed, smart mode will gracefully fall back to fast mode.

## Running the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Base URL**: `http://localhost:8000`
- **Interactive docs**: `http://localhost:8000/docs`
- **OpenAPI spec**: `http://localhost:8000/openapi.json`

## API Endpoints

### Health Check

**GET** `/health`

Check if the API is running and database is connected.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-12T20:00:00.000Z",
  "database": "connected"
}
```

### Analyze Text

**POST** `/v1/analyze/text`

Analyze text content with sentiment analysis and keyword extraction.

```bash
curl -X POST http://localhost:8000/v1/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a wonderful product! I absolutely love it.",
    "mode": "fast"
  }'
```

**Parameters:**
- `text` (string, required): Text to analyze
- `mode` (string, optional): `"fast"` (default) or `"smart"`

**Response:**
```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created_at": "2026-02-12T20:00:00.000Z",
  "source_type": "text",
  "mode": "fast",
  "result": {
    "word_count": 42,
    "sentiment": {
      "polarity_label": "positive",
      "polarity_score": 0.8,
      "confidence": null,
      "compound": 0.8,
      "positive": 0.6,
      "negative": 0.0,
      "neutral": 0.4
    },
    "keywords": ["wonderful", "product", "love"],
    "top_words": [["product", 5], ["wonderful", 3]]
  }
}
```

### Analyze URL

**POST** `/v1/analyze/url`

Fetch and analyze content from a URL.

```bash
curl -X POST http://localhost:8000/v1/analyze/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "mode": "fast"
  }'
```

**Parameters:**
- `url` (string, required): URL to fetch and analyze
- `mode` (string, optional): `"fast"` (default) or `"smart"`

**Security**: Built-in SSRF protection blocks localhost and private IP ranges.

### Analyze Image

**POST** `/v1/analyze/image`

Extract text from an image using OCR and analyze it.

```bash
curl -X POST http://localhost:8000/v1/analyze/image \
  -F "file=@/path/to/image.png" \
  -F "mode=fast"
```

**Parameters:**
- `file` (file, required): Image file (PNG, JPG, PDF)
- `mode` (string, optional): `"fast"` (default) or `"smart"`

**Requirements**: Tesseract OCR must be installed.

### Retrieve Analysis by ID

**GET** `/v1/analyses/{analysis_id}`

Retrieve a specific analysis result by its ID.

```bash
curl http://localhost:8000/v1/analyses/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### List Analyses

**GET** `/v1/analyses`

List all analyses with pagination and filtering.

```bash
curl "http://localhost:8000/v1/analyses?source_type=text&limit=10&offset=0"
```

**Query Parameters:**
- `source_type` (optional): Filter by `text`, `url`, or `image`
- `limit` (optional, default=10, max=100): Number of results per page
- `offset` (optional, default=0): Number of results to skip

**Response:**
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "analyses": [...]
}
```

## Analysis Modes

### Fast Mode (Default)

Uses **VADER** (Valence Aware Dictionary and sEntiment Reasoner) for sentiment analysis:

- ⚡ **Instant results** - no model loading required
- 📊 Provides compound, positive, negative, and neutral scores
- ✅ Works well for social media, reviews, and general text
- 🔧 No additional dependencies

### Smart Mode (Optional)

Uses **transformer-based models** (DistilBERT) for sentiment analysis:

- 🧠 **Advanced NLP** - deeper contextual understanding
- 🎯 Higher accuracy on complex text
- ⏱️ Slightly slower (still fast on modern hardware)
- 📦 Requires additional dependencies (transformers, torch)

**Fallback**: If transformer dependencies are not installed, smart mode automatically falls back to fast mode.

## Data Persistence

All analysis results are stored in a local SQLite database (`literary_analysis.db`) with the following information:

- Unique analysis ID (UUID)
- Timestamp
- Source type (text/url/image)
- Input hash (for deduplication)
- Extracted text (first 1000 characters)
- Analysis mode used
- Model version
- Complete analysis results

### Database Location

The database file is created in the root directory: `literary_analysis.db`

### Reset Database

To reset the database, simply delete the file:

```bash
rm literary_analysis.db
```

The database will be recreated automatically on next API startup.

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Tests cover:
- ✅ All API endpoints
- ✅ Sentiment analysis (positive, negative, neutral)
- ✅ SSRF protection
- ✅ Input validation
- ✅ Database persistence
- ✅ Pagination

## Project Structure

```
LiteraryAnalysisAPI/
├── app/
│   ├── main.py              # FastAPI application
│   ├── routes.py            # API endpoints
│   ├── database.py          # Database models & session
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── analysis.py      # Main analysis logic
│       ├── sentiment.py     # Sentiment analysis (VADER + transformers)
│       ├── keywords.py      # Keyword extraction
│       ├── scraper.py       # URL fetching with SSRF protection
│       ├── ocr.py           # Image OCR processing
│       └── report_writer.py # PDF report generation (legacy)
├── tests/
│   ├── conftest.py          # Test configuration
│   ├── test_api.py          # API endpoint tests
│   └── test_security.py     # Security tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Legacy Endpoints

For backward compatibility, the following legacy endpoints are still available:

- `POST /analyze-file/`
- `POST /analyze-url/`
- `POST /analyze-image/`

**Recommendation**: Use the new v1 endpoints for new integrations.

## Security Features

- ✅ **SSRF Protection**: Blocks requests to localhost and private IP ranges
- ✅ **Input Validation**: Pydantic models validate all inputs
- ✅ **Timeout Protection**: HTTP requests have timeouts
- ✅ **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- ✅ **Secure Dependencies**: All dependencies are open-source and vetted

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source and available under the MIT License.

## Acknowledgments

- **VADER Sentiment**: [vaderSentiment](https://github.com/cjhutto/vaderSentiment)
- **Transformers**: [Hugging Face Transformers](https://huggingface.co/transformers/)
- **FastAPI**: [FastAPI Framework](https://fastapi.tiangolo.com/)
- **Tesseract OCR**: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
