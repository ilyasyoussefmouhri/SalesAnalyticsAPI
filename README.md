# FastAPI Sales Analytics

A comprehensive FastAPI application for analyzing sales data with data validation, quality checks, and detailed analytics.

## Features

- **Health Check**: Monitor application status
- **Quick Stats**: Get file information and basic statistics
- **Data Validation**: Validate data quality and identify issues
- **Full Analysis**: Comprehensive sales analytics including:
  - Total revenue and quantity calculations
  - Top products by revenue and quantity
  - Customer segmentation (high/medium/low value)
  - Time-based analysis (daily and monthly revenue)

## Project Structure

The project follows a clean architecture with separation of concerns:

```
├── main.py          # Application entry point, middleware, and app initialization
├── routers.py       # API endpoints and authentication
├── processing.py    # Data processing and analytics functions
├── schemas.py       # Pydantic models for request/response validation
├── config.py        # Configuration settings with .env support
├── requirements.txt # Python dependencies
├── README.md        # This file
├── test_data.csv    # Sample sales data for testing
└── .gitignore       # Git ignore patterns
```

- **main.py**: Contains FastAPI app initialization, middleware setup (CORS, logging), and the main entry point
- **routers.py**: All API route handlers and authentication logic
- **processing.py**: Business logic for CSV reading, data validation, and sales analytics calculations
- **schemas.py**: Pydantic models for type-safe request/response handling
- **config.py**: Centralized configuration management using Pydantic Settings

## Requirements

- Python 3.8+
- pip

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the project root with the following content:
   ```bash
   # API Configuration
   API_KEY=your-secret-api-key-change-in-production
   API_KEY_HEADER=X-API-Key
   
   # Application Settings
   APP_NAME=FastAPI Sales Analytics
   APP_VERSION=1.0.0
   DEBUG=False
   
   # CORS Settings
   CORS_ORIGINS=["*"]
   CORS_ALLOW_CREDENTIALS=True
   CORS_ALLOW_METHODS=["*"]
   CORS_ALLOW_HEADERS=["*"]
   
   # Logging
   LOG_LEVEL=INFO
   ```
   
   Make sure to update the `API_KEY` with your secret key.

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Or run directly:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. GET /health
Health check endpoint (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

### 2. POST /quick-stats
Get quick statistics about the uploaded CSV file.

**Headers:**
- `X-API-Key: your-secret-api-key`

**Request:**
- `file`: CSV file (multipart/form-data)

**Response:**
```json
{
  "filename": "sales.csv",
  "file_size": 1024,
  "rows": 20,
  "columns": 5,
  "column_names": ["date", "product", "quantity", "price", "customer"],
  "data_types": {...},
  "sample_data": [...]
}
```

### 3. POST /validate
Validate data quality of the uploaded sales file.

**Headers:**
- `X-API-Key: your-secret-api-key`

**Request:**
- `file`: CSV file (multipart/form-data)

**Response:**
```json
{
  "filename": "sales.csv",
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": [],
    "stats": {...}
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### 4. POST /analyze
Perform full sales analysis on the uploaded file.

**Headers:**
- `X-API-Key: your-secret-api-key`

**Request:**
- `file`: CSV file (multipart/form-data)

**Response:**
```json
{
  "filename": "sales.csv",
  "validation": {...},
  "analytics": {
    "total_revenue": 15000.0,
    "total_quantity": 100,
    "total_orders": 20,
    "average_order_value": 750.0,
    "top_products_by_revenue": {...},
    "top_products_by_quantity": {...},
    "customer_segments": {...},
    "time_analysis": {...}
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## CSV File Format

The application expects CSV files with the following columns:

- **date**: Date of the sale (format: YYYY-MM-DD or any parseable date format)
- **product**: Product name
- **quantity**: Quantity sold (numeric)
- **price**: Price per unit (numeric)
- **customer**: Customer name or ID

Example:
```csv
date,product,quantity,price,customer
2024-01-01,Widget A,5,10.50,Customer A
2024-01-02,Widget B,3,15.00,Customer B
```

## Testing

You can test the API using the included `test_data.csv` file or use tools like:

- **curl**:
  ```bash
  curl -X POST "http://localhost:8000/analyze" \
    -H "X-API-Key: your-secret-api-key" \
    -F "file=@test_data.csv"
  ```

- **Python requests**:
  ```python
  import requests
  
  url = "http://localhost:8000/analyze"
  headers = {"X-API-Key": "your-secret-api-key"}
  files = {"file": open("test_data.csv", "rb")}
  
  response = requests.post(url, headers=headers, files=files)
  print(response.json())
  ```

- **Postman**: Import the endpoints and test with file uploads

## Security

- **API Key Authentication**: All endpoints (except `/health`) require a valid API key in the `X-API-Key` header
- **CORS**: Configured via environment variables
- **Input Validation**: All uploaded files are validated before processing

## Configuration

All configuration is done through environment variables in the `.env` file:

- `API_KEY`: Secret API key for authentication
- `API_KEY_HEADER`: Header name for API key (default: X-API-Key)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)
- `CORS_ORIGINS`: Allowed CORS origins (default: ["*"])

## Logging

The application includes comprehensive logging middleware that logs:
- All HTTP requests with method and path
- Response status codes
- Processing time for each request

Logs are written to both:
- **Console**: Real-time log output during development
- **File**: All logs are saved to `app.log` in the project root directory

The log file (`app.log`) is automatically excluded from version control via `.gitignore`.

## License

This project is provided as-is for educational and development purposes.
