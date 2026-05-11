"""
EarnFlow 数据模型模块 / Data Models Module

定义任务引擎中使用的所有核心数据结构，包括任务、结果、收益记录、模板和统计信息。
Defines all core data structures used in the task engine, including tasks, results,
earning records, templates, and statistics.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# 枚举类型 / Enum Types
# ============================================================


class TaskStatus(Enum):
    """任务状态枚举 / Task status enumeration"""
    PENDING = "pending"          # 等待中 / Waiting
    RUNNING = "running"          # 运行中 / Running
    COMPLETED = "completed"      # 已完成 / Completed
    FAILED = "failed"            # 已失败 / Failed
    SKIPPED = "skipped"          # 已跳过 / Skipped


class TaskPriority(Enum):
    """任务优先级枚举 / Task priority enumeration"""
    LOW = "low"                  # 低优先级 / Low
    MEDIUM = "medium"            # 中优先级 / Medium
    HIGH = "high"                # 高优先级 / High
    URGENT = "urgent"            # 紧急 / Urgent


class TaskCategory(Enum):
    """任务分类枚举 / Task category enumeration"""
    CONTENT_GEN = "content_gen"      # 内容生成 / Content Generation
    DATA_LABEL = "data_label"        # 数据标注 / Data Labeling
    TRANSLATION = "translation"      # 翻译 / Translation
    CODE_REVIEW = "code_review"      # 代码审查 / Code Review
    QA_TEST = "qa_test"              # 质量测试 / QA Testing
    RESEARCH = "research"            # 研究调查 / Research
    OTHER = "other"                  # 其他 / Other


# 优先级权重映射 / Priority weight mapping
PRIORITY_WEIGHTS: Dict[TaskPriority, int] = {
    TaskPriority.LOW: 1,
    TaskPriority.MEDIUM: 2,
    TaskPriority.HIGH: 3,
    TaskPriority.URGENT: 4,
}


# ============================================================
# 数据类 / Data Classes
# ============================================================


@dataclass
class Task:
    """
    任务模型 / Task Model

    表示一个可执行的任务，包含任务的元数据、状态和执行结果。
    Represents an executable task with metadata, status, and execution result.

    Attributes:
        id: 任务唯一标识符 / Unique task identifier
        title: 任务标题 / Task title
        description: 任务描述 / Task description
        category: 任务分类 / Task category
        priority: 任务优先级 / Task priority
        reward: 任务奖励金额 / Task reward amount
        estimated_time: 预估执行时间（秒）/ Estimated execution time in seconds
        tags: 任务标签列表 / Task tag list
        created_at: 创建时间戳 / Creation timestamp
        status: 任务状态 / Task status
        result: 任务执行结果 / Task execution result
    """
    id: str = ""
    title: str = ""
    description: str = ""
    category: TaskCategory = TaskCategory.OTHER
    priority: TaskPriority = TaskPriority.MEDIUM
    reward: float = 0.0
    estimated_time: int = 60
    tags: List[str] = field(default_factory=list)
    created_at: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None

    def __post_init__(self) -> None:
        """初始化后处理：设置默认值 / Post-initialization: set defaults"""
        if not self.id:
            self.id = self._generate_id()
        if not self.created_at:
            self.created_at = time.time()

    @staticmethod
    def _generate_id() -> str:
        """生成任务ID / Generate task ID"""
        import uuid
        return f"task_{uuid.uuid4().hex[:12]}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 / Convert to dictionary"""
        data = asdict(self)
        data["category"] = self.category.value
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        if self.result:
            data["result"] = self.result.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """从字典创建任务 / Create task from dictionary"""
        data = data.copy()
        if "category" in data and isinstance(data["category"], str):
            data["category"] = TaskCategory(data["category"])
        if "priority" in data and isinstance(data["priority"], str):
            data["priority"] = TaskPriority(data["priority"])
        if "status" in data and isinstance(data["status"], str):
            data["status"] = TaskStatus(data["status"])
        if "result" in data and isinstance(data["result"], dict):
            data["result"] = TaskResult.from_dict(data["result"])
        return cls(**data)


@dataclass
class TaskResult:
    """
    任务执行结果 / Task Execution Result

    记录任务执行后的输出、收益、耗时和质量评分。
    Records the output, earnings, duration, and quality score after task execution.

    Attributes:
        task_id: 关联任务ID / Associated task ID
        output: 任务输出内容 / Task output content
        earnings: 实际收益金额 / Actual earnings amount
        duration: 实际执行时长（秒）/ Actual execution duration in seconds
        quality_score: 质量评分（0-100）/ Quality score (0-100)
    """
    task_id: str = ""
    output: str = ""
    earnings: float = 0.0
    duration: float = 0.0
    quality_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 / Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskResult:
        """从字典创建结果 / Create result from dictionary"""
        return cls(**data)


@dataclass
class EarningRecord:
    """
    收益记录 / Earning Record

    记录每笔收益的详细信息。
    Records detailed information for each earning.

    Attributes:
        id: 记录唯一标识符 / Unique record identifier
        task_id: 关联任务ID / Associated task ID
        amount: 收益金额 / Earning amount
        currency: 货币类型 / Currency type
        timestamp: 收益时间戳 / Earning timestamp
        category: 任务分类 / Task category
    """
    id: str = ""
    task_id: str = ""
    amount: float = 0.0
    currency: str = "CNY"
    timestamp: float = 0.0
    category: str = "other"

    def __post_init__(self) -> None:
        """初始化后处理 / Post-initialization"""
        if not self.id:
            import uuid
            self.id = f"earn_{uuid.uuid4().hex[:12]}"
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 / Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EarningRecord:
        """从字典创建记录 / Create record from dictionary"""
        return cls(**data)


@dataclass
class TaskTemplate:
    """
    任务模板 / Task Template

    定义可复用的任务模板，用于快速创建同类任务。
    Defines reusable task templates for quickly creating similar tasks.

    Attributes:
        name: 模板名称 / Template name
        description: 模板描述 / Template description
        category: 任务分类 / Task category
        base_reward: 基础奖励 / Base reward
        steps: 执行步骤列表 / Execution step list
        required_tags: 必需标签 / Required tags
    """
    name: str = ""
    description: str = ""
    category: str = "other"
    base_reward: float = 0.0
    steps: List[str] = field(default_factory=list)
    required_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 / Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskTemplate:
        """从字典创建模板 / Create template from dictionary"""
        return cls(**data)

    def create_task(
        self,
        title: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        reward_multiplier: float = 1.0,
        extra_tags: Optional[List[str]] = None,
    ) -> Task:
        """
        从模板创建任务 / Create a task from this template

        Args:
            title: 自定义标题（默认使用模板名称）/ Custom title (defaults to template name)
            priority: 任务优先级 / Task priority
            reward_multiplier: 奖励倍率 / Reward multiplier
            extra_tags: 额外标签 / Extra tags

        Returns:
            创建的任务实例 / Created task instance
        """
        tags = list(self.required_tags) + (extra_tags or [])
        return Task(
            title=title or self.name,
            description=self.description,
            category=TaskCategory(self.category),
            priority=priority,
            reward=self.base_reward * reward_multiplier,
            tags=tags,
        )


@dataclass
class DashboardStats:
    """
    仪表盘统计数据 / Dashboard Statistics

    聚合展示收益和任务执行的整体统计信息。
    Aggregated statistics for earnings and task execution overview.

    Attributes:
        total_earnings: 总收益 / Total earnings
        total_tasks: 总任务数 / Total task count
        success_rate: 成功率（0-100）/ Success rate (0-100)
        avg_reward: 平均奖励 / Average reward
        category_breakdown: 分类收益明细 / Category earnings breakdown
        daily_trend: 每日趋势数据 / Daily trend data
    """
    total_earnings: float = 0.0
    total_tasks: int = 0
    success_rate: float = 0.0
    avg_reward: float = 0.0
    category_breakdown: Dict[str, float] = field(default_factory=dict)
    daily_trend: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 / Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DashboardStats:
        """从字典创建统计 / Create stats from dictionary"""
        return cls(**data)
