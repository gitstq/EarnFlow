"""
EarnFlow - 轻量级AI自动化任务收益引擎
Lightweight AI Automated Task Earning Engine

一个零外部依赖的CLI工具，用于管理AI自动化任务的执行和收益追踪。
A CLI tool with zero external dependencies for managing AI automated task execution and earnings tracking.
"""

__version__ = "1.0.0"
__author__ = "EarnFlow Team"
__description__ = "Lightweight AI Automated Task Earning Engine"

from earnflow.models import (
    Task,
    TaskResult,
    EarningRecord,
    TaskTemplate,
    DashboardStats,
    TaskStatus,
    TaskPriority,
    TaskCategory,
)

__all__ = [
    "__version__",
    "Task",
    "TaskResult",
    "EarningRecord",
    "TaskTemplate",
    "DashboardStats",
    "TaskStatus",
    "TaskPriority",
    "TaskCategory",
]
