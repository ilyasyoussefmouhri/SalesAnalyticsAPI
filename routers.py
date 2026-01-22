"""API routes for the FastAPI Sales Analytics application."""
import logging
from datetime import datetime
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from config import settings
from processing import read_csv_file, validate_sales_data, calculate_sales_analytics
from schemas import (
    HealthResponse,
    QuickStatsResponse,
    ValidateResponse,
    AnalyzeResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# API Key Authentication
async def verify_api_key(request: Request):
    """Verify API key from request headers."""
    api_key = request.headers.get(settings.api_key_header)
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key missing. Please provide X-API-Key header."
        )
    
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key."
        )
    
    return api_key


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.app_version
    )


@router.post("/quick-stats", response_model=QuickStatsResponse)
async def quick_stats(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """Get quick statistics about the uploaded file."""
    logger.info(f"Quick stats requested for file: {file.filename}")
    
    # SECURITY: Validate file size before processing to prevent DoS attacks
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file.size} bytes) exceeds maximum allowed size ({settings.max_file_size} bytes)"
        )
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )
    
    try:
        df = read_csv_file(file, settings.max_file_size)
        
        return QuickStatsResponse(
            filename=file.filename,
            file_size=file.size,
            rows=len(df),
            columns=len(df.columns),
            column_names=list(df.columns),
            data_types={col: str(dtype) for col, dtype in df.dtypes.items()},
            sample_data=df.head(5).to_dict(orient="records")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing quick stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/validate", response_model=ValidateResponse)
async def validate_data(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """Validate data quality of the uploaded sales file."""
    logger.info(f"Validation requested for file: {file.filename}")
    
    # SECURITY: Validate file size before processing to prevent DoS attacks
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file.size} bytes) exceeds maximum allowed size ({settings.max_file_size} bytes)"
        )
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )
    
    try:
        df = read_csv_file(file, settings.max_file_size)
        validation_results = validate_sales_data(df)
        
        return ValidateResponse(
            filename=file.filename,
            validation=validation_results,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validating file: {str(e)}"
        )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_sales(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """Perform full sales analysis on the uploaded file."""
    logger.info(f"Full analysis requested for file: {file.filename}")
    
    # SECURITY: Validate file size before processing to prevent DoS attacks
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file.size} bytes) exceeds maximum allowed size ({settings.max_file_size} bytes)"
        )
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )
    
    try:
        df = read_csv_file(file, settings.max_file_size)
        
        # First validate the data
        validation_results = validate_sales_data(df)
        
        if not validation_results["valid"]:
            error_response = ErrorResponse(
                error="Data validation failed",
                validation=validation_results,
                timestamp=datetime.now().isoformat()
            )
            return JSONResponse(
                status_code=400,
                content=error_response.model_dump()
            )
        
        # Calculate analytics
        analytics = calculate_sales_analytics(df)
        
        return AnalyzeResponse(
            filename=file.filename,
            validation=validation_results,
            analytics=analytics,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing file: {str(e)}"
        )
