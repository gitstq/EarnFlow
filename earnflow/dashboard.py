"""
EarnFlow TUI仪表盘模块 / TUI Dashboard Module

使用标准库print实现终端收益统计展示，包括：
- 总收益、今日收益、任务完成数、成功率
- 分类收益柱状图（ASCII）
- 近7日趋势折线图（ASCII）
- 实时刷新

Uses standard library print for terminal earnings statistics display, including:
- Total earnings, today's earnings, task completion count, success rate
- Category earnings bar chart (ASCII)
- 7-day trend line chart (ASCII)
- Real-time refresh
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from earnflow.models import DashboardStats, Task, TaskStatus
from earnflow.tracker import EarningTracker
from earnflow.utils import (
    color_text,
    format_currency,
    format_duration,
    get_date_str,
    percentage,
)


# ============================================================
# ASCII 图表绘制 / ASCII Chart Drawing
# ============================================================


def draw_bar_chart(
    data: Dict[str, float],
    width: int = 40,
    max_height: int = 10,
    title: str = "",
) -> str:
    """
    绘制ASCII水平柱状图 / Draw ASCII horizontal bar chart

    Args:
        data: 数据字典（标签->值）/ Data dictionary (label -> value)
        width: 柱状图最大宽度 / Max bar width
        max_height: 最大高度（行数）/ Max height (rows)
        title: 图表标题 / Chart title

    Returns:
        ASCII图表字符串 / ASCII chart string
    """
    if not data:
        return "  No data available."

    lines: List[str] = []

    if title:
        lines.append(f"  {title}")
        lines.append("")

    max_val = max(data.values()) if data.values() else 1
    if max_val == 0:
        max_val = 1

    # 按值排序 / Sort by value
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)

    for label, value in sorted_items:
        bar_len = int((value / max_val) * width) if max_val > 0 else 0
        bar = "#" * bar_len
        label_str = f"{label:<15}"
        value_str = f"{value:>8.2f}"
        lines.append(f"  {label_str} |{color_text(bar, 'cyan')}| {value_str}")

    return "\n".join(lines)


def draw_line_chart(
    data: Dict[str, float],
    height: int = 10,
    width: int = 50,
    title: str = "",
) -> str:
    """
    绘制ASCII折线图 / Draw ASCII line chart

    Args:
        data: 数据字典（标签->值）/ Data dictionary (label -> value)
        height: 图表高度 / Chart height
        width: 图表宽度 / Chart width
        title: 图表标题 / Chart title

    Returns:
        ASCII图表字符串 / ASCII chart string
    """
    if not data:
        return "  No data available."

    lines: List[str] = []

    if title:
        lines.append(f"  {title}")
        lines.append("")

    sorted_items = sorted(data.items())
    labels = [k[-5:] for k, _ in sorted_items]  # 取最后5个字符作为标签 / Take last 5 chars as label
    values = [v for _, v in sorted_items]

    max_val = max(values) if values else 1
    if max_val == 0:
        max_val = 1

    min_val = min(values)
    val_range = max_val - min_val if max_val != min_val else 1

    # 生成Y轴刻度 / Generate Y-axis ticks
    for row in range(height, -1, -1):
        threshold = min_val + (val_range / height) * row
        row_str = f"  {threshold:>8.1f} |"

        for value in values:
            normalized = (value - min_val) / val_range if val_range > 0 else 0
            char_row = int(normalized * height)

            if abs(char_row - row) < 0.5:
                row_str += color_text(" *", "green")
            elif char_row > row:
                row_str += "  |"
            else:
                row_str += "   "

        lines.append(row_str)

    # X轴 / X-axis
    lines.append(f"  {'':>8} +" + "-" * (len(values) * 3))

    # X轴标签 / X-axis labels
    label_str = "          "
    for label in labels:
        label_str += f" {label}"
    lines.append(label_str)

    return "\n".join(lines)


# ============================================================
# TUI 仪表盘 / TUI Dashboard
# ============================================================


class Dashboard:
    """
    TUI仪表盘 / TUI Dashboard

    在终端中实时展示收益统计和任务执行情况。
    Displays earnings statistics and task execution status in real-time in the terminal.

    Attributes:
        tracker: 收益追踪器 / Earnings tracker
        refresh_interval: 刷新间隔（秒）/ Refresh interval (seconds)
    """

    def __init__(
        self,
        tracker: EarningTracker,
        tasks: Optional[List[Task]] = None,
        refresh_interval: int = 5,
    ) -> None:
        """
        初始化仪表盘 / Initialize dashboard

        Args:
            tracker: 收益追踪器 / Earnings tracker
            tasks: 任务列表（可选）/ Task list (optional)
            refresh_interval: 刷新间隔秒数 / Refresh interval in seconds
        """
        self.tracker = tracker
        self.tasks = tasks or []
        self.refresh_interval = refresh_interval
        self._running = False

    def render(self, stats: Optional[DashboardStats] = None) -> str:
        """
        渲染仪表盘界面 / Render dashboard interface

        Args:
            stats: 仪表盘统计数据（可选，自动计算）/ Dashboard stats (optional, auto-calculated)

        Returns:
            渲染后的界面字符串 / Rendered interface string
        """
        if not stats:
            total_tasks = len(self.tasks)
            success_count = sum(
                1 for t in self.tasks if t.status == TaskStatus.COMPLETED
            )
            stats = self.tracker.get_dashboard_stats(total_tasks, success_count)

        lines: List[str] = []

        # 清屏并渲染 / Clear screen and render
        lines.append("\033[2J\033[H")  # ANSI clear screen and home cursor

        # 标题 / Header
        lines.append(color_text("=" * 60, "dim"))
        lines.append(
            color_text("  EarnFlow Dashboard", "bold", "cyan")
            + color_text("  - AI Task Earning Engine", "dim")
        )
        lines.append(
            color_text(f"  Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "dim")
        )
        lines.append(color_text("=" * 60, "dim"))
        lines.append("")

        # 核心指标卡片 / Core metric cards
        lines.append(self._render_metric_cards(stats))
        lines.append("")

        # 分类收益柱状图 / Category earnings bar chart
        if stats.category_breakdown:
            lines.append(draw_bar_chart(
                stats.category_breakdown,
                width=35,
                title=color_text("  Category Earnings Breakdown", "bold"),
            ))
            lines.append("")

        # 每日趋势折线图 / Daily trend line chart
        if stats.daily_trend:
            lines.append(draw_line_chart(
                stats.daily_trend,
                height=8,
                title=color_text("  Daily Earnings Trend (Last 7 Days)", "bold"),
            ))
            lines.append("")

        # 最近任务列表 / Recent tasks
        lines.append(self._render_recent_tasks())
        lines.append("")

        # 底部信息 / Footer
        lines.append(color_text("-" * 60, "dim"))
        lines.append(
            color_text("  Press Ctrl+C to exit", "dim")
            + color_text("  |  Auto-refresh: ", "dim")
            + color_text(f"{self.refresh_interval}s", "yellow")
        )

        return "\n".join(lines)

    def _render_metric_cards(self, stats: DashboardStats) -> str:
        """
        渲染核心指标卡片 / Render core metric cards

        Args:
            stats: 仪表盘统计数据 / Dashboard statistics

        Returns:
            卡片渲染字符串 / Card render string
        """
        currency = self.tracker.currency
        today = self.tracker.get_today_earnings()

        # 趋势计算 / Trend calculation
        daily = self.tracker.get_daily_earnings(2)
        dates = sorted(daily.keys())
        if len(dates) >= 2:
            yesterday = daily[dates[0]]
            today_val = daily[dates[1]]
            from earnflow.utils import calculate_trend
            growth_rate, direction = calculate_trend(today_val, yesterday)
            trend_str = f"{'+' if growth_rate > 0 else ''}{growth_rate:.1f}%"
            trend_color = "green" if direction == "up" else ("red" if direction == "down" else "yellow")
        else:
            trend_str = "N/A"
            trend_color = "dim"

        lines: List[str] = []
        lines.append(color_text("  +------------------------------------------+", "cyan"))
        lines.append(color_text("  |", "cyan") + color_text("          CORE METRICS", "bold") + "                    " + color_text("|", "cyan"))
        lines.append(color_text("  +------------------------------------------+", "cyan"))
        lines.append(
            color_text("  |", "cyan")
            + f"  Total Earnings:  "
            + color_text(f"{format_currency(stats.total_earnings, currency)}", "green", "bold")
            + " " * (60 - 30 - len(format_currency(stats.total_earnings, currency)))
            + color_text("|", "cyan")
        )
        lines.append(
            color_text("  |", "cyan")
            + f"  Today's Earnings: "
            + color_text(f"{format_currency(today, currency)}", "green")
            + f"  ({color_text(trend_str, trend_color)})"
            + " " * max(0, 60 - 35 - len(format_currency(today, currency)) - len(trend_str))
            + color_text("|", "cyan")
        )
        lines.append(
            color_text("  |", "cyan")
            + f"  Tasks Completed:  "
            + color_text(f"{stats.total_tasks}", "bold")
            + " / "
            + color_text(f"{stats.success_rate}%", "yellow" if stats.success_rate < 80 else "green")
            + " success"
            + " " * max(0, 60 - 35)
            + color_text("|", "cyan")
        )
        lines.append(
            color_text("  |", "cyan")
            + f"  Avg Reward:       "
            + color_text(f"{format_currency(stats.avg_reward, currency)}", "cyan")
            + " " * max(0, 60 - 30 - len(format_currency(stats.avg_reward, currency)))
            + color_text("|", "cyan")
        )
        lines.append(color_text("  +------------------------------------------+", "cyan"))

        return "\n".join(lines)

    def _render_recent_tasks(self, max_tasks: int = 8) -> str:
        """
        渲染最近任务列表 / Render recent tasks list

        Args:
            max_tasks: 最大显示任务数 / Max tasks to display

        Returns:
            任务列表字符串 / Task list string
        """
        lines: List[str] = []

        lines.append(color_text("  Recent Tasks:", "bold"))
        lines.append(color_text(f"  {'ID':<14} {'Title':<25} {'Status':<12} {'Reward':>10}", "dim"))
        lines.append(color_text("  " + "-" * 63, "dim"))

        recent = self.tasks[-max_tasks:] if self.tasks else []
        if not recent:
            lines.append(color_text("  No tasks yet.", "dim"))
        else:
            for task in reversed(recent):
                status_colors = {
                    TaskStatus.COMPLETED: ("green", "[OK] "),
                    TaskStatus.RUNNING: ("cyan", "[>>] "),
                    TaskStatus.PENDING: ("dim", "[..] "),
                    TaskStatus.FAILED: ("red", "[!!] "),
                    TaskStatus.SKIPPED: ("yellow", "[--] "),
                }
                color, icon = status_colors.get(task.status, ("dim", "[??] "))

                title = task.title[:23] + ".." if len(task.title) > 25 else task.title
                lines.append(
                    f"  {task.id[:14]} "
                    f"{title:<25} "
                    f"{color_text(icon + task.status.value, color):<12} "
                    f"{format_currency(task.reward, self.tracker.currency):>10}"
                )

        return "\n".join(lines)

    def show(self, one_shot: bool = False) -> None:
        """
        显示仪表盘 / Show dashboard

        Args:
            one_shot: 是否只显示一次（不循环刷新）/ Whether to show only once (no loop refresh)
        """
        self._running = True

        try:
            while self._running:
                output = self.render()
                print(output, end="", flush=True)

                if one_shot:
                    break

                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            self._running = False
            print("\n\n  Dashboard closed. Goodbye!")
        finally:
            self._running = False

    def stop(self) -> None:
        """停止仪表盘刷新 / Stop dashboard refresh"""
        self._running = False
