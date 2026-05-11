"""
EarnFlow 收益追踪模块 / Earnings Tracking Module

提供收益记录、聚合统计和趋势分析功能。
支持按日/周/月维度进行收益统计和环比增长率计算。
Provides earnings recording, aggregation statistics, and trend analysis.
Supports daily/weekly/monthly earnings statistics and period-over-period growth calculation.
"""

from __future__ import annotations

import os
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from earnflow.models import EarningRecord, DashboardStats
from earnflow.utils import (
    get_date_str,
    get_datetime_str,
    format_currency,
    calculate_trend,
    percentage,
)


# ============================================================
# 收益追踪器 / Earnings Tracker
# ============================================================


class EarningTracker:
    """
    收益追踪器 / Earnings Tracker

    记录每笔收益，提供多维度统计分析和趋势计算。
    Records each earning, providing multi-dimensional statistical analysis and trend calculation.

    Attributes:
        records: 收益记录列表 / Earning record list
        currency: 货币类型 / Currency type
    """

    def __init__(self, currency: str = "CNY", storage_path: Optional[str] = None) -> None:
        """
        初始化收益追踪器 / Initialize earnings tracker

        Args:
            currency: 默认货币类型 / Default currency type
            storage_path: 数据存储路径（可选）/ Data storage path (optional)
        """
        self.records: List[EarningRecord] = []
        self.currency = currency
        self._storage_path = storage_path

        # 如果有存储路径，尝试加载历史数据 / If storage path exists, try loading history
        if storage_path and os.path.exists(storage_path):
            self._load(storage_path)

    # ========================================================
    # 记录管理 / Record Management
    # ========================================================

    def add_record(
        self,
        task_id: str,
        amount: float,
        category: str = "other",
        currency: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> EarningRecord:
        """
        添加收益记录 / Add earning record

        Args:
            task_id: 关联任务ID / Associated task ID
            amount: 收益金额 / Earning amount
            category: 任务分类 / Task category
            currency: 货币类型（默认使用追踪器货币）/ Currency (defaults to tracker currency)
            timestamp: 时间戳（默认当前时间）/ Timestamp (defaults to now)

        Returns:
            创建的收益记录 / Created earning record
        """
        record = EarningRecord(
            task_id=task_id,
            amount=round(amount, 2),
            currency=currency or self.currency,
            timestamp=timestamp or time.time(),
            category=category,
        )
        self.records.append(record)
        return record

    def add_records(self, records_data: List[Dict[str, Any]]) -> int:
        """
        批量添加收益记录 / Batch add earning records

        Args:
            records_data: 记录数据列表 / Record data list

        Returns:
            添加的记录数 / Number of records added
        """
        count = 0
        for data in records_data:
            record = EarningRecord.from_dict(data)
            self.records.append(record)
            count += 1
        return count

    def remove_record(self, record_id: str) -> bool:
        """
        删除收益记录 / Remove earning record

        Args:
            record_id: 记录ID / Record ID

        Returns:
            是否删除成功 / Whether deletion was successful
        """
        for i, record in enumerate(self.records):
            if record.id == record_id:
                self.records.pop(i)
                return True
        return False

    def get_record(self, record_id: str) -> Optional[EarningRecord]:
        """
        获取指定ID的收益记录 / Get earning record by ID

        Args:
            record_id: 记录ID / Record ID

        Returns:
            收益记录或None / Earning record or None
        """
        for record in self.records:
            if record.id == record_id:
                return record
        return None

    def clear(self) -> None:
        """清空所有记录 / Clear all records"""
        self.records.clear()

    # ========================================================
    # 统计分析 / Statistical Analysis
    # ========================================================

    @property
    def total_earnings(self) -> float:
        """
        获取总收益 / Get total earnings

        Returns:
            总收益金额 / Total earnings amount
        """
        return round(sum(r.amount for r in self.records), 2)

    @property
    def record_count(self) -> int:
        """
        获取记录数 / Get record count

        Returns:
            记录总数 / Total record count
        """
        return len(self.records)

    def get_earnings_by_category(self) -> Dict[str, float]:
        """
        按分类汇总收益 / Aggregate earnings by category

        Returns:
            分类收益字典 / Category earnings dictionary
        """
        category_totals: Dict[str, float] = defaultdict(float)
        for record in self.records:
            category_totals[record.category] += record.amount
        return {k: round(v, 2) for k, v in category_totals.items()}

    def get_earnings_by_date(self) -> Dict[str, float]:
        """
        按日期汇总收益 / Aggregate earnings by date

        Returns:
            日期收益字典（键为YYYY-MM-DD）/ Date earnings dictionary (key: YYYY-MM-DD)
        """
        date_totals: Dict[str, float] = defaultdict(float)
        for record in self.records:
            date_str = get_date_str(record.timestamp)
            date_totals[date_str] += record.amount
        return {k: round(v, 2) for k, v in sorted(date_totals.items())}

    def get_earnings_by_week(self) -> Dict[str, float]:
        """
        按周汇总收益 / Aggregate earnings by week

        Returns:
            周收益字典（键为YYYY-WXX格式）/ Week earnings dictionary (key: YYYY-WXX)
        """
        week_totals: Dict[str, float] = defaultdict(float)
        for record in self.records:
            dt = datetime.fromtimestamp(record.timestamp)
            year = dt.year
            week_num = dt.isocalendar()[1]
            week_key = f"{year}-W{week_num:02d}"
            week_totals[week_key] += record.amount
        return {k: round(v, 2) for k, v in sorted(week_totals.items())}

    def get_earnings_by_month(self) -> Dict[str, float]:
        """
        按月汇总收益 / Aggregate earnings by month

        Returns:
            月收益字典（键为YYYY-MM格式）/ Month earnings dictionary (key: YYYY-MM)
        """
        month_totals: Dict[str, float] = defaultdict(float)
        for record in self.records:
            dt = datetime.fromtimestamp(record.timestamp)
            month_key = f"{dt.year}-{dt.month:02d}"
            month_totals[month_key] += record.amount
        return {k: round(v, 2) for k, v in sorted(month_totals.items())}

    def get_daily_earnings(self, days: int = 7) -> Dict[str, float]:
        """
        获取最近N天的每日收益 / Get daily earnings for the last N days

        Args:
            days: 天数 / Number of days

        Returns:
            每日收益字典 / Daily earnings dictionary
        """
        now = time.time()
        cutoff = now - (days * 86400)

        daily: Dict[str, float] = defaultdict(float)
        for record in self.records:
            if record.timestamp >= cutoff:
                date_str = get_date_str(record.timestamp)
                daily[date_str] += record.amount

        # 填充缺失的日期（设为0）/ Fill missing dates with 0
        result: Dict[str, float] = {}
        for i in range(days):
            dt = datetime.fromtimestamp(now - (i * 86400))
            date_str = dt.strftime("%Y-%m-%d")
            result[date_str] = round(daily.get(date_str, 0.0), 2)

        return dict(sorted(result.items()))

    def get_today_earnings(self) -> float:
        """
        获取今日收益 / Get today's earnings

        Returns:
            今日收益金额 / Today's earnings amount
        """
        today = get_date_str()
        daily = self.get_earnings_by_date()
        return daily.get(today, 0.0)

    def get_average_earnings(self) -> float:
        """
        获取平均每笔收益 / Get average earnings per record

        Returns:
            平均收益 / Average earnings
        """
        if not self.records:
            return 0.0
        return round(self.total_earnings / len(self.records), 2)

    # ========================================================
    # 趋势分析 / Trend Analysis
    # ========================================================

    def get_daily_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取每日趋势数据 / Get daily trend data

        Args:
            days: 天数 / Number of days

        Returns:
            趋势数据列表 / Trend data list
        """
        daily = self.get_daily_earnings(days)
        dates = sorted(daily.keys())
        trend: List[Dict[str, Any]] = []

        for i, date in enumerate(dates):
            amount = daily[date]
            prev_amount = daily[dates[i - 1]] if i > 0 else 0.0
            growth_rate, direction = calculate_trend(amount, prev_amount)

            trend.append({
                "date": date,
                "amount": amount,
                "previous": prev_amount,
                "growth_rate": growth_rate,
                "direction": direction,
            })

        return trend

    def get_category_percentages(self) -> Dict[str, float]:
        """
        获取分类收益占比 / Get category earnings percentages

        Returns:
            分类占比字典 / Category percentage dictionary
        """
        category_totals = self.get_earnings_by_category()
        total = self.total_earnings

        if total == 0:
            return {k: 0.0 for k in category_totals}

        return {k: percentage(v, total) for k, v in category_totals.items()}

    # ========================================================
    # 仪表盘统计 / Dashboard Statistics
    # ========================================================

    def get_dashboard_stats(self, total_tasks: int = 0, success_count: int = 0) -> DashboardStats:
        """
        获取仪表盘统计数据 / Get dashboard statistics

        Args:
            total_tasks: 总任务数 / Total task count
            success_count: 成功任务数 / Successful task count

        Returns:
            仪表盘统计数据 / Dashboard statistics
        """
        daily_trend = self.get_daily_earnings(7)
        category_breakdown = self.get_earnings_by_category()

        success_rate = percentage(success_count, total_tasks) if total_tasks > 0 else 0.0
        avg_reward = self.get_average_earnings()

        return DashboardStats(
            total_earnings=self.total_earnings,
            total_tasks=total_tasks,
            success_rate=success_rate,
            avg_reward=avg_reward,
            category_breakdown=category_breakdown,
            daily_trend=daily_trend,
        )

    # ========================================================
    # 数据持久化 / Data Persistence
    # ========================================================

    def save(self, path: Optional[str] = None) -> None:
        """
        保存收益记录到文件 / Save earning records to file

        Args:
            path: 文件路径（默认使用初始化路径）/ File path (defaults to init path)
        """
        save_path = path or self._storage_path
        if not save_path:
            return

        dir_path = os.path.dirname(save_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        data = [r.to_dict() for r in self.records]
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load(self, path: str) -> None:
        """
        从文件加载收益记录 / Load earning records from file

        Args:
            path: 文件路径 / File path
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                record = EarningRecord.from_dict(item)
                self.records.append(record)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Tracker] Warning: Failed to load data from {path}: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        获取追踪器数据摘要 / Get tracker data summary

        Returns:
            数据摘要字典 / Data summary dictionary
        """
        return {
            "total_earnings": self.total_earnings,
            "record_count": self.record_count,
            "currency": self.currency,
            "category_breakdown": self.get_earnings_by_category(),
            "daily_trend": self.get_daily_earnings(7),
        }

    def __len__(self) -> int:
        return len(self.records)

    def __repr__(self) -> str:
        return (
            f"EarningTracker(records={len(self.records)}, "
            f"total={format_currency(self.total_earnings, self.currency)})"
        )
