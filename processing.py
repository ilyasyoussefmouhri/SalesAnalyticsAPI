"""Data processing functions for sales analytics."""
import logging
import pandas as pd
from io import BytesIO
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)


def read_csv_file(file: UploadFile, max_size: int) -> pd.DataFrame:
    """Read and parse CSV file from upload.
    
    Args:
        file: Uploaded file object
        max_size: Maximum allowed file size in bytes
        
    Returns:
        Parsed pandas DataFrame
        
    Raises:
        HTTPException: If file size exceeds limit or reading fails
    """
    # SECURITY: Validate file size before reading into memory to prevent DoS attacks
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file.size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )
    
    try:
        contents = file.file.read()
        
        # Additional check: validate actual content size (file.size might be None)
        if len(contents) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({len(contents)} bytes) exceeds maximum allowed size ({max_size} bytes)"
            )
        
        df = pd.read_csv(BytesIO(contents))
        return df
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error reading CSV file: {str(e)}"
        )
    finally:
        file.file.seek(0)


def validate_sales_data(df: pd.DataFrame) -> dict:
    """Validate sales data quality and return validation results.
    
    Note: Works on a copy of the DataFrame to avoid side effects.
    
    Args:
        df: Input DataFrame to validate
        
    Returns:
        Dictionary with validation results (valid, errors, warnings, stats)
    """
    # SECURITY: Work on a copy to avoid mutating the input DataFrame
    # This prevents side effects and unexpected behavior
    df = df.copy()
    
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {}
    }
    
    # Required columns
    required_columns = ["date", "product", "quantity", "price", "customer"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        validation_results["valid"] = False
        validation_results["errors"].append(
            f"Missing required columns: {', '.join(missing_columns)}"
        )
        return validation_results
    
    # Check for empty dataframe
    if df.empty:
        validation_results["valid"] = False
        validation_results["errors"].append("DataFrame is empty")
        return validation_results
    
    # Check for missing values
    missing_values = df[required_columns].isnull().sum()
    if missing_values.any():
        for col, count in missing_values.items():
            if count > 0:
                validation_results["warnings"].append(
                    f"Column '{col}' has {count} missing values"
                )
    
    # Validate data types (working on copy, so mutations are safe)
    if "quantity" in df.columns:
        try:
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
            if df["quantity"].isnull().any():
                validation_results["warnings"].append(
                    "Some quantity values could not be converted to numeric"
                )
        except Exception as e:
            validation_results["errors"].append(f"Error validating quantity: {str(e)}")
    
    if "price" in df.columns:
        try:
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            if df["price"].isnull().any():
                validation_results["warnings"].append(
                    "Some price values could not be converted to numeric"
                )
        except Exception as e:
            validation_results["errors"].append(f"Error validating price: {str(e)}")
    
    # Validate date format
    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            invalid_dates = df["date"].isnull().sum()
            if invalid_dates > 0:
                validation_results["warnings"].append(
                    f"{invalid_dates} dates could not be parsed"
                )
        except Exception as e:
            validation_results["warnings"].append(f"Date validation warning: {str(e)}")
    
    # Calculate basic stats
    validation_results["stats"] = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "date_range": {
            "min": str(df["date"].min()) if "date" in df.columns and not df["date"].isnull().all() else None,
            "max": str(df["date"].max()) if "date" in df.columns and not df["date"].isnull().all() else None
        } if "date" in df.columns else None
    }
    
    if validation_results["errors"]:
        validation_results["valid"] = False
    
    return validation_results


def calculate_sales_analytics(df: pd.DataFrame) -> dict:
    """Calculate comprehensive sales analytics.
    
    Note: Works on a copy of the DataFrame to avoid side effects.
    
    Args:
        df: Input DataFrame with sales data
        
    Returns:
        Dictionary with comprehensive sales analytics
    """
    # SECURITY: Work on a copy to avoid mutating the input DataFrame
    df = df.copy()
    
    # Ensure numeric columns
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    
    # Calculate revenue
    df["revenue"] = df["quantity"] * df["price"]
    
    # Total revenue
    total_revenue = df["revenue"].sum()
    
    # Total quantity sold
    total_quantity = df["quantity"].sum()
    
    # Average order value
    avg_order_value = df["revenue"].mean() if len(df) > 0 else 0
    
    # Top products by revenue
    top_products_revenue = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .to_dict()
    )
    
    # Top products by quantity
    top_products_quantity = (
        df.groupby("product")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .to_dict()
    )
    
    # Customer segments (by total revenue)
    customer_revenue = df.groupby("customer")["revenue"].sum().sort_values(ascending=False)
    
    # Segment customers
    if len(customer_revenue) > 0:
        high_value_threshold = customer_revenue.quantile(0.8)
        medium_value_threshold = customer_revenue.quantile(0.5)
        
        customer_segments = {
            "high_value": customer_revenue[customer_revenue >= high_value_threshold].to_dict(),
            "medium_value": customer_revenue[
                (customer_revenue >= medium_value_threshold) & 
                (customer_revenue < high_value_threshold)
            ].to_dict(),
            "low_value": customer_revenue[customer_revenue < medium_value_threshold].to_dict()
        }
    else:
        customer_segments = {"high_value": {}, "medium_value": {}, "low_value": {}}
    
    # Time-based analysis
    time_analysis = {}
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df_with_dates = df.dropna(subset=["date"])
        
        if len(df_with_dates) > 0:
            # Daily revenue
            daily_revenue = (
                df_with_dates.groupby(df_with_dates["date"].dt.date)["revenue"]
                .sum()
                .to_dict()
            )
            time_analysis["daily_revenue"] = {str(k): float(v) for k, v in daily_revenue.items()}
            
            # Monthly revenue
            monthly_revenue = (
                df_with_dates.groupby(df_with_dates["date"].dt.to_period("M"))["revenue"]
                .sum()
                .to_dict()
            )
            time_analysis["monthly_revenue"] = {str(k): float(v) for k, v in monthly_revenue.items()}
    
    return {
        "total_revenue": float(total_revenue),
        "total_quantity": float(total_quantity),
        "total_orders": len(df),
        "average_order_value": float(avg_order_value),
        "top_products_by_revenue": {k: float(v) for k, v in top_products_revenue.items()},
        "top_products_by_quantity": {k: float(v) for k, v in top_products_quantity.items()},
        "customer_segments": {
            "high_value": {k: float(v) for k, v in customer_segments["high_value"].items()},
            "medium_value": {k: float(v) for k, v in customer_segments["medium_value"].items()},
            "low_value": {k: float(v) for k, v in customer_segments["low_value"].items()}
        },
        "time_analysis": time_analysis
    }
