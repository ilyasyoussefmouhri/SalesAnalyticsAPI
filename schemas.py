"""Pydantic models for request/response schemas."""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: str
    version: str

class DateRangeStats(BaseModel):
    """Statistics about date range in the data"""
    min: str
    max: str
    span_days: int = Field(description="Number of days between min and max date")

class ValidationStats(BaseModel):
    """Statistics about the validated data"""
    total_rows: int = Field(description="Total rows in input data")
    total_columns: int = Field(description="Total columns in input data")
    missing_values_total: int = Field(description="Total missing values across all columns in input data")
    duplicate_rows: int = Field(description="Number of duplicate rows in input data")
    date_range: Optional[DateRangeStats] = Field(default=None, description="Date range if date column exists in input data")


class ValidationResults(BaseModel):
    """Complete validation results with quality score"""
    valid: bool = Field(description="Whether data passes validation")
    errors: list[str] = Field(default_factory=list, description="Critical errors that fail validation")
    warnings: list[str] = Field(default_factory=list, description="Non-critical issues")
    stats: ValidationStats
    quality_score: float = Field(ge=0, le=100, description="Overall data quality score (0-100)")




class QuickStatsResponse(BaseModel):
    """Quick stats response schema."""
    filename: str
    file_size: Optional[int]
    rows: int
    columns: int
    column_names: List[str]
    data_types: Dict[str, str]
    sample_data: List[Dict[str, Any]]


class ValidateResponse(BaseModel):
    """Data validation response schema."""
    filename: str
    validation: ValidationResult
    timestamp: str


class CustomerSegments(BaseModel):
    """Customer segments schema."""
    high_value: Dict[str, float]
    medium_value: Dict[str, float]
    low_value: Dict[str, float]


class TimeAnalysis(BaseModel):
    """Time-based analysis schema."""
    daily_revenue: Optional[Dict[str, float]] = None
    monthly_revenue: Optional[Dict[str, float]] = None


class SalesAnalytics(BaseModel):
    """Sales analytics schema."""
    total_revenue: float
    total_quantity: float
    total_orders: int
    average_order_value: float
    top_products_by_revenue: Dict[str, float]
    top_products_by_quantity: Dict[str, float]
    customer_segments: CustomerSegments
    time_analysis: TimeAnalysis


class AnalyzeResponse(BaseModel):
    """Full analysis response schema."""
    filename: str
    validation: ValidationResult
    analytics: SalesAnalytics
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    validation: ValidationResult
    timestamp: str
