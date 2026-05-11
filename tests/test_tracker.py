"""
EarnFlow 追踪器测试模块 / Tracker Test Module

测试收益追踪器的记录管理、聚合统计和趋势分析功能。
Tests the earnings tracker's record management, aggregation statistics,
and trend analysis functionality.
"""

import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from earnflow.models import EarningRecord
from earnflow.tracker import EarningTracker
from earnflow.utils import calculate_trend, get_date_str


class TestEarningTracker(unittest.TestCase):
    """收益追踪器测试类 / Earnings Tracker Test Class"""

    def setUp(self) -> None:
        """测试前准备 / Setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = EarningTracker(currency="CNY")

    def tearDown(self) -> None:
        """测试后清理 / Cleanup"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _add_sample_records(self) -> None:
        """添加样本记录 / Add sample records"""
        now = time.time()
        categories = ["content_gen", "data_label", "translation", "code_review"]
        amounts = [15.0, 8.5, 12.0, 20.0, 10.0, 18.0, 7.5, 22.0]

        for i, (cat, amount) in enumerate(zip(
            [categories[i % len(categories)] for i in range(len(amounts))],
            amounts,
        )):
            # 分布在过去7天内 / Distributed over the past 7 days
            timestamp = now - (i * 86400)
            self.tracker.add_record(
                task_id=f"task_{i}",
                amount=amount,
                category=cat,
                timestamp=timestamp,
            )

    def test_add_record(self) -> None:
        """测试添加记录 / Test adding a record"""
        record = self.tracker.add_record(
            task_id="task_001",
            amount=10.0,
            category="content_gen",
        )

        self.assertIsInstance(record, EarningRecord)
        self.assertEqual(record.amount, 10.0)
        self.assertEqual(record.task_id, "task_001")
        self.assertEqual(len(self.tracker), 1)

    def test_add_record_with_timestamp(self) -> None:
        """测试带时间戳的记录 / Test record with timestamp"""
        ts = time.time() - 86400  # 昨天 / Yesterday
        record = self.tracker.add_record(
            task_id="task_002",
            amount=15.0,
            timestamp=ts,
        )

        self.assertEqual(record.timestamp, ts)

    def test_total_earnings(self) -> None:
        """测试总收益计算 / Test total earnings calculation"""
        self.tracker.add_record("task_1", 10.0)
        self.tracker.add_record("task_2", 20.0)
        self.tracker.add_record("task_3", 5.5)

        self.assertAlmostEqual(self.tracker.total_earnings, 35.5)

    def test_record_count(self) -> None:
        """测试记录数 / Test record count"""
        self.assertEqual(self.tracker.record_count, 0)

        for i in range(5):
            self.tracker.add_record(f"task_{i}", 10.0)

        self.assertEqual(self.tracker.record_count, 5)

    def test_get_earnings_by_category(self) -> None:
        """测试按分类汇总 / Test category aggregation"""
        self._add_sample_records()
        cat_earnings = self.tracker.get_earnings_by_category()

        self.assertIsInstance(cat_earnings, dict)
        self.assertGreater(len(cat_earnings), 0)
        self.assertIn("content_gen", cat_earnings)

    def test_get_earnings_by_date(self) -> None:
        """测试按日期汇总 / Test date aggregation"""
        self._add_sample_records()
        date_earnings = self.tracker.get_earnings_by_date()

        self.assertIsInstance(date_earnings, dict)
        self.assertGreater(len(date_earnings), 0)

    def test_get_earnings_by_week(self) -> None:
        """测试按周汇总 / Test weekly aggregation"""
        self._add_sample_records()
        week_earnings = self.tracker.get_earnings_by_week()

        self.assertIsInstance(week_earnings, dict)

    def test_get_earnings_by_month(self) -> None:
        """测试按月汇总 / Test monthly aggregation"""
        self._add_sample_records()
        month_earnings = self.tracker.get_earnings_by_month()

        self.assertIsInstance(month_earnings, dict)

    def test_get_daily_earnings(self) -> None:
        """测试每日收益 / Test daily earnings"""
        self._add_sample_records()
        daily = self.tracker.get_daily_earnings(7)

        self.assertIsInstance(daily, dict)
        self.assertEqual(len(daily), 7)  # 应返回7天 / Should return 7 days

    def test_get_today_earnings(self) -> None:
        """测试今日收益 / Test today's earnings"""
        self.tracker.add_record("task_today", 25.0)
        today = self.tracker.get_today_earnings()

        self.assertGreater(today, 0)

    def test_get_average_earnings(self) -> None:
        """测试平均收益 / Test average earnings"""
        self.tracker.add_record("task_1", 10.0)
        self.tracker.add_record("task_2", 20.0)

        avg = self.tracker.get_average_earnings()
        self.assertAlmostEqual(avg, 15.0)

    def test_get_average_earnings_empty(self) -> None:
        """测试空记录的平均收益 / Test average earnings with no records"""
        avg = self.tracker.get_average_earnings()
        self.assertEqual(avg, 0.0)

    def test_get_daily_trend(self) -> None:
        """测试每日趋势 / Test daily trend"""
        self._add_sample_records()
        trend = self.tracker.get_daily_trend(7)

        self.assertIsInstance(trend, list)
        self.assertEqual(len(trend), 7)

        # 趋势数据应包含必要字段 / Trend data should contain required fields
        for item in trend:
            self.assertIn("date", item)
            self.assertIn("amount", item)
            self.assertIn("growth_rate", item)
            self.assertIn("direction", item)

    def test_get_category_percentages(self) -> None:
        """测试分类占比 / Test category percentages"""
        self._add_sample_records()
        percentages = self.tracker.get_category_percentages()

        total_pct = sum(percentages.values())
        self.assertAlmostEqual(total_pct, 100.0, places=1)

    def test_get_dashboard_stats(self) -> None:
        """测试仪表盘统计 / Test dashboard statistics"""
        self._add_sample_records()
        stats = self.tracker.get_dashboard_stats(
            total_tasks=10,
            success_count=8,
        )

        self.assertGreater(stats.total_earnings, 0)
        self.assertEqual(stats.total_tasks, 10)
        self.assertEqual(stats.success_rate, 80.0)
        self.assertGreater(stats.avg_reward, 0)

    def test_remove_record(self) -> None:
        """测试删除记录 / Test removing a record"""
        record = self.tracker.add_record("task_1", 10.0)
        self.assertEqual(len(self.tracker), 1)

        result = self.tracker.remove_record(record.id)
        self.assertTrue(result)
        self.assertEqual(len(self.tracker), 0)

    def test_remove_nonexistent_record(self) -> None:
        """测试删除不存在的记录 / Test removing nonexistent record"""
        result = self.tracker.remove_record("nonexistent_id")
        self.assertFalse(result)

    def test_clear_records(self) -> None:
        """测试清空记录 / Test clearing records"""
        for i in range(5):
            self.tracker.add_record(f"task_{i}", 10.0)

        self.tracker.clear()
        self.assertEqual(len(self.tracker), 0)
        self.assertEqual(self.tracker.total_earnings, 0.0)

    def test_save_and_load(self) -> None:
        """测试保存和加载 / Test save and load"""
        self._add_sample_records()

        save_path = os.path.join(self.temp_dir, "earnings_test.json")
        self.tracker.save(save_path)

        new_tracker = EarningTracker(currency="CNY", storage_path=save_path)
        self.assertEqual(len(new_tracker), len(self.tracker))
        self.assertAlmostEqual(new_tracker.total_earnings, self.tracker.total_earnings)

    def test_batch_add_records(self) -> None:
        """测试批量添加 / Test batch adding"""
        records_data = [
            {"task_id": "t1", "amount": 10.0, "category": "cat1"},
            {"task_id": "t2", "amount": 20.0, "category": "cat2"},
            {"task_id": "t3", "amount": 15.0, "category": "cat1"},
        ]
        count = self.tracker.add_records(records_data)

        self.assertEqual(count, 3)
        self.assertEqual(len(self.tracker), 3)

    def test_to_dict(self) -> None:
        """测试字典转换 / Test dictionary conversion"""
        self._add_sample_records()
        data = self.tracker.to_dict()

        self.assertIn("total_earnings", data)
        self.assertIn("record_count", data)
        self.assertIn("category_breakdown", data)
        self.assertIn("daily_trend", data)


class TestTrendCalculation(unittest.TestCase):
    """趋势计算测试 / Trend Calculation Tests"""

    def test_positive_trend(self) -> None:
        """测试上升趋势 / Test upward trend"""
        rate, direction = calculate_trend(150, 100)
        self.assertEqual(rate, 50.0)
        self.assertEqual(direction, "up")

    def test_negative_trend(self) -> None:
        """测试下降趋势 / Test downward trend"""
        rate, direction = calculate_trend(80, 100)
        self.assertEqual(rate, -20.0)
        self.assertEqual(direction, "down")

    def test_stable_trend(self) -> None:
        """测试持平趋势 / Test stable trend"""
        rate, direction = calculate_trend(100, 100)
        self.assertEqual(rate, 0.0)
        self.assertEqual(direction, "stable")

    def test_zero_previous(self) -> None:
        """测试上期为零 / Test zero previous period"""
        rate, direction = calculate_trend(100, 0)
        self.assertEqual(rate, 100.0)
        self.assertEqual(direction, "up")

    def test_both_zero(self) -> None:
        """测试两期都为零 / Test both periods zero"""
        rate, direction = calculate_trend(0, 0)
        self.assertEqual(rate, 0.0)
        self.assertEqual(direction, "stable")


if __name__ == "__main__":
    unittest.main()
