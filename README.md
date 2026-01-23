# FastAPI Sales Analytics

A comprehensive FastAPI application for analyzing sales data with data validation, quality checks, and detailed analytics.

**Repository**: [https://github.com/ilyasyoussefmouhri/SalesAnalyticsAPI](https://github.com/ilyasyoussefmouhri/SalesAnalyticsAPI)

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

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ilyasyoussefmouhri/SalesAnalyticsAPI.git
   cd SalesAnalyticsAPI
   ```

   Or if you already have the project, navigate to the project directory

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
   
   **IMPORTANT**: Create a `.env` file in the project root. The `API_KEY` is **REQUIRED** - the application will not start without it.
   
   Create a `.env` file with the following content:
   ```bash
   # API Configuration (REQUIRED)
   # SECURITY: You MUST set a secure API key - no default is provided for security reasons
   API_KEY=your-secret-api-key-change-in-production
   API_KEY_HEADER=X-API-Key
   
   # Application Settings
   APP_NAME=FastAPI Sales Analytics
   APP_VERSION=1.0.0
   DEBUG=False
   
   # CORS Settings (REQUIRED)
   # SECURITY: CORS_ORIGINS defaults to empty [] - you MUST configure allowed origins
   # For development: CORS_ORIGINS=["*"] (less secure, convenient for testing)
   # For production: CORS_ORIGINS=["https://yourdomain.com"] (specify exact origins)
   CORS_ORIGINS=["*"]
   CORS_ALLOW_CREDENTIALS=True
   CORS_ALLOW_METHODS=["*"]
   CORS_ALLOW_HEADERS=["*"]
   
   # Logging
   LOG_LEVEL=INFO
   ```
   
   **SECURITY NOTES**:
   - `API_KEY` is **REQUIRED** - the application will fail to start if not provided
   - `CORS_ORIGINS` defaults to `[]` (empty) - you MUST configure it explicitly
   - For development, you can use `CORS_ORIGINS=["*"]` but this is insecure for production
   - Generate a strong, random API key for production use

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
- **CORS Configuration**: **CRITICAL** - CORS (Cross-Origin Resource Sharing) must be properly configured for security and functionality:
  - **Security**: Prevents unauthorized cross-origin requests from accessing your API
  - **Functionality**: Enables frontend applications to communicate with the API without browser blocking
  - **Production**: Replace `["*"]` with specific allowed origins (e.g., `["https://yourdomain.com"]`) in production
  - **Development**: `["*"]` is acceptable for development but poses security risks in production
  - Configure via `.env` file using `CORS_ORIGINS`, `CORS_ALLOW_CREDENTIALS`, `CORS_ALLOW_METHODS`, and `CORS_ALLOW_HEADERS`
- **Input Validation**: All uploaded files are validated before processing

## Configuration

All configuration is done through environment variables in the `.env` file:

- `API_KEY`: Secret API key for authentication
- `API_KEY_HEADER`: Header name for API key (default: X-API-Key)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)

### CORS Configuration (Required for Security and Functionality)

**IMPORTANT**: CORS configuration is essential for both security and application functionality. Without proper CORS settings:
- Frontend applications cannot communicate with the API (browser will block requests)
- Security vulnerabilities may arise from overly permissive CORS settings

**CORS Environment Variables**:

- `CORS_ORIGINS`: List of allowed origins for cross-origin requests
  - **Development**: `["*"]` allows all origins (convenient but less secure)
  - **Production**: Specify exact origins, e.g., `["https://yourdomain.com", "https://app.yourdomain.com"]`
  - Example: `CORS_ORIGINS=["https://example.com", "https://app.example.com"]`

- `CORS_ALLOW_CREDENTIALS`: Allow credentials (cookies, auth headers) in cross-origin requests
  - Default: `True`
  - Set to `False` if credentials are not needed

- `CORS_ALLOW_METHODS`: Allowed HTTP methods for cross-origin requests
  - Default: `["*"]` (allows all methods)
  - Production example: `["GET", "POST", "PUT", "DELETE"]`

- `CORS_ALLOW_HEADERS`: Allowed headers in cross-origin requests
  - Default: `["*"]` (allows all headers)
  - Production example: `["X-API-Key", "Content-Type", "Authorization"]`

**Example Production CORS Configuration**:
```bash
CORS_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=["GET", "POST"]
CORS_ALLOW_HEADERS=["X-API-Key", "Content-Type"]
```

## Logging

The application includes comprehensive logging middleware that logs:
- All HTTP requests with method and path
- Response status codes
- Processing time for each request

Logs are written to both:
- **Console**: Real-time log output during development
- **File**: All logs are saved to `app.log` in the project root directory

The log file (`app.log`) is automatically excluded from version control via `.gitignore`.

## Repository

This project is hosted on GitHub:
- **Repository**: [SalesAnalyticsAPI](https://github.com/ilyasyoussefmouhri/SalesAnalyticsAPI)
- **Issues**: [Report Issues](https://github.com/ilyasyoussefmouhri/SalesAnalyticsAPI/issues)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for educational and development purposes.
