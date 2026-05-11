"""
EarnFlow 引擎测试模块 / Engine Test Module

测试核心任务引擎的功能，包括任务添加、执行、状态管理和数据持久化。
Tests core task engine functionality including task addition, execution,
state management, and data persistence.
"""

import json
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch, MagicMock

# 确保可以导入包 / Ensure package imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from earnflow.models import (
    Task, TaskResult, TaskStatus, TaskPriority, TaskCategory,
    EarningRecord, TaskTemplate, DashboardStats,
)
from earnflow.engine import TaskEngine
from earnflow.config import ConfigManager
from earnflow.plugins import PluginRegistry
from earnflow.tracker import EarningTracker


class TestTaskEngine(unittest.TestCase):
    """任务引擎测试类 / Task Engine Test Class"""

    def setUp(self) -> None:
        """测试前准备 / Setup before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigManager()
        self.config.set("work_dir", self.temp_dir)
        self.config.set("max_concurrent", 2)
        self.config.set("task_timeout", 30)
        self.registry = PluginRegistry()
        self.tracker = EarningTracker(currency="CNY")
        self.engine = TaskEngine(
            config=self.config,
            registry=self.registry,
            tracker=self.tracker,
        )

    def tearDown(self) -> None:
        """测试后清理 / Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_task(self) -> None:
        """测试添加任务 / Test adding a task"""
        task = Task(
            title="Test Task",
            description="A test task",
            category=TaskCategory.CONTENT_GEN,
            reward=10.0,
        )
        task_id = self.engine.add_task(task)

        self.assertIsNotNone(task_id)
        self.assertEqual(self.engine.queue_size, 1)
        self.assertEqual(task.status, TaskStatus.PENDING)

    def test_add_task_from_template(self) -> None:
        """测试从模板创建任务 / Test creating task from template"""
        template = TaskTemplate(
            name="Test Template",
            description="Test description",
            category="content_gen",
            base_reward=15.0,
            required_tags=["test"],
        )
        task_id = self.engine.add_task_from_template(template)

        self.assertIsNotNone(task_id)
        self.assertEqual(self.engine.queue_size, 1)

    def test_add_tasks_batch(self) -> None:
        """测试批量添加任务 / Test batch adding tasks"""
        tasks = [
            Task(title=f"Task {i}", category=TaskCategory.CONTENT_GEN, reward=5.0)
            for i in range(5)
        ]
        ids = self.engine.add_tasks_batch(tasks)

        self.assertEqual(len(ids), 5)
        self.assertEqual(self.engine.queue_size, 5)

    def test_run_empty_queue(self) -> None:
        """测试空队列运行 / Test running with empty queue"""
        summary = self.engine.run()

        self.assertEqual(summary["status"], "empty")
        self.assertEqual(summary["executed"], 0)

    def test_run_single_task(self) -> None:
        """测试运行单个任务 / Test running a single task"""
        task = Task(
            title="Content Generation Test",
            description="Generate a test article",
            category=TaskCategory.CONTENT_GEN,
            reward=10.0,
            estimated_time=5,
        )
        self.engine.add_task(task)

        summary = self.engine.run()

        self.assertEqual(summary["status"], "completed")
        self.assertEqual(summary["executed"], 1)
        self.assertGreaterEqual(summary["completed"], 1)
        self.assertGreaterEqual(summary["total_earnings"], 0)

    def test_run_multiple_tasks(self) -> None:
        """测试运行多个任务 / Test running multiple tasks"""
        categories = [
            TaskCategory.CONTENT_GEN,
            TaskCategory.DATA_LABEL,
            TaskCategory.TRANSLATION,
            TaskCategory.CODE_REVIEW,
        ]
        for i, cat in enumerate(categories):
            task = Task(
                title=f"Task {i}",
                description=f"Test task for {cat.value}",
                category=cat,
                reward=10.0,
                estimated_time=5,
            )
            self.engine.add_task(task)

        summary = self.engine.run()

        self.assertEqual(summary["executed"], 4)
        self.assertGreater(summary["total_earnings"], 0)

    def test_max_tasks_limit(self) -> None:
        """测试最大任务数限制 / Test max tasks limit"""
        for i in range(5):
            task = Task(
                title=f"Task {i}",
                category=TaskCategory.CONTENT_GEN,
                reward=5.0,
                estimated_time=3,
            )
            self.engine.add_task(task)

        summary = self.engine.run(max_tasks=2)

        self.assertEqual(summary["executed"], 2)
        self.assertEqual(self.engine.queue_size, 3)

    def test_progress_callback(self) -> None:
        """测试进度回调 / Test progress callback"""
        messages: list = []

        def callback(task: Task, message: str) -> None:
            messages.append(message)

        self.engine.on_progress(callback)

        task = Task(
            title="Callback Test",
            category=TaskCategory.CONTENT_GEN,
            reward=5.0,
            estimated_time=3,
        )
        self.engine.add_task(task)
        self.engine.run()

        self.assertGreater(len(messages), 0)

    def test_priority_sorting(self) -> None:
        """测试优先级排序 / Test priority sorting"""
        priorities = [
            TaskPriority.LOW,
            TaskPriority.URGENT,
            TaskPriority.MEDIUM,
            TaskPriority.HIGH,
        ]
        for priority in priorities:
            task = Task(
                title=f"Task {priority.value}",
                category=TaskCategory.CONTENT_GEN,
                reward=5.0,
                priority=priority,
                estimated_time=3,
            )
            self.engine.add_task(task)

        self.engine.run()

        # 高优先级任务应先执行 / Higher priority tasks should execute first
        self.assertEqual(self.engine.completed_tasks[0].priority, TaskPriority.URGENT)

    def test_save_and_load_state(self) -> None:
        """测试状态保存和加载 / Test state save and load"""
        task = Task(
            title="Persistence Test",
            category=TaskCategory.CONTENT_GEN,
            reward=10.0,
            estimated_time=3,
        )
        self.engine.add_task(task)
        self.engine.run()

        # 保存状态 / Save state
        self.engine.save_state()

        # 创建新引擎并加载 / Create new engine and load
        new_tracker = EarningTracker(currency="CNY")
        new_engine = TaskEngine(
            config=self.config,
            registry=self.registry,
            tracker=new_tracker,
        )
        loaded = new_engine.load_state()

        self.assertTrue(loaded)
        self.assertGreater(len(new_engine.completed_tasks), 0)

    def test_load_templates(self) -> None:
        """测试加载模板文件 / Test loading template file"""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "templates", "default_tasks.json"
        )
        if os.path.exists(template_path):
            templates = self.engine.load_templates(template_path)
            self.assertGreater(len(templates), 0)
            self.assertIsInstance(templates[0], TaskTemplate)

    def test_get_summary(self) -> None:
        """测试获取摘要 / Test getting summary"""
        task = Task(
            title="Summary Test",
            category=TaskCategory.CONTENT_GEN,
            reward=10.0,
            estimated_time=3,
        )
        self.engine.add_task(task)
        self.engine.run()

        summary = self.engine.get_summary()
        self.assertEqual(summary["total_tasks"], 1)
        self.assertGreaterEqual(summary["completed"], 1)

    def test_engine_not_running_twice(self) -> None:
        """测试引擎不能同时运行两次 / Test engine cannot run twice simultaneously"""
        task = Task(
            title="Concurrent Test",
            category=TaskCategory.CONTENT_GEN,
            reward=5.0,
            estimated_time=3,
        )
        self.engine.add_task(task)

        # 模拟运行中状态 / Simulate running state
        self.engine._running = True
        summary = self.engine.run()

        self.assertEqual(summary["status"], "already_running")
        self.engine._running = False


if __name__ == "__main__":
    unittest.main()
