"""
EarnFlow 匹配器测试模块 / Matcher Test Module

测试智能任务匹配引擎的关键字匹配、分类匹配、标签匹配和综合评分功能。
Tests the intelligent task matching engine's keyword matching, category matching,
tag matching, and composite scoring functionality.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from earnflow.models import Task, TaskCategory, TaskPriority
from earnflow.matcher import TaskMatcher, tokenize, compute_tf, compute_idf


class TestTokenizer(unittest.TestCase):
    """分词功能测试 / Tokenizer Tests"""

    def test_english_tokenization(self) -> None:
        """测试英文分词 / Test English tokenization"""
        tokens = tokenize("Hello World Python Programming")
        self.assertIn("hello", tokens)
        self.assertIn("world", tokens)
        self.assertIn("python", tokens)
        self.assertIn("programming", tokens)

    def test_chinese_tokenization(self) -> None:
        """测试中文分词 / Test Chinese tokenization"""
        tokens = tokenize("人工智能任务引擎")
        self.assertIn("人", tokens)
        self.assertIn("工", tokens)
        self.assertIn("智", tokens)
        self.assertIn("能", tokens)

    def test_mixed_tokenization(self) -> None:
        """测试中英文混合分词 / Test mixed Chinese-English tokenization"""
        tokens = tokenize("AI人工智能引擎Engine")
        self.assertIn("ai", tokens)
        self.assertIn("engine", tokens)
        # 中文字符
        self.assertIn("人", tokens)

    def test_empty_string(self) -> None:
        """测试空字符串 / Test empty string"""
        tokens = tokenize("")
        self.assertEqual(tokens, [])


class TestTFIDF(unittest.TestCase):
    """TF-IDF计算测试 / TF-IDF Calculation Tests"""

    def test_compute_tf(self) -> None:
        """测试词频计算 / Test term frequency calculation"""
        tokens = ["hello", "world", "hello", "python"]
        tf = compute_tf(tokens)
        self.assertAlmostEqual(tf["hello"], 0.5)
        self.assertAlmostEqual(tf["world"], 0.25)
        self.assertAlmostEqual(tf["python"], 0.25)

    def test_compute_tf_empty(self) -> None:
        """测试空列表的词频 / Test TF of empty list"""
        tf = compute_tf([])
        self.assertEqual(tf, {})

    def test_compute_idf(self) -> None:
        """测试逆文档频率计算 / Test IDF calculation"""
        docs = [
            ["hello", "world"],
            ["hello", "python"],
            ["world", "python", "code"],
        ]
        idf = compute_idf(docs)

        self.assertIn("hello", idf)
        self.assertIn("world", idf)
        self.assertIn("python", idf)
        self.assertIn("code", idf)

        # "code" 只出现在一个文档中，IDF应更高 / "code" appears in only one doc, IDF should be higher
        self.assertGreater(idf["code"], idf["hello"])

    def test_compute_idf_empty(self) -> None:
        """测试空文档列表的IDF / Test IDF of empty document list"""
        idf = compute_idf([])
        self.assertEqual(idf, {})


class TestTaskMatcher(unittest.TestCase):
    """任务匹配引擎测试 / Task Matcher Tests"""

    def setUp(self) -> None:
        """测试前准备 / Setup"""
        self.matcher = TaskMatcher(
            keyword_weight=0.4,
            category_weight=0.3,
            tag_weight=0.3,
        )
        self.tasks = [
            Task(
                title="Blog Article Writing",
                description="Write a comprehensive blog post about technology trends",
                category=TaskCategory.CONTENT_GEN,
                tags=["writing", "blog", "technology"],
                reward=15.0,
            ),
            Task(
                title="Image Data Labeling",
                description="Label images for machine learning training datasets",
                category=TaskCategory.DATA_LABEL,
                tags=["labeling", "images", "ml", "dataset"],
                reward=10.0,
            ),
            Task(
                title="Python Code Review",
                description="Review Python source code for quality and security",
                category=TaskCategory.CODE_REVIEW,
                tags=["python", "code", "review", "security"],
                reward=20.0,
            ),
            Task(
                title="Technical Translation EN-CN",
                description="Translate technical documents from English to Chinese",
                category=TaskCategory.TRANSLATION,
                tags=["translation", "english", "chinese", "technical"],
                reward=18.0,
            ),
            Task(
                title="Market Research Analysis",
                description="Research market trends and compile analysis report",
                category=TaskCategory.RESEARCH,
                tags=["research", "market", "analysis", "report"],
                reward=25.0,
            ),
        ]

    def test_keyword_matching(self) -> None:
        """测试关键词匹配 / Test keyword matching"""
        results = self.matcher.match("blog writing article", self.tasks)
        self.assertGreater(len(results), 0)

        # 博客写作任务应排在前面 / Blog writing task should rank high
        top_task = results[0][0]
        self.assertEqual(top_task.category, TaskCategory.CONTENT_GEN)

    def test_category_matching(self) -> None:
        """测试分类匹配 / Test category matching"""
        results = self.matcher.match(
            "task",
            self.tasks,
            category=TaskCategory.CODE_REVIEW,
        )

        # 代码审查任务应排在最前 / Code review task should rank first
        top_task = results[0][0]
        self.assertEqual(top_task.category, TaskCategory.CODE_REVIEW)

    def test_tag_matching(self) -> None:
        """测试标签匹配 / Test tag matching"""
        results = self.matcher.match(
            "task",
            self.tasks,
            tags=["python", "security"],
        )

        # 代码审查任务应排在前面 / Code review task should rank high
        top_task = results[0][0]
        self.assertEqual(top_task.category, TaskCategory.CODE_REVIEW)

    def test_top_n_limit(self) -> None:
        """测试返回数量限制 / Test top-N limit"""
        results = self.matcher.match("task", self.tasks, top_n=3)
        self.assertEqual(len(results), 3)

    def test_empty_tasks(self) -> None:
        """测试空任务列表 / Test empty task list"""
        results = self.matcher.match("query", [])
        self.assertEqual(results, [])

    def test_match_single(self) -> None:
        """测试单个任务匹配 / Test single task matching"""
        task = self.tasks[0]
        score = self.matcher.match_single("blog writing", task)

        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)

    def test_filter_by_score(self) -> None:
        """测试分数过滤 / Test score filtering"""
        results = self.matcher.filter_by_score(
            "blog writing article technology",
            self.tasks,
            min_score=20.0,
        )

        # 所有结果应达到最低分数 / All results should meet minimum score
        for task, score in results:
            self.assertGreaterEqual(score, 20.0)

    def test_no_match_query(self) -> None:
        """测试不相关查询 / Test irrelevant query"""
        results = self.matcher.match("quantum physics black hole", self.tasks)
        self.assertGreater(len(results), 0)  # 仍应返回结果（优先级加分）/ Should still return results (priority bonus)

    def test_priority_bonus(self) -> None:
        """测试优先级加分 / Test priority bonus"""
        urgent_task = Task(
            title="Urgent Task",
            description="An urgent task",
            category=TaskCategory.OTHER,
            priority=TaskPriority.URGENT,
            reward=5.0,
        )
        low_task = Task(
            title="Low Priority Task",
            description="A low priority task",
            category=TaskCategory.OTHER,
            priority=TaskPriority.LOW,
            reward=5.0,
        )

        results = self.matcher.match("task", [urgent_task, low_task])
        self.assertGreater(results[0][1], results[1][1])


if __name__ == "__main__":
    unittest.main()
