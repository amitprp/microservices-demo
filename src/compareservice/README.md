# Compare Service

A microservice that compares 2-3 products and returns comparison data including a feature matrix.

## Feature Overview

The Compare Service enables users to:
- Select 2-3 products from the Online Boutique catalog
- View a side-by-side comparison table
- See a feature matrix showing product attributes (recycled, vintage, durable, etc.)
- Get a summary identifying the cheapest product

## API

### Endpoint

`POST /compare`

### Request

```json
{
  "product_ids": ["OLJCESPC7Z", "66VCHSJNUP", "1YMWWN1N4O"]
}
```

**Constraints:**
- Minimum 2 product IDs
- Maximum 3 product IDs

### Response

```json
{
  "products": [
    {
      "id": "OLJCESPC7Z",
      "name": "Sunglasses",
      "price": {"amount": "19.99", "currency": "USD"},
      "description": "Add a modern touch...",
      "categories": ["accessories"]
    }
  ],
  "summary": "Sunglasses is the cheapest at $19.99",
  "feature_matrix": {
    "features": ["recycled", "vintage", "stylish"],
    "matrix": {
      "OLJCESPC7Z": {"recycled": true, "vintage": false, "stylish": true},
      "66VCHSJNUP": {"recycled": false, "vintage": true, "stylish": false}
    }
  }
}
```

### Feature Matrix

The service extracts features from product descriptions using keyword matching:

| Category | Keywords |
|----------|----------|
| Materials | recycled, organic, sustainable, eco-friendly |
| Quality | durable, premium, handmade, authentic |
| Physical | lightweight, portable, compact, vintage |
| Style | classic, modern, stylish, minimalist |

Only features found in at least one product are included in the response.

### Health Check

`GET /health` - Returns `OK` when service is healthy

### OpenAPI Spec

`GET /openapi.yaml` - Returns the OpenAPI specification

---

## Local Development

### Option 1: Using deploy.py (Recommended)

From the project root:

```bash
# Fresh deployment (starts minikube, builds services, deploys)
python3 deploy.py --deploy

# Rebuild compareservice after code changes
python3 deploy.py --rebuild --services compareservice

# Open port-forward to access the app
python3 deploy.py --open

# Check deployment status
python3 deploy.py --status
```

Access the app at: **http://localhost:8080**

### Option 2: Run Locally (without Kubernetes)

```bash
cd src/compareservice

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the service
PORT=8080 PRODUCT_CATALOG_SERVICE_ADDR=localhost:3550 python compareservice.py
```

**Note:** Requires `productcatalogservice` running on port 3550.

### Option 3: Docker

```bash
# Build
docker build -t compareservice:local src/compareservice/

# Run
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e PRODUCT_CATALOG_SERVICE_ADDR=host.docker.internal:3550 \
  compareservice:local
```

---

## Testing

### Run Tests

```bash
cd src/compareservice

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Structure

| File | Description |
|------|-------------|
| `tests/test_compare_logic.py` | Unit tests for feature extraction, matrix building, summary generation |
| `tests/test_compareservice.py` | Integration tests for `/compare` endpoint |

### Test Cases

**Unit Tests (`test_compare_logic.py`):**
- `test_extract_features_*` - Feature keyword extraction from descriptions
- `test_build_feature_matrix_*` - Feature matrix construction
- `test_validate_ids_*` - Product ID validation (2-3 IDs required)
- `test_generate_summary_*` - Cheapest product summary generation

**Integration Tests (`test_compareservice.py`):**
- `/compare` endpoint returns correct response structure
- Feature matrix included in response
- Error handling for invalid requests

---

## Quality Focus: Testing

This service focuses on **testing quality** as the primary quality attribute.

### Measurement
- Number of automated tests
- Code coverage percentage
- All tests pass in CI

### Implementation
- Comprehensive unit tests for `compare_logic.py`
- Integration tests for API endpoints
- Edge case coverage (empty descriptions, no features found, etc.)

### Running Quality Checks

```bash
# Run tests with coverage
pytest tests/ --cov=. --cov-report=term-missing -v

# Expected output shows coverage percentage and any uncovered lines
```

---

## Project Structure

```
src/compareservice/
├── compareservice.py      # Flask app, HTTP handlers
├── compare_logic.py       # Business logic (feature extraction, matrix building)
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container build
├── openapi.yaml          # API specification
├── README.md             # This file
└── tests/
    ├── test_compare_logic.py      # Unit tests
    └── test_compareservice.py     # Integration tests
```

---

## API Examples

### Compare 2 Products

```bash
curl -X POST http://localhost:8080/compare \
  -H 'Content-Type: application/json' \
  -d '{"product_ids":["OLJCESPC7Z","66VCHSJNUP"]}'
```

### Compare 3 Products

```bash
curl -X POST http://localhost:8080/compare \
  -H 'Content-Type: application/json' \
  -d '{"product_ids":["OLJCESPC7Z","66VCHSJNUP","1YMWWN1N4O"]}'
```

### Health Check

```bash
curl http://localhost:8080/health
```

---

## Integration Points

| Component | Integration |
|-----------|-------------|
| **Frontend** | Calls `/compare` endpoint, displays comparison table |
| **ProductCatalogService** | Fetches product details via gRPC |
| **Kubernetes** | Deployed as separate pod with Service |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | HTTP server port | `8080` |
| `PRODUCT_CATALOG_SERVICE_ADDR` | ProductCatalogService address | `productcatalogservice:3550` |
