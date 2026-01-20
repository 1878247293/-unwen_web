"""
统一响应格式工具
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200
) -> dict:
    """成功响应"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "success": True
    }


def error_response(
    message: str = "操作失败",
    code: int = 400,
    data: Any = None
) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "success": False
    }


class ResponseCode:
    """响应状态码"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
