"""Data processing functions for sales analytics."""
import logging
import pandas as pd
from io import BytesIO
from fastapi import UploadFile, HTTPException
from schemas import DateRangeStats, SalesAnalytics, ValidationStats, ValidationResults

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

def read_excel_file(file: UploadFile, max_size: int) -> pd.DataFrame:
    """Read and parse Excel file from upload.
    
    Args:
        file: Uploaded file object
        max_size: Maximum allowed file size in bytes
        
    Returns:
        Parsed pandas DataFrame
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
        df = pd.read_excel(BytesIO(contents))
        return df
    except HTTPException:
        logger.error("Error reading Excel file")
        raise HTTPException(status_code=400, detail="Error reading Excel file")
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}")
        raise
    finally:
        file.file.seek(0)


def validate_sales_data(df: pd.DataFrame) -> ValidationResults:
    """Validate sales data quality and return validation results.
    
    Args:
        df: Input DataFrame to validate
        
    Returns:
        ValidationResults model with validation status and quality score
    """
    logger.info(f"Starting validation for DataFrame with {len(df)} rows")

    validation_results = ValidationResults(
        valid=True,
        errors=[],
        warnings=[],
        stats=ValidationStats(total_rows=len(df), total_columns=len(df.columns), missing_values_total=0, duplicate_rows=0, date_range=None)
        quality_score=100.0

    )
    
    # Required columns
    required_columns = ["date", "product", "quantity", "price", "customer"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        error_msg = f"Missing required columns: {', '.join(missing_columns)}"
        logger.error(error_msg)
        validation_results.valid = False
        validation_results.errors.append(error_msg)
        validation_results.quality_score = 0.0
        return validation_results
    
    # Check for empty dataframe
    if df.empty:
        error_msg = "DataFrame is empty"
        logger.error(error_msg)
        validation_results.valid = False
        validation_results.errors.append(error_msg)
        validation_results.quality_score = 0.0
        return validation_results
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        duplicate_pct = (duplicate_count / len(df)) * 100
        warning_msg = f"Found {duplicate_count} duplicate rows ({duplicate_pct:.1f}%)"
        validation_results.warnings.append(warning_msg)
        logger.warning(warning_msg)

    # Check for missing values
    missing_values = df[required_columns].isnull().sum()
    if missing_values.any():
        for col, count in missing_values.items():
            if count > 0:
                percentage = (count / len(df)) * 100
                warning_msg = f"Column '{col}' has {count} missing values ({percentage:.1f}%)"
                validation_results.warnings.append(warning_msg)
                logger.warning(warning_msg)
    
    # Same logic for quantity as for price and date
    # Distinguish between original nulls and conversion failures
    if "quantity" in df.columns:
        try:
            # Count original nulls
            original_nulls = df["quantity"].isnull().sum()
            
            # Test conversion without modifying original
            test_quantity = pd.to_numeric(df["quantity"], errors="coerce")
            
            # Count new nulls created by conversion (Issue #2)
            conversion_failures = test_quantity.isnull().sum() - original_nulls
            
            if conversion_failures > 0:
                percentage = (conversion_failures / len(df)) * 100
                warning_msg = f"{conversion_failures} quantity values are not numeric ({percentage:.1f}%)"
                validation_results.warnings.append(warning_msg)
                logger.warning(warning_msg)
            if original_nulls > 0:
                percentage = (original_nulls / len(df)) * 100
                warning_msg = f"{original_nulls} quantity values are missing/null ({percentage:.1f}%)"
                validation_results.warnings.append(warning_msg)
                logger.warning(warning_msg)
                
            # Check for zero or negative quantities
            valid_quantities = test_quantity.dropna()
            if len(valid_quantities) > 0:
                invalid_quantity_count = (valid_quantities <= 0).sum()
                if invalid_quantity_count > 0:
                    percentage = (invalid_quantity_count / len(df)) * 100
                    warning_msg = f"{invalid_quantity_count} quantities are zero or negative ({percentage:.1f}%)"
                    validation_results.warnings.append(warning_msg)
                    logger.warning(warning_msg)
        
        except Exception as e:
            error_msg = f"Error validating quantity: {str(e)}"
            validation_results.errors.append(error_msg)
            logger.error(error_msg)
    
    
    
    if "price" in df.columns:
        try:
            # Count original nulls
            original_nulls = df["price"].isnull().sum()
            
            # Test conversion without modifying original
            test_price = pd.to_numeric(df["price"], errors="coerce")
            
            # Count new nulls created by conversion
            conversion_failures = test_price.isnull().sum() - original_nulls
            
            # Specific message with count
            if conversion_failures > 0:
                percentage = (conversion_failures / len(df)) * 100
                warning_msg = f"{conversion_failures} prices could not be parsed ({percentage:.1f}%)"
                validation_results.warnings.append(warning_msg)
                logger.warning(warning_msg)
            if original_nulls > 0:
                percentage = (original_nulls / len(df)) * 100
                warning_msg = f"{original_nulls} prices are missing/null ({percentage:.1f}%)"
                validation_results.warnings.append(warning_msg)
                logger.warning(warning_msg)

                
            # Check for zero or negative prices
            valid_prices = test_price.dropna()
            if len(valid_prices) > 0:
                negative_price_count = (valid_prices < 0).sum()
                if negative_price_count > 0:
                    percentage = (negative_price_count / len(df)) * 100
                    warning_msg = f"{negative_price_count} prices are negative ({percentage:.1f}%)"
                    validation_results.warnings.append(warning_msg)
                    logger.warning(warning_msg)
                    
        except Exception as e:
            error_msg = f"Error validating price: {str(e)}"
            validation_results.errors.append(error_msg)
            logger.error(error_msg)
    
    # Validate date format
    date_range_stats = None
    if "date" in df.columns:
        try:
            # Count original nulls
            original_nulls = df["date"].isnull().sum()
            
            # Test conversion without modifying original
            test_dates = pd.to_datetime(df["date"], errors="coerce")
            
            # Count new nulls created by conversion (Issue #2)
            conversion_failures = test_dates.isnull().sum() - original_nulls
            
            # Specific message with count
            if conversion_failures > 0:
                percentage = (conversion_failures / len(df)) * 100
                warning_msg = f"{conversion_failures} dates could not be parsed ({percentage:.1f}%)"
                validation_results.warnings.append(warning_msg)
                logger.warning(warning_msg)
            if original_nulls > 0:
                percentage = (original_nulls / len(df)) * 100
                warning_msg = f"{original_nulls} dates are missing/null ({percentage:.1f}%)"
                validation_results.warnings.append(warning_msg)
                logger.warning(warning_msg)


            # Calculate date range
            valid_dates = test_dates.dropna()
            if len(valid_dates) > 0:
                min_date = valid_dates.min()
                max_date = valid_dates.max()
                
                date_range_stats = DateRangeStats(
                    min=str(min_date.date()),
                    max=str(max_date.date()),
                    span_days=(max_date - min_date).days
                )
                
        except Exception as e:
            warning_msg = f"Date validation warning: {str(e)}"
            validation_results.warnings.append(warning_msg)
            logger.warning(warning_msg)


    # Calculate basic stats
    validation_results.stats = ValidationStats(
        total_rows=len(df),
        total_columns=len(df.columns),
        missing_values_total=int(df.isnull().sum().sum()),
        duplicate_rows=int(duplicate_count),
        date_range=date_range_stats
    )
    
    if validation_results.errors:
        validation_results.valid = False
    
    # Calculate quality score
    quality_score = calculate_quality_score(
        total_rows=len(df),
        errors_count=len(validation_results.errors),
        warnings_count=len(validation_results.warnings),
        missing_total=validation_results.stats.missing_values_total,
        duplicates=duplicate_count
    )
    
    # Update quality score
    validation_results.quality_score = quality_score

    return validation_results


def calculate_quality_score(
    total_rows: int,
    errors_count: int,
    warnings_count: int,
    missing_total: int,
    duplicates: int
) -> float:
    """Calculate quality score based on validation results.
    
    Scoring breakdown:
    - Start at 100
    - Deduct for errors (critical issues)
    - Deduct for warnings (minor issues)
    - Deduct for missing values
    - Deduct for duplicates
    
    Args:
        total_rows: Total number of rows
        errors_count: Number of critical errors
        warnings_count: Number of warnings
        missing_total: Total missing values
        duplicates: Number of duplicate rows
        
    Returns:
        Score from 0 (terrible) to 100 (perfect)
    """
    if total_rows == 0:
        return 0.0
    
    score = 100.0
    
    # Critical errors drop score significantly
    if errors_count > 0:
        return 0.0  # Any errors = failed validation
    
    # Deduct for warnings (5 points each, max 50 points)
    score -= min(warnings_count * 5, 50)
    
    # Deduct for missing values as percentage
    missing_percentage = (missing_total / (total_rows * 5)) * 100  # 5 = required columns
    score -= min(missing_percentage, 30)  # Max 30 points deducted
    
    # Deduct for duplicates as percentage
    if duplicates > 0:
        duplicate_percentage = (duplicates / total_rows) * 100
        score -= min(duplicate_percentage, 20)  # Max 20 points deducted
    
    return max(0.0, min(100.0, round(score, 1))) # Make sure score is between 0 and 100


def calculate_sales_analytics(df: pd.DataFrame) -> SalesAnalytics:
    """Calculate comprehensive sales analytics.
    
    Args:
        df: Input DataFrame with sales data
        
    Returns:
        SalesAnalytics model with comprehensive sales analytics
    """
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
    
    total_revenue = df["revenue"].sum()
    total_quantity = df["quantity"].sum()
    avg_order_value = total_revenue / len(df)
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
