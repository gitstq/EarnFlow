"""
EarnFlow 插件系统模块 / Plugin System Module

提供任务处理器的抽象基类、内置处理器实现和插件注册表。
支持通过插件扩展新的任务类型处理器。
Provides abstract base class for task handlers, built-in handler implementations,
and plugin registry. Supports extending new task type handlers via plugins.
"""

from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from earnflow.models import Task, TaskResult, TaskCategory
from earnflow.utils import generate_random_text, format_duration


# ============================================================
# 抽象基类 / Abstract Base Class
# ============================================================


class BaseTaskHandler(ABC):
    """
    任务处理器抽象基类 / Abstract base class for task handlers

    所有任务处理器必须继承此类并实现 execute 方法。
    All task handlers must inherit from this class and implement the execute method.

    Attributes:
        name: 处理器名称 / Handler name
        category: 支持的任务分类 / Supported task category
        description: 处理器描述 / Handler description
    """

    name: str = "base"
    category: str = "other"
    description: str = "Base task handler"

    @abstractmethod
    def execute(self, task: Task) -> TaskResult:
        """
        执行任务 / Execute task

        Args:
            task: 要执行的任务 / Task to execute

        Returns:
            任务执行结果 / Task execution result
        """
        ...

    def can_handle(self, task: Task) -> bool:
        """
        检查是否能处理指定任务 / Check if this handler can handle the given task

        Args:
            task: 待检查的任务 / Task to check

        Returns:
            是否能处理 / Whether it can handle
        """
        return task.category.value == self.category

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name!r}, category={self.category!r})>"


# ============================================================
# 内置处理器 / Built-in Handlers
# ============================================================


class ContentGenHandler(BaseTaskHandler):
    """
    内容生成处理器 / Content Generation Handler

    模拟AI内容生成任务，如文章撰写、文案创作等。
    Simulates AI content generation tasks, such as article writing, copywriting, etc.
    """

    name = "content_gen"
    category = "content_gen"
    description = "Handles content generation tasks (articles, copywriting, etc.)"

    # 模拟内容模板 / Simulated content templates
    _CONTENT_TEMPLATES = [
        "Generated a comprehensive article on {topic} with {count} sections covering key insights and analysis.",
        "Created engaging marketing copy for {topic} campaign, targeting {count} audience segments.",
        "Produced a detailed product description for {topic} with {count} feature highlights.",
        "Wrote an informative blog post about {topic} including {count} practical tips for readers.",
        "Drafted a professional social media content series about {topic} with {count} unique posts.",
    ]

    def execute(self, task: Task) -> TaskResult:
        """
        执行内容生成任务 / Execute content generation task

        模拟生成内容并返回结果。
        Simulates content generation and returns results.
        """
        start_time = time.time()
        topic = task.title or "general topic"
        count = random.randint(3, 8)

        # 模拟处理时间 / Simulate processing time
        simulated_time = random.uniform(1.0, min(task.estimated_time * 0.3, 10.0))
        time.sleep(simulated_time)

        template = random.choice(self._CONTENT_TEMPLATES)
        output = template.format(topic=topic, count=count)
        output += f"\n\nAdditional analysis: {generate_random_text(8, 15)}."

        duration = time.time() - start_time
        quality_score = random.uniform(70, 98)
        earnings = task.reward * (quality_score / 100)

        return TaskResult(
            task_id=task.id,
            output=output,
            earnings=round(earnings, 2),
            duration=round(duration, 2),
            quality_score=round(quality_score, 1),
        )


class DataLabelHandler(BaseTaskHandler):
    """
    数据标注处理器 / Data Labeling Handler

    模拟AI辅助数据标注任务，如图像分类、文本标注等。
    Simulates AI-assisted data labeling tasks, such as image classification, text annotation, etc.
    """

    name = "data_label"
    category = "data_label"
    description = "Handles data labeling tasks (image classification, text annotation, etc.)"

    _LABEL_OUTPUTS = [
        "Labeled {count} data points with {accuracy}% confidence across {labels} categories.",
        "Completed annotation of {count} samples, achieving inter-annotator agreement of {accuracy}%.",
        "Processed {count} items with label distribution: {labels}.",
        "Classified {count} records into {labels} categories with {accuracy}% average precision.",
    ]

    def execute(self, task: Task) -> TaskResult:
        """执行数据标注任务 / Execute data labeling task"""
        start_time = time.time()
        count = random.randint(50, 500)
        accuracy = random.uniform(85, 99)
        labels = random.randint(3, 10)

        simulated_time = random.uniform(0.5, min(task.estimated_time * 0.2, 8.0))
        time.sleep(simulated_time)

        label_names = ["positive", "negative", "neutral", "custom_a", "custom_b"]
        selected_labels = ", ".join(random.sample(label_names, min(labels, len(label_names))))

        template = random.choice(self._LABEL_OUTPUTS)
        output = template.format(
            count=count, accuracy=round(accuracy, 1), labels=selected_labels
        )
        output += f"\n\nQuality metrics: {generate_random_text(5, 10)}."

        duration = time.time() - start_time
        quality_score = accuracy
        earnings = task.reward * (quality_score / 100)

        return TaskResult(
            task_id=task.id,
            output=output,
            earnings=round(earnings, 2),
            duration=round(duration, 2),
            quality_score=round(quality_score, 1),
        )


class TranslationHandler(BaseTaskHandler):
    """
    翻译处理器 / Translation Handler

    模拟AI翻译任务，支持多语言翻译质量评估。
    Simulates AI translation tasks with multilingual translation quality assessment.
    """

    name = "translation"
    category = "translation"
    description = "Handles translation tasks between multiple languages"

    _TRANSLATION_OUTPUTS = [
        "Translated {count} segments from {source} to {target} with BLEU score of {score}.",
        "Completed {count} sentence translations ({source} -> {target}), TER: {score}.",
        "Processed {count} paragraphs with cultural adaptation, quality score: {score}/100.",
    ]

    _LANGUAGES = ["Chinese", "English", "Japanese", "Korean", "French", "German", "Spanish"]

    def execute(self, task: Task) -> TaskResult:
        """执行翻译任务 / Execute translation task"""
        start_time = time.time()
        count = random.randint(20, 200)
        source = random.choice(self._LANGUAGES)
        target = random.choice([l for l in self._LANGUAGES if l != source])
        score = random.uniform(0.75, 0.98)

        simulated_time = random.uniform(0.5, min(task.estimated_time * 0.25, 8.0))
        time.sleep(simulated_time)

        template = random.choice(self._TRANSLATION_OUTPUTS)
        output = template.format(
            count=count, source=source, target=target, score=round(score, 3)
        )
        output += f"\n\nTranslation notes: {generate_random_text(5, 12)}."

        duration = time.time() - start_time
        quality_score = score * 100
        earnings = task.reward * (quality_score / 100)

        return TaskResult(
            task_id=task.id,
            output=output,
            earnings=round(earnings, 2),
            duration=round(duration, 2),
            quality_score=round(quality_score, 1),
        )


class CodeReviewHandler(BaseTaskHandler):
    """
    代码审查处理器 / Code Review Handler

    模拟AI代码审查任务，包括代码质量分析、安全检查和优化建议。
    Simulates AI code review tasks, including code quality analysis, security checks, and optimization suggestions.
    """

    name = "code_review"
    category = "code_review"
    description = "Handles code review tasks (quality analysis, security checks, etc.)"

    _REVIEW_OUTPUTS = [
        "Reviewed {files} files ({loc} lines of code). Found {issues} issues: {summary}.",
        "Completed code audit of {files} modules. Quality score: {score}/100. Key findings: {summary}.",
        "Analyzed {loc} lines across {files} files. {issues} suggestions for improvement: {summary}.",
    ]

    def execute(self, task: Task) -> TaskResult:
        """执行代码审查任务 / Execute code review task"""
        start_time = time.time()
        files = random.randint(3, 25)
        loc = random.randint(200, 5000)
        issues = random.randint(1, 15)
        score = random.uniform(65, 95)

        simulated_time = random.uniform(1.0, min(task.estimated_time * 0.3, 10.0))
        time.sleep(simulated_time)

        summaries = [
            "2 critical security vulnerabilities, 3 performance bottlenecks, 5 style issues",
            "1 potential memory leak, 4 code smells, 2 missing error handlers",
            "3 deprecated API usages, 2 type safety improvements, 4 naming convention fixes",
            "5 documentation gaps, 2 test coverage improvements, 3 refactoring opportunities",
        ]
        summary = random.choice(summaries)

        template = random.choice(self._REVIEW_OUTPUTS)
        output = template.format(
            files=files, loc=loc, issues=issues, score=round(score, 1), summary=summary
        )
        output += f"\n\nRecommendations: {generate_random_text(6, 12)}."

        duration = time.time() - start_time
        quality_score = score
        earnings = task.reward * (quality_score / 100)

        return TaskResult(
            task_id=task.id,
            output=output,
            earnings=round(earnings, 2),
            duration=round(duration, 2),
            quality_score=round(quality_score, 1),
        )


class QATestHandler(BaseTaskHandler):
    """
    质量测试处理器 / QA Testing Handler

    模拟AI辅助质量测试任务，包括测试用例生成和Bug检测。
    Simulates AI-assisted QA testing tasks, including test case generation and bug detection.
    """

    name = "qa_test"
    category = "qa_test"
    description = "Handles QA testing tasks (test generation, bug detection, etc.)"

    def execute(self, task: Task) -> TaskResult:
        """执行质量测试任务 / Execute QA testing task"""
        start_time = time.time()

        test_cases = random.randint(10, 100)
        bugs_found = random.randint(0, 8)
        coverage = random.uniform(60, 95)

        simulated_time = random.uniform(0.5, min(task.estimated_time * 0.2, 8.0))
        time.sleep(simulated_time)

        output = (
            f"Generated {test_cases} test cases with {coverage:.1f}% code coverage.\n"
            f"Found {bugs_found} potential bugs during automated testing.\n"
            f"Test categories: unit ({random.randint(20, 50)}), integration ({random.randint(10, 30)}), "
            f"e2e ({random.randint(5, 20)}).\n"
            f"Analysis: {generate_random_text(6, 12)}."
        )

        duration = time.time() - start_time
        quality_score = coverage
        earnings = task.reward * (quality_score / 100)

        return TaskResult(
            task_id=task.id,
            output=output,
            earnings=round(earnings, 2),
            duration=round(duration, 2),
            quality_score=round(quality_score, 1),
        )


class ResearchHandler(BaseTaskHandler):
    """
    研究调查处理器 / Research Handler

    模拟AI研究调查任务，包括信息收集、分析和总结。
    Simulates AI research tasks, including information gathering, analysis, and summarization.
    """

    name = "research"
    category = "research"
    description = "Handles research and analysis tasks"

    def execute(self, task: Task) -> TaskResult:
        """执行研究调查任务 / Execute research task"""
        start_time = time.time()

        sources = random.randint(10, 50)
        key_findings = random.randint(3, 10)
        confidence = random.uniform(70, 95)

        simulated_time = random.uniform(1.0, min(task.estimated_time * 0.3, 10.0))
        time.sleep(simulated_time)

        output = (
            f"Research completed on '{task.title or 'general topic'}'.\n"
            f"Analyzed {sources} sources, identified {key_findings} key findings.\n"
            f"Confidence level: {confidence:.1f}%\n"
            f"Summary: {generate_random_text(10, 20)}.\n"
            f"Key insights: {generate_random_text(8, 15)}."
        )

        duration = time.time() - start_time
        quality_score = confidence
        earnings = task.reward * (quality_score / 100)

        return TaskResult(
            task_id=task.id,
            output=output,
            earnings=round(earnings, 2),
            duration=round(duration, 2),
            quality_score=round(quality_score, 1),
        )


# ============================================================
# 插件注册表 / Plugin Registry
# ============================================================


class PluginRegistry:
    """
    插件注册表 / Plugin Registry

    管理所有已注册的任务处理器，提供按分类查找和注册新处理器的功能。
    Manages all registered task handlers, providing lookup by category and
    registration of new handlers.

    Attributes:
        _handlers: 已注册的处理器字典 / Registered handlers dictionary
    """

    def __init__(self) -> None:
        """初始化注册表并注册内置处理器 / Initialize registry and register built-in handlers"""
        self._handlers: Dict[str, BaseTaskHandler] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """注册所有内置处理器 / Register all built-in handlers"""
        builtins: List[Type[BaseTaskHandler]] = [
            ContentGenHandler,
            DataLabelHandler,
            TranslationHandler,
            CodeReviewHandler,
            QATestHandler,
            ResearchHandler,
        ]
        for handler_cls in builtins:
            handler = handler_cls()
            self.register(handler)

    def register(self, handler: BaseTaskHandler) -> None:
        """
        注册处理器 / Register a handler

        Args:
            handler: 任务处理器实例 / Task handler instance
        """
        self._handlers[handler.category] = handler

    def unregister(self, category: str) -> None:
        """
        注销处理器 / Unregister a handler

        Args:
            category: 要注销的分类 / Category to unregister
        """
        self._handlers.pop(category, None)

    def get_handler(self, category: str) -> Optional[BaseTaskHandler]:
        """
        获取指定分类的处理器 / Get handler for specified category

        Args:
            category: 任务分类 / Task category

        Returns:
            处理器实例或None / Handler instance or None
        """
        return self._handlers.get(category)

    def get_handler_for_task(self, task: Task) -> Optional[BaseTaskHandler]:
        """
        获取能处理指定任务的处理器 / Get handler that can handle the specified task

        Args:
            task: 任务实例 / Task instance

        Returns:
            匹配的处理器或None / Matching handler or None
        """
        handler = self._handlers.get(task.category.value)
        if handler and handler.can_handle(task):
            return handler
        return None

    def list_handlers(self) -> List[Dict[str, str]]:
        """
        列出所有已注册的处理器 / List all registered handlers

        Returns:
            处理器信息列表 / List of handler information
        """
        return [
            {
                "name": h.name,
                "category": h.category,
                "description": h.description,
            }
            for h in self._handlers.values()
        ]

    @property
    def categories(self) -> List[str]:
        """
        获取所有已注册的分类 / Get all registered categories

        Returns:
            分类名称列表 / List of category names
        """
        return list(self._handlers.keys())

    def __len__(self) -> int:
        return len(self._handlers)

    def __repr__(self) -> str:
        return f"PluginRegistry(handlers={list(self._handlers.keys())})"
