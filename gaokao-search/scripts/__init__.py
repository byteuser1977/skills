# scripts/__init__.py
"""
高考志愿搜索工具包
提供阳光高考平台专业搜索及高校招生信息查询功能
"""

__version__ = "1.0.0"
__author__ = "Gaokao Search Team"

from .search_gaokao import GaokaoSearcher, search_gaokao
from .fallback_school_site import fallback_scrape, SchoolSiteScraper
from .utils import (
    RequestUtils,
    PlaywrightUtils,
    DataExporter,
    load_school_nature,
    get_nature_code,
)

__all__ = [
    # 主搜索类
    "GaokaoSearcher",
    "search_gaokao",
    # 兜底抓取
    "fallback_scrape",
    "SchoolSiteScraper",
    # 工具函数
    "RequestUtils",
    "PlaywrightUtils",
    "DataExporter",
    "load_school_nature",
    "get_nature_code",
]
