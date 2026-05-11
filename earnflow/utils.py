"""
EarnFlow 工具函数模块 / Utility Functions Module

提供项目中通用的工具函数，包括ID生成、格式化、趋势计算和终端彩色输出等。
Provides common utility functions used across the project, including ID generation,
formatting, trend calculation, and terminal color output.
"""

from __future__ import annotations

import math
import random
import string
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# ID 生成 / ID Generation
# ============================================================


def generate_id(prefix: str = "id", length: int = 12) -> str:
    """
    生成唯一标识符 / Generate unique identifier

    Args:
        prefix: ID前缀 / ID prefix
        length: 随机部分长度 / Random part length

    Returns:
        格式为 {prefix}_{random_hex} 的唯一ID / Unique ID in format {prefix}_{random_hex}

    Examples:
        >>> generate_id("task")
        'task_a1b2c3d4e5f6'
    """
    random_hex = uuid.uuid4().hex[:length]
    return f"{prefix}_{random_hex}"


# ============================================================
# 时间与日期 / Time & Date
# ============================================================


def get_timestamp() -> float:
    """
    获取当前时间戳 / Get current timestamp

    Returns:
        当前Unix时间戳（秒）/ Current Unix timestamp in seconds
    """
    return time.time()


def get_datetime_str(timestamp: Optional[float] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取格式化的日期时间字符串 / Get formatted datetime string

    Args:
        timestamp: 时间戳（默认当前时间）/ Timestamp (defaults to now)
        fmt: 格式字符串 / Format string

    Returns:
        格式化的日期时间字符串 / Formatted datetime string
    """
    ts = timestamp or time.time()
    return datetime.fromtimestamp(ts).strftime(fmt)


def get_date_str(timestamp: Optional[float] = None) -> str:
    """
    获取日期字符串（YYYY-MM-DD）/ Get date string (YYYY-MM-DD)

    Args:
        timestamp: 时间戳（默认当前时间）/ Timestamp (defaults to now)

    Returns:
        日期字符串 / Date string
    """
    ts = timestamp or time.time()
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def format_duration(seconds: float) -> str:
    """
    格式化时长 / Format duration

    将秒数转换为可读的时间格式。
    Convert seconds to a human-readable time format.

    Args:
        seconds: 秒数 / Number of seconds

    Returns:
        格式化的时长字符串 / Formatted duration string

    Examples:
        >>> format_duration(65)
        '1m 5s'
        >>> format_duration(3665)
        '1h 1m 5s'
    """
    if seconds < 0:
        return "0s"
    if seconds < 60:
        return f"{seconds:.1f}s"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    parts: List[str] = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 and hours == 0:
        parts.append(f"{secs:.0f}s")

    return " ".join(parts)


# ============================================================
# 货币格式化 / Currency Formatting
# ============================================================


def format_currency(
    amount: float,
    currency: str = "CNY",
    show_symbol: bool = True,
) -> str:
    """
    货币金额格式化 / Format currency amount

    Args:
        amount: 金额 / Amount
        currency: 货币类型 / Currency type
        show_symbol: 是否显示货币符号 / Whether to show currency symbol

    Returns:
        格式化的货币字符串 / Formatted currency string

    Examples:
        >>> format_currency(1234.5)
        '¥1,234.50'
        >>> format_currency(100, "USD")
        '$100.00'
    """
    symbols: Dict[str, str] = {
        "CNY": "¥",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
    }
    symbol = symbols.get(currency, f"{currency} ")
    formatted = f"{amount:,.2f}"
    return f"{symbol}{formatted}" if show_symbol else formatted


# ============================================================
# 趋势计算 / Trend Calculation
# ============================================================


def calculate_trend(current: float, previous: float) -> Tuple[float, str]:
    """
    计算环比增长率 / Calculate period-over-period growth rate

    Args:
        current: 当前值 / Current value
        previous: 上期值 / Previous value

    Returns:
        元组：(增长率百分比, 趋势方向) / Tuple: (growth rate percentage, trend direction)
        趋势方向: "up"（上升）, "down"（下降）, "stable"（持平）/ Trend direction

    Examples:
        >>> calculate_trend(150, 100)
        (50.0, 'up')
        >>> calculate_trend(80, 100)
        (-20.0, 'down')
    """
    if previous == 0:
        if current > 0:
            return (100.0, "up")
        return (0.0, "stable")

    rate = ((current - previous) / previous) * 100

    if rate > 0.5:
        direction = "up"
    elif rate < -0.5:
        direction = "down"
    else:
        direction = "stable"

    return (round(rate, 2), direction)


# ============================================================
# 终端彩色输出 / Terminal Color Output
# ============================================================

# ANSI颜色代码 / ANSI color codes
_COLORS: Dict[str, str] = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "underline": "\033[4m",
    "reset": "\033[0m",
}


def color_text(text: str, *colors: str) -> str:
    """
    为文本添加终端颜色 / Add terminal colors to text

    Args:
        text: 要着色的文本 / Text to color
        *colors: 颜色名称（可叠加）/ Color names (can be stacked)

    Returns:
        着色后的文本 / Colored text

    Examples:
        >>> color_text("Hello", "green", "bold")
        '\\033[92m\\033[1mHello\\033[0m'
    """
    color_codes = "".join(_COLORS.get(c, "") for c in colors)
    reset = _COLORS["reset"]
    return f"{color_codes}{text}{reset}"


def print_colored(text: str, *colors: str, end: str = "\n") -> None:
    """
    打印彩色文本 / Print colored text

    Args:
        text: 要打印的文本 / Text to print
        *colors: 颜色名称 / Color names
        end: 结尾字符 / End character
    """
    print(color_text(text, *colors), end=end)


# ============================================================
# 数据验证 / Data Validation
# ============================================================


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证配置字典的有效性 / Validate configuration dictionary

    Args:
        config: 配置字典 / Configuration dictionary

    Returns:
        元组：(是否有效, 错误消息列表) / Tuple: (is_valid, error_messages)
    """
    errors: List[str] = []

    # 检查必需字段 / Check required fields
    required_fields = ["currency", "work_dir", "output_dir"]
    for field_name in required_fields:
        if field_name not in config:
            errors.append(f"Missing required field: {field_name}")

    # 验证并发数 / Validate concurrency
    if "max_concurrent" in config:
        max_c = config["max_concurrent"]
        if not isinstance(max_c, int) or max_c < 1:
            errors.append("max_concurrent must be a positive integer")
        if max_c > 16:
            errors.append("max_concurrent should not exceed 16")

    # 验证货币 / Validate currency
    if "currency" in config:
        valid_currencies = {"CNY", "USD", "EUR", "GBP", "JPY"}
        if config["currency"] not in valid_currencies:
            errors.append(f"currency must be one of: {', '.join(valid_currencies)}")

    # 验证超时 / Validate timeout
    if "task_timeout" in config:
        timeout = config["task_timeout"]
        if not isinstance(timeout, (int, float)) or timeout < 1:
            errors.append("task_timeout must be a positive number")

    return (len(errors) == 0, errors)


def validate_task_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证任务数据的有效性 / Validate task data

    Args:
        data: 任务数据字典 / Task data dictionary

    Returns:
        元组：(是否有效, 错误消息列表) / Tuple: (is_valid, error_messages)
    """
    errors: List[str] = []

    if "title" not in data or not data["title"]:
        errors.append("Task must have a non-empty title")

    if "reward" in data:
        if not isinstance(data["reward"], (int, float)) or data["reward"] < 0:
            errors.append("reward must be a non-negative number")

    if "estimated_time" in data:
        if not isinstance(data["estimated_time"], (int, float)) or data["estimated_time"] < 0:
            errors.append("estimated_time must be a non-negative number")

    return (len(errors) == 0, errors)


# ============================================================
# 数学工具 / Math Utilities
# ============================================================


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    将值限制在指定范围内 / Clamp value to specified range

    Args:
        value: 输入值 / Input value
        min_val: 最小值 / Minimum value
        max_val: 最大值 / Maximum value

    Returns:
        限制后的值 / Clamped value
    """
    return max(min_val, min(max_val, value))


def percentage(value: float, total: float) -> float:
    """
    计算百分比 / Calculate percentage

    Args:
        value: 当前值 / Current value
        total: 总值 / Total value

    Returns:
        百分比值（0-100）/ Percentage value (0-100)
    """
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)


# ============================================================
# 字符串工具 / String Utilities
# ============================================================


def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    截断文本 / Truncate text

    Args:
        text: 输入文本 / Input text
        max_length: 最大长度 / Maximum length
        suffix: 截断后缀 / Truncation suffix

    Returns:
        截断后的文本 / Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def generate_random_text(min_words: int = 5, max_words: int = 15) -> str:
    """
    生成随机模拟文本 / Generate random simulated text

    用于插件系统的模拟输出。
    Used for simulated output in the plugin system.

    Args:
        min_words: 最小单词数 / Minimum word count
        max_words: 最大单词数 / Maximum word count

    Returns:
        随机文本 / Random text
    """
    sample_words = [
        "analysis", "completed", "data", "processed", "results",
        "generated", "report", "review", "quality", "score",
        "optimized", "verified", "validated", "tested", "approved",
        "document", "section", "updated", "improved", "enhanced",
    ]
    word_count = random.randint(min_words, max_words)
    words = random.sample(sample_words, min(word_count, len(sample_words)))
    return " ".join(words)
