"""
Statistics API endpoints

Handles system statistics and performance analytics.
"""

import logging
from fastapi import APIRouter, HTTPException, Query, status

from models.schemas import (
    StatisticsResponse,
    PerformanceTrendResponse,
    ErrorResponse
)
from services.statistics_service import get_statistics_service
from utils.response import error_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=StatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get system statistics",
    description="Get comprehensive system statistics and performance analytics",
    responses={
        200: {"description": "Statistics retrieved successfully", "model": StatisticsResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_statistics():
    """
    Get comprehensive system statistics (leaching-efficiency based).

    返回内容包含：
    - **Summary**：推荐数量、形成率、最大浸出效率均值/中位数、平均测量条数
    - **By Material**：推荐数量的材料分布（计数）
    - **By Status**：状态分布
    - **Performance Trend**：按日聚合的形成率与最大浸出效率均值/中位数
    - **Top Formulations**：按平均最大浸出效率排序的前 10 配方
    - **Target Material Stats**：按目标物质分组的形成率与浸出效率统计

    **Example Response**:
    ```json
    {
      "status": "success",
      "message": "Statistics retrieved successfully. Total: 150 recommendations, Avg Performance: 7.2/10.0",
      "data": {
        "summary": {
          "total_recommendations": 150,
          "pending_experiments": 45,
          "completed_experiments": 95,
          "cancelled": 10,
          "liquid_formation_rate": 0.89,
          "max_leaching_efficiency_mean": 42.1,
          "max_leaching_efficiency_median": 38.0,
          "measurement_rows_mean": 5.2
        },
        "by_material": {
          "cellulose": 80,
          "lignin": 45,
          "chitin": 25
        },
        "by_status": {
          "PENDING": 45,
          "COMPLETED": 95,
          "CANCELLED": 10
        },
        "performance_trend": [
          {
            "date": "2025-10-14",
            "max_leaching_efficiency_mean": 42.0,
            "max_leaching_efficiency_median": 38.0,
            "experiment_count": 12,
            "liquid_formation_rate": 0.92
          },
          {
            "date": "2025-10-15",
          "max_leaching_efficiency_mean": 55.0,
          "max_leaching_efficiency_median": 50.0,
          "experiment_count": 15,
          "liquid_formation_rate": 0.87
        }
      ],
        "top_formulations": [
          {
            "formulation": "Choline chloride:Urea (1:2)",
            "avg_max_leaching_efficiency": 68.5,
            "success_count": 12
          },
          {
            "formulation": "Choline chloride:Glycerol (1:2)",
            "avg_performance": 8.2,
            "success_count": 8
          }
        ]
      }
    }
    ```

    **Notes**:
    - 全部指标基于浸出效率（%）与是否形成液体
    - Performance trend / target material stats 仅包含已完成且有实验结果的记录
    """
    try:
        # Get statistics from service
        stats_service = get_statistics_service()
        stats_data = stats_service.get_statistics()

        # Return success response
        return StatisticsResponse(
            status="success",
            message=(
                f"Statistics retrieved successfully. "
                f"Total: {stats_data.summary.total_recommendations} recommendations."
            ),
            data=stats_data
        )

    except RuntimeError as e:
        logger.error(f"Failed to retrieve statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(message=str(e))
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(message=f"Unexpected error: {str(e)}")
        )


@router.get(
    "/performance-trend",
    response_model=PerformanceTrendResponse,
    status_code=status.HTTP_200_OK,
    summary="Get performance trend",
    description="Get performance trend for a specific date range",
    responses={
        200: {"description": "Performance trend retrieved successfully", "model": PerformanceTrendResponse},
        400: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_performance_trend(
    start_date: str = Query(
        ...,
        description="Start date in ISO format (YYYY-MM-DD)",
        example="2025-10-01"
    ),
    end_date: str = Query(
        ...,
        description="End date in ISO format (YYYY-MM-DD)",
        example="2025-10-16"
    )
):
    """
    Get performance trend for a specific date range.

    Returns daily aggregated performance metrics for completed experiments within the date range.

    **Query Parameters**:
    - **start_date** (required): Start date in ISO format (YYYY-MM-DD)
    - **end_date** (required): End date in ISO format (YYYY-MM-DD)

    **Example Request**:
    ```
    GET /api/v1/statistics/performance-trend?start_date=2025-10-01&end_date=2025-10-16
    ```

    **Example Response**:
    ```json
    {
      "status": "success",
      "message": "Performance trend retrieved: 15 data points from 2025-10-01 to 2025-10-16",
      "data": [
        {
          "date": "2025-10-01",
          "max_leaching_efficiency_mean": 40.5,
          "max_leaching_efficiency_median": 38.0,
          "experiment_count": 8,
          "liquid_formation_rate": 0.88
        },
        {
          "date": "2025-10-02",
          "max_leaching_efficiency_mean": 42.1,
          "max_leaching_efficiency_median": 41.0,
          "experiment_count": 10,
          "liquid_formation_rate": 0.90
        }
      ]
    }
    ```

    **Notes**:
    - Only completed experiments are included in the trend
    - Dates with no completed experiments are omitted from results
    - start_date must be before or equal to end_date
    - Performance metrics are calculated as daily averages

    **Validation Rules**:
    - Date format must be YYYY-MM-DD (ISO format)
    - start_date must be before or equal to end_date
    """
    try:
        # Get performance trend from service
        stats_service = get_statistics_service()
        trend_data = stats_service.get_performance_trend(start_date, end_date)

        # Return success response
        return PerformanceTrendResponse(
            status="success",
            message=(
                f"Performance trend retrieved: {len(trend_data)} data points "
                f"from {start_date} to {end_date}"
            ),
            data=trend_data
        )

    except ValueError as e:
        # Validation error
        error_msg = str(e)
        logger.warning(f"Validation error: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message=error_msg)
        )

    except RuntimeError as e:
        logger.error(f"Failed to retrieve performance trend: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(message=str(e))
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(message=f"Unexpected error: {str(e)}")
        )
