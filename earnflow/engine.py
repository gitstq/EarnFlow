"""
EarnFlow 核心任务引擎模块 / Core Task Engine Module

提供任务队列管理、并发执行、超时控制和结果收集等核心功能。
使用threading实现并发，支持任务生命周期管理。
Provides task queue management, concurrent execution, timeout control, and result collection.
Uses threading for concurrency with full task lifecycle management.
"""

from __future__ import annotations

import json
import os
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError as FuturesTimeoutError
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

from earnflow.config import ConfigManager
from earnflow.models import (
    Task,
    TaskResult,
    TaskStatus,
    TaskPriority,
    TaskTemplate,
    PRIORITY_WEIGHTS,
)
from earnflow.plugins import PluginRegistry
from earnflow.tracker import EarningTracker
from earnflow.utils import color_text, format_duration, generate_id


# ============================================================
# 进度回调类型 / Progress Callback Types
# ========================================================

ProgressCallback = Callable[[Task, str], None]
"""进度回调函数类型: (task, message) -> None / Progress callback type"""


# ============================================================
# 任务引擎 / Task Engine
# ============================================================


class TaskEngine:
    """
    核心任务引擎 / Core Task Engine

    管理任务的完整生命周期：创建 -> 匹配 -> 排队 -> 执行 -> 完成。
    Manages the complete task lifecycle: create -> match -> queue -> execute -> complete.

    Attributes:
        config: 配置管理器 / Configuration manager
        registry: 插件注册表 / Plugin registry
        tracker: 收益追踪器 / Earnings tracker
        queue: 任务队列 / Task queue
        completed_tasks: 已完成任务列表 / Completed task list
        failed_tasks: 失败任务列表 / Failed task list
    """

    def __init__(
        self,
        config: Optional[ConfigManager] = None,
        registry: Optional[PluginRegistry] = None,
        tracker: Optional[EarningTracker] = None,
    ) -> None:
        """
        初始化任务引擎 / Initialize task engine

        Args:
            config: 配置管理器（可选，自动创建）/ Config manager (optional, auto-created)
            registry: 插件注册表（可选，自动创建）/ Plugin registry (optional, auto-created)
            tracker: 收益追踪器（可选，自动创建）/ Earnings tracker (optional, auto-created)
        """
        self.config = config or ConfigManager()
        self.registry = registry or PluginRegistry()
        self.tracker = tracker or EarningTracker(
            currency=self.config.get("currency", "CNY")
        )

        # 任务队列 / Task queue
        self._queue: Deque[Task] = deque()
        self._lock = threading.Lock()

        # 结果存储 / Result storage
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        self.all_tasks: List[Task] = []

        # 状态 / State
        self._running = False
        self._progress_callbacks: List[ProgressCallback] = []

        # 确保目录存在 / Ensure directories exist
        self.config.ensure_dirs()

    # ========================================================
    # 回调管理 / Callback Management
    # ========================================================

    def on_progress(self, callback: ProgressCallback) -> None:
        """
        注册进度回调 / Register progress callback

        Args:
            callback: 回调函数 / Callback function
        """
        self._progress_callbacks.append(callback)

    def _notify_progress(self, task: Task, message: str) -> None:
        """
        通知所有进度回调 / Notify all progress callbacks

        Args:
            task: 任务 / Task
            message: 进度消息 / Progress message
        """
        for callback in self._progress_callbacks:
            try:
                callback(task, message)
            except Exception:
                pass  # 回调异常不应影响引擎运行 / Callback errors should not affect engine

    # ========================================================
    # 任务管理 / Task Management
    # ========================================================

    def add_task(self, task: Task) -> str:
        """
        添加任务到队列 / Add task to queue

        Args:
            task: 任务实例 / Task instance

        Returns:
            任务ID / Task ID
        """
        with self._lock:
            task.status = TaskStatus.PENDING
            self._queue.append(task)
            self.all_tasks.append(task)
        self._notify_progress(task, "Task added to queue")
        return task.id

    def add_task_from_template(
        self,
        template: TaskTemplate,
        title: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        reward_multiplier: float = 1.0,
        extra_tags: Optional[List[str]] = None,
    ) -> str:
        """
        从模板创建并添加任务 / Create and add task from template

        Args:
            template: 任务模板 / Task template
            title: 自定义标题 / Custom title
            priority: 优先级 / Priority
            reward_multiplier: 奖励倍率 / Reward multiplier
            extra_tags: 额外标签 / Extra tags

        Returns:
            任务ID / Task ID
        """
        task = template.create_task(title, priority, reward_multiplier, extra_tags)
        return self.add_task(task)

    def add_tasks_batch(self, tasks: List[Task]) -> List[str]:
        """
        批量添加任务 / Batch add tasks

        Args:
            tasks: 任务列表 / Task list

        Returns:
            任务ID列表 / Task ID list
        """
        return [self.add_task(task) for task in tasks]

    @property
    def queue_size(self) -> int:
        """
        获取队列中待处理任务数 / Get pending task count in queue

        Returns:
            队列大小 / Queue size
        """
        with self._lock:
            return len(self._queue)

    @property
    def is_running(self) -> bool:
        """
        引擎是否正在运行 / Whether the engine is running

        Returns:
            运行状态 / Running status
        """
        return self._running

    # ========================================================
    # 任务执行 / Task Execution
    # ========================================================

    def _execute_single(self, task: Task) -> TaskResult:
        """
        执行单个任务 / Execute a single task

        Args:
            task: 任务实例 / Task instance

        Returns:
            任务结果 / Task result

        Raises:
            RuntimeError: 没有找到合适的处理器 / No suitable handler found
        """
        task.status = TaskStatus.RUNNING
        self._notify_progress(task, "Task execution started")

        # 查找处理器 / Find handler
        handler = self.registry.get_handler_for_task(task)
        if not handler:
            raise RuntimeError(f"No handler found for category: {task.category.value}")

        # 执行任务 / Execute task
        result = handler.execute(task)
        self._notify_progress(task, "Task execution completed")

        return result

    def _process_task(self, task: Task) -> None:
        """
        处理单个任务（含错误处理和重试）/ Process a single task (with error handling and retry)

        Args:
            task: 任务实例 / Task instance
        """
        retry_limit = self.config.get("retry_limit", 2)
        timeout = self.config.get("task_timeout", 300)

        for attempt in range(1, retry_limit + 2):
            try:
                self._notify_progress(task, f"Attempt {attempt}/{retry_limit + 1}")

                # 使用线程池执行以支持超时 / Use thread pool for timeout support
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future: Future[TaskResult] = executor.submit(self._execute_single, task)
                    result = future.result(timeout=timeout)

                # 执行成功 / Execution succeeded
                task.status = TaskStatus.COMPLETED
                task.result = result

                # 记录收益 / Record earnings
                if result.earnings > 0:
                    self.tracker.add_record(
                        task_id=task.id,
                        amount=result.earnings,
                        category=task.category.value,
                    )

                with self._lock:
                    self.completed_tasks.append(task)

                self._notify_progress(
                    task,
                    f"Completed: earned {result.earnings:.2f}, "
                    f"quality={result.quality_score:.1f}, "
                    f"duration={format_duration(result.duration)}"
                )
                return

            except FuturesTimeoutError:
                self._notify_progress(task, f"Timeout after {timeout}s on attempt {attempt}")
            except Exception as e:
                self._notify_progress(task, f"Error on attempt {attempt}: {str(e)}")

            # 最后一次尝试失败 / Last attempt failed
            if attempt == retry_limit + 1:
                task.status = TaskStatus.FAILED
                with self._lock:
                    self.failed_tasks.append(task)
                self._notify_progress(task, "Task failed after all retries")

    def run(
        self,
        max_tasks: int = 0,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Dict[str, Any]:
        """
        运行任务引擎 / Run the task engine

        从队列中取出任务并并发执行。
        Dequeue tasks and execute them concurrently.

        Args:
            max_tasks: 最大执行任务数（0表示全部）/ Max tasks to execute (0 = all)
            progress_callback: 进度回调 / Progress callback

        Returns:
            执行摘要字典 / Execution summary dictionary
        """
        if self._running:
            return {"status": "already_running", "message": "Engine is already running"}

        if progress_callback:
            self._progress_callbacks.append(progress_callback)

        self._running = True
        start_time = time.time()
        tasks_to_run: List[Task] = []

        # 从队列取出任务 / Dequeue tasks
        with self._lock:
            while self._queue:
                task = self._queue.popleft()
                tasks_to_run.append(task)
                if max_tasks > 0 and len(tasks_to_run) >= max_tasks:
                    break

        if not tasks_to_run:
            self._running = False
            return {"status": "empty", "message": "No tasks in queue", "executed": 0}

        # 按优先级排序 / Sort by priority
        tasks_to_run.sort(
            key=lambda t: PRIORITY_WEIGHTS.get(t.priority, 1),
            reverse=True,
        )

        max_concurrent = self.config.get("max_concurrent", 4)
        self._notify_progress(
            tasks_to_run[0],
            f"Starting engine: {len(tasks_to_run)} tasks, {max_concurrent} concurrent workers"
        )

        # 并发执行 / Concurrent execution
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = {
                executor.submit(self._process_task, task): task
                for task in tasks_to_run
            }
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    task = futures[future]
                    self._notify_progress(task, f"Unexpected error: {str(e)}")

        # 执行摘要 / Execution summary
        total_duration = time.time() - start_time
        self._running = False

        summary = {
            "status": "completed",
            "executed": len(tasks_to_run),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "total_earnings": self.tracker.total_earnings,
            "duration": round(total_duration, 2),
            "success_rate": round(
                (len(self.completed_tasks) / len(tasks_to_run) * 100)
                if tasks_to_run else 0,
                1,
            ),
        }

        self._notify_progress(
            tasks_to_run[0],
            f"Engine finished: {summary['completed']}/{summary['executed']} tasks, "
            f"earnings={summary['total_earnings']:.2f}"
        )

        return summary

    # ========================================================
    # 模板管理 / Template Management
    # ========================================================

    def load_templates(self, path: str) -> List[TaskTemplate]:
        """
        从JSON文件加载任务模板 / Load task templates from JSON file

        Args:
            path: 模板文件路径 / Template file path

        Returns:
            模板列表 / Template list
        """
        if not os.path.exists(path):
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            templates = []
            for item in data.get("templates", data) if isinstance(data, dict) else data:
                template = TaskTemplate.from_dict(item)
                templates.append(template)

            return templates
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Engine] Warning: Failed to load templates from {path}: {e}")
            return []

    def create_tasks_from_templates(
        self,
        template_path: str,
        count: int = 1,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> List[str]:
        """
        从模板文件批量创建任务 / Batch create tasks from template file

        Args:
            template_path: 模板文件路径 / Template file path
            count: 每个模板创建的任务数 / Tasks per template
            priority: 默认优先级 / Default priority

        Returns:
            创建的任务ID列表 / Created task ID list
        """
        templates = self.load_templates(template_path)
        task_ids: List[str] = []

        for template in templates:
            for _ in range(count):
                task_id = self.add_task_from_template(template, priority=priority)
                task_ids.append(task_id)

        return task_ids

    # ========================================================
    # 数据持久化 / Data Persistence
    # ========================================================

    def save_state(self, path: Optional[str] = None) -> None:
        """
        保存引擎状态 / Save engine state

        Args:
            path: 文件路径 / File path
        """
        save_path = path or os.path.join(
            self.config.get("work_dir", "./earnflow_data"),
            "engine_state.json",
        )

        dir_path = os.path.dirname(save_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        state = {
            "completed_tasks": [t.to_dict() for t in self.completed_tasks],
            "failed_tasks": [t.to_dict() for t in self.failed_tasks],
            "queue": [t.to_dict() for t in self._queue],
        }

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        # 同时保存收益数据 / Also save earnings data
        tracker_path = os.path.join(
            self.config.get("work_dir", "./earnflow_data"),
            "earnings.json",
        )
        self.tracker.save(tracker_path)

    def load_state(self, path: Optional[str] = None) -> bool:
        """
        加载引擎状态 / Load engine state

        Args:
            path: 文件路径 / File path

        Returns:
            是否加载成功 / Whether loading was successful
        """
        load_path = path or os.path.join(
            self.config.get("work_dir", "./earnflow_data"),
            "engine_state.json",
        )

        if not os.path.exists(load_path):
            return False

        try:
            with open(load_path, "r", encoding="utf-8") as f:
                state = json.load(f)

            for task_data in state.get("completed_tasks", []):
                task = Task.from_dict(task_data)
                self.completed_tasks.append(task)
                self.all_tasks.append(task)

            for task_data in state.get("failed_tasks", []):
                task = Task.from_dict(task_data)
                self.failed_tasks.append(task)
                self.all_tasks.append(task)

            for task_data in state.get("queue", []):
                task = Task.from_dict(task_data)
                self._queue.append(task)
                self.all_tasks.append(task)

            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Engine] Warning: Failed to load state from {load_path}: {e}")
            return False

    # ========================================================
    # 统计信息 / Statistics
    # ========================================================

    def get_summary(self) -> Dict[str, Any]:
        """
        获取引擎运行摘要 / Get engine runtime summary

        Returns:
            摘要字典 / Summary dictionary
        """
        total = len(self.all_tasks)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)

        return {
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "pending": self.queue_size,
            "success_rate": round((completed / total * 100) if total > 0 else 0, 1),
            "total_earnings": self.tracker.total_earnings,
            "avg_earnings": self.tracker.get_average_earnings(),
        }

    def __repr__(self) -> str:
        return (
            f"TaskEngine(queue={self.queue_size}, "
            f"completed={len(self.completed_tasks)}, "
            f"failed={len(self.failed_tasks)}, "
            f"earnings={self.tracker.total_earnings:.2f})"
        )
