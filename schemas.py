"""Pydantic models for request/response schemas."""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: str
    version: str


class ValidationStats(BaseModel):
    """Validation statistics schema."""
    total_rows: int
    total_columns: int
    columns: List[str]
    date_range: Optional[Dict[str, Optional[str]]] = None


class ValidationResult(BaseModel):
    """Data validation result schema."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    stats: ValidationStats


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
