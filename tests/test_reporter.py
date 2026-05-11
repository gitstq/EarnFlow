"""
EarnFlow 报告器测试模块 / Reporter Test Module

测试报告生成器的多格式输出功能，包括JSON、CSV、Markdown和HTML。
Tests the report generator's multi-format output functionality,
including JSON, CSV, Markdown, and HTML.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from earnflow.models import (
    Task, TaskResult, TaskStatus, TaskCategory, TaskPriority,
    EarningRecord, DashboardStats,
)
from earnflow.reporter import ReportGenerator
from earnflow.utils import format_currency


class TestReportGenerator(unittest.TestCase):
    """报告生成器测试类 / Report Generator Test Class"""

    def setUp(self) -> None:
        """测试前准备 / Setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ReportGenerator(currency="CNY")
        self.stats = DashboardStats(
            total_earnings=156.5,
            total_tasks=12,
            success_rate=83.3,
            avg_reward=13.04,
            category_breakdown={
                "content_gen": 45.0,
                "data_label": 28.5,
                "translation": 36.0,
                "code_review": 47.0,
            },
            daily_trend={
                "2025-01-05": 10.0,
                "2025-01-06": 15.5,
                "2025-01-07": 22.0,
                "2025-01-08": 18.0,
                "2025-01-09": 25.0,
                "2025-01-10": 30.0,
                "2025-01-11": 36.0,
            },
        )

        # 创建样本任务 / Create sample tasks
        self.tasks = [
            Task(
                id="task_001",
                title="Blog Article Writing",
                category=TaskCategory.CONTENT_GEN,
                status=TaskStatus.COMPLETED,
                reward=15.0,
                result=TaskResult(
                    task_id="task_001",
                    earnings=14.5,
                    quality_score=96.7,
                    duration=45.2,
                ),
            ),
            Task(
                id="task_002",
                title="Image Data Labeling",
                category=TaskCategory.DATA_LABEL,
                status=TaskStatus.COMPLETED,
                reward=10.0,
            ),
            Task(
                id="task_003",
                title="Code Review",
                category=TaskCategory.CODE_REVIEW,
                status=TaskStatus.FAILED,
                reward=20.0,
            ),
        ]

        # 创建样本收益记录 / Create sample earning records
        self.records = [
            EarningRecord(
                id="earn_001",
                task_id="task_001",
                amount=14.5,
                currency="CNY",
                category="content_gen",
            ),
            EarningRecord(
                id="earn_002",
                task_id="task_002",
                amount=9.8,
                currency="CNY",
                category="data_label",
            ),
        ]

    def tearDown(self) -> None:
        """测试后清理 / Cleanup"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_json(self) -> None:
        """测试JSON报告生成 / Test JSON report generation"""
        json_str = self.generator.generate_json(self.stats, self.tasks, self.records)

        import json
        data = json.loads(json_str)

        self.assertEqual(data["report_title"], "EarnFlow Report")
        self.assertEqual(data["summary"]["total_earnings"], 156.5)
        self.assertEqual(data["summary"]["total_tasks"], 12)
        self.assertIn("tasks", data)
        self.assertIn("earnings", data)

    def test_generate_csv(self) -> None:
        """测试CSV报告生成 / Test CSV report generation"""
        csv_str = self.generator.generate_csv(self.records)

        lines = csv_str.strip().split("\n")
        self.assertGreater(len(lines), 1)  # 至少有表头和一行数据 / At least header and one data row

        # 检查表头 / Check header
        header = lines[0]
        self.assertIn("ID", header)
        self.assertIn("Amount", header)
        self.assertIn("Category", header)

    def test_generate_csv_no_header(self) -> None:
        """测试无表头CSV / Test CSV without header"""
        csv_str = self.generator.generate_csv(self.records, include_header=False)

        lines = csv_str.strip().split("\n")
        self.assertEqual(len(lines), 2)  # 只有数据行 / Only data rows

    def test_generate_task_csv(self) -> None:
        """测试任务CSV报告 / Test task CSV report"""
        csv_str = self.generator.generate_task_csv(self.tasks)

        lines = csv_str.strip().split("\n")
        self.assertGreater(len(lines), 1)
        self.assertIn("Title", lines[0])
        self.assertIn("Category", lines[0])

    def test_generate_markdown(self) -> None:
        """测试Markdown报告生成 / Test Markdown report generation"""
        md_str = self.generator.generate_markdown(self.stats, self.tasks, self.records)

        # 检查Markdown结构 / Check Markdown structure
        self.assertIn("# EarnFlow Report", md_str)
        self.assertIn("## Overview", md_str)
        self.assertIn("## Category Breakdown", md_str)
        self.assertIn("## Daily Trend", md_str)
        self.assertIn("## Recent Tasks", md_str)
        self.assertIn("## Recent Earnings", md_str)

        # 检查ASCII图表 / Check ASCII charts
        self.assertIn("### Category Chart", md_str)
        self.assertIn("### Trend Chart", md_str)

    def test_generate_markdown_no_tasks(self) -> None:
        """测试无任务数据的Markdown / Test Markdown with no task data"""
        md_str = self.generator.generate_markdown(self.stats)

        self.assertIn("# EarnFlow Report", md_str)
        self.assertNotIn("## Recent Tasks", md_str)

    def test_generate_html(self) -> None:
        """测试HTML报告生成 / Test HTML report generation"""
        html_str = self.generator.generate_html(self.stats, self.tasks, self.records)

        # 检查HTML结构 / Check HTML structure
        self.assertIn("<!DOCTYPE html>", html_str)
        self.assertIn("<html", html_str)
        self.assertIn("</html>", html_str)
        self.assertIn("<head>", html_str)
        self.assertIn("<body>", html_str)

        # 检查内联CSS / Check inline CSS
        self.assertIn("<style>", html_str)
        self.assertIn("background:", html_str)
        self.assertIn("color:", html_str)

        # 检查统计卡片 / Check stat cards
        self.assertIn("Total Earnings", html_str)
        self.assertIn("Success Rate", html_str)

        # 检查SVG图表 / Check SVG charts
        self.assertIn("<svg", html_str)
        self.assertIn("</svg>", html_str)

    def test_generate_html_no_data(self) -> None:
        """测试无数据的HTML报告 / Test HTML report with no data"""
        empty_stats = DashboardStats()
        html_str = self.generator.generate_html(empty_stats)

        self.assertIn("<!DOCTYPE html>", html_str)
        self.assertIn("0.00", html_str)

    def test_generate_unsupported_format(self) -> None:
        """测试不支持的格式 / Test unsupported format"""
        with self.assertRaises(ValueError):
            self.generator.generate("xml", self.stats)

    def test_generate_with_format_alias(self) -> None:
        """测试格式别名 / Test format alias"""
        md_str = self.generator.generate("md", self.stats)
        self.assertIn("# EarnFlow Report", md_str)

    def test_save_report(self) -> None:
        """测试保存报告 / Test saving report"""
        output_path = os.path.join(self.temp_dir, "test_report.md")
        saved = self.generator.save_report("markdown", output_path, self.stats)

        self.assertEqual(saved, output_path)
        self.assertTrue(os.path.exists(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("# EarnFlow Report", content)

    def test_save_report_creates_dirs(self) -> None:
        """测试保存报告时创建目录 / Test creating directories when saving report"""
        output_path = os.path.join(self.temp_dir, "sub", "dir", "report.json")
        saved = self.generator.save_report("json", output_path, self.stats)

        self.assertTrue(os.path.exists(output_path))

    def test_html_escaping(self) -> None:
        """测试HTML转义 / Test HTML escaping"""
        task_with_special_chars = Task(
            id="task_special",
            title="Test <script>alert('xss')</script>",
            category=TaskCategory.OTHER,
            status=TaskStatus.PENDING,
            reward=5.0,
        )
        html_str = self.generator.generate_html(self.stats, [task_with_special_chars])

        self.assertNotIn("<script>", html_str)
        self.assertIn("&lt;script&gt;", html_str)


if __name__ == "__main__":
    unittest.main()
