"""
EarnFlow 报告生成模块 / Report Generation Module

支持多格式报告导出，包括JSON、CSV、Markdown和HTML。
HTML报告包含内联CSS样式，美观专业。
Supports multi-format report export including JSON, CSV, Markdown, and HTML.
HTML reports include inline CSS styles for a professional appearance.
"""

from __future__ import annotations

import csv
import io
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from earnflow.models import DashboardStats, Task, TaskResult, EarningRecord
from earnflow.utils import (
    format_currency,
    format_duration,
    get_datetime_str,
    get_date_str,
    percentage,
)


# ============================================================
# 报告生成器 / Report Generator
# ============================================================


class ReportGenerator:
    """
    报告生成器 / Report Generator

    根据收益追踪数据和任务数据生成多格式的报告。
    Generates multi-format reports based on earnings tracking and task data.

    Attributes:
        currency: 货币类型 / Currency type
        date_format: 日期格式 / Date format
    """

    def __init__(
        self,
        currency: str = "CNY",
        date_format: str = "%Y-%m-%d %H:%M:%S",
    ) -> None:
        """
        初始化报告生成器 / Initialize report generator

        Args:
            currency: 货币类型 / Currency type
            date_format: 日期格式 / Date format
        """
        self.currency = currency
        self.date_format = date_format

    # ========================================================
    # JSON 报告 / JSON Report
    # ========================================================

    def generate_json(
        self,
        stats: DashboardStats,
        tasks: Optional[List[Task]] = None,
        records: Optional[List[EarningRecord]] = None,
    ) -> str:
        """
        生成JSON格式报告 / Generate JSON format report

        Args:
            stats: 仪表盘统计数据 / Dashboard statistics
            tasks: 任务列表（可选）/ Task list (optional)
            records: 收益记录列表（可选）/ Earning record list (optional)

        Returns:
            JSON字符串 / JSON string
        """
        report: Dict[str, Any] = {
            "report_title": "EarnFlow Report",
            "generated_at": get_datetime_str(fmt=self.date_format),
            "currency": self.currency,
            "summary": {
                "total_earnings": stats.total_earnings,
                "total_tasks": stats.total_tasks,
                "success_rate": stats.success_rate,
                "avg_reward": stats.avg_reward,
            },
            "category_breakdown": stats.category_breakdown,
            "daily_trend": stats.daily_trend,
        }

        if tasks:
            report["tasks"] = [
                {
                    "id": t.id,
                    "title": t.title,
                    "category": t.category.value,
                    "status": t.status.value,
                    "reward": t.reward,
                    "created_at": get_datetime_str(t.created_at, self.date_format),
                }
                for t in tasks
            ]

        if records:
            report["earnings"] = [
                {
                    "id": r.id,
                    "task_id": r.task_id,
                    "amount": r.amount,
                    "timestamp": get_datetime_str(r.timestamp, self.date_format),
                    "category": r.category,
                }
                for r in records
            ]

        return json.dumps(report, indent=2, ensure_ascii=False)

    # ========================================================
    # CSV 报告 / CSV Report
    # ========================================================

    def generate_csv(
        self,
        records: List[EarningRecord],
        include_header: bool = True,
    ) -> str:
        """
        生成CSV格式报告 / Generate CSV format report

        Args:
            records: 收益记录列表 / Earning record list
            include_header: 是否包含表头 / Whether to include header

        Returns:
            CSV字符串 / CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        if include_header:
            writer.writerow(["ID", "Task ID", "Amount", "Currency", "Timestamp", "Category"])

        for record in records:
            writer.writerow([
                record.id,
                record.task_id,
                record.amount,
                record.currency,
                get_datetime_str(record.timestamp, self.date_format),
                record.category,
            ])

        return output.getvalue()

    def generate_task_csv(
        self,
        tasks: List[Task],
        include_header: bool = True,
    ) -> str:
        """
        生成任务CSV报告 / Generate task CSV report

        Args:
            tasks: 任务列表 / Task list
            include_header: 是否包含表头 / Whether to include header

        Returns:
            CSV字符串 / CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        if include_header:
            writer.writerow([
                "ID", "Title", "Category", "Priority", "Status",
                "Reward", "Estimated Time", "Tags", "Created At",
            ])

        for task in tasks:
            writer.writerow([
                task.id,
                task.title,
                task.category.value,
                task.priority.value,
                task.status.value,
                task.reward,
                task.estimated_time,
                ",".join(task.tags),
                get_datetime_str(task.created_at, self.date_format),
            ])

        return output.getvalue()

    # ========================================================
    # Markdown 报告 / Markdown Report
    # ========================================================

    def generate_markdown(
        self,
        stats: DashboardStats,
        tasks: Optional[List[Task]] = None,
        records: Optional[List[EarningRecord]] = None,
    ) -> str:
        """
        生成Markdown格式报告 / Generate Markdown format report

        Args:
            stats: 仪表盘统计数据 / Dashboard statistics
            tasks: 任务列表（可选）/ Task list (optional)
            records: 收益记录列表（可选）/ Earning record list (optional)

        Returns:
            Markdown字符串 / Markdown string
        """
        lines: List[str] = []

        # 标题 / Header
        lines.append("# EarnFlow Report")
        lines.append(f"> Generated at {get_datetime_str(fmt=self.date_format)}")
        lines.append("")

        # 概览 / Overview
        lines.append("## Overview")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| **Total Earnings** | {format_currency(stats.total_earnings, self.currency)} |")
        lines.append(f"| **Total Tasks** | {stats.total_tasks} |")
        lines.append(f"| **Success Rate** | {stats.success_rate}% |")
        lines.append(f"| **Avg Reward** | {format_currency(stats.avg_reward, self.currency)} |")
        lines.append("")

        # 分类明细 / Category Breakdown
        if stats.category_breakdown:
            lines.append("## Category Breakdown")
            lines.append("")
            lines.append("| Category | Earnings | Percentage |")
            lines.append("|----------|----------|------------|")
            total = stats.total_earnings or 1
            for cat, amount in sorted(stats.category_breakdown.items(), key=lambda x: x[1], reverse=True):
                pct = percentage(amount, total)
                lines.append(f"| {cat} | {format_currency(amount, self.currency)} | {pct}% |")
            lines.append("")

            # ASCII 柱状图 / ASCII bar chart
            lines.append("### Category Chart")
            lines.append("```")
            max_amount = max(stats.category_breakdown.values()) if stats.category_breakdown else 1
            bar_width = 30
            for cat, amount in sorted(stats.category_breakdown.items(), key=lambda x: x[1], reverse=True):
                bar_len = int((amount / max_amount) * bar_width) if max_amount > 0 else 0
                bar = "#" * bar_len
                lines.append(f"  {cat:<15} {bar} {format_currency(amount, self.currency, show_symbol=False)}")
            lines.append("```")
            lines.append("")

        # 每日趋势 / Daily Trend
        if stats.daily_trend:
            lines.append("## Daily Trend (Last 7 Days)")
            lines.append("")
            lines.append("| Date | Earnings |")
            lines.append("|------|----------|")
            for date, amount in sorted(stats.daily_trend.items()):
                lines.append(f"| {date} | {format_currency(amount, self.currency)} |")
            lines.append("")

            # ASCII 折线图 / ASCII line chart
            lines.append("### Trend Chart")
            lines.append("```")
            amounts = list(stats.daily_trend.values())
            dates = list(stats.daily_trend.keys())
            if amounts:
                max_val = max(amounts) if max(amounts) > 0 else 1
                chart_height = 8
                for row in range(chart_height, -1, -1):
                    threshold = (max_val / chart_height) * row
                    row_str = f"  {threshold:>8.1f} |"
                    for amount in amounts:
                        if amount >= threshold:
                            row_str += "  *"
                        else:
                            row_str += "   "
                    lines.append(row_str)
                # X轴标签 / X-axis labels
                lines.append("         +" + "---" * len(amounts))
                label_str = "          "
                for date in dates:
                    label_str += f" {date[-2:]}"
                lines.append(label_str)
            lines.append("```")
            lines.append("")

        # 任务列表 / Task List
        if tasks:
            lines.append("## Recent Tasks")
            lines.append("")
            lines.append("| ID | Title | Category | Status | Reward |")
            lines.append("|----|-------|----------|--------|--------|")
            for task in tasks[:20]:
                status_icon = {
                    "completed": "[x]",
                    "running": "[>]",
                    "pending": "[ ]",
                    "failed": "[!]",
                    "skipped": "[-]",
                }.get(task.status.value, "[?]")
                lines.append(
                    f"| {task.id[:12]} | {task.title[:30]} | "
                    f"{task.category.value} | {status_icon} {task.status.value} | "
                    f"{format_currency(task.reward, self.currency)} |"
                )
            lines.append("")

        # 最近收益 / Recent Earnings
        if records:
            lines.append("## Recent Earnings")
            lines.append("")
            lines.append("| ID | Task | Amount | Category | Time |")
            lines.append("|----|------|--------|----------|------|")
            for record in records[:20]:
                lines.append(
                    f"| {record.id[:12]} | {record.task_id[:12]} | "
                    f"{format_currency(record.amount, self.currency)} | "
                    f"{record.category} | {get_datetime_str(record.timestamp, '%m-%d %H:%M')} |"
                )
            lines.append("")

        lines.append("---")
        lines.append("*Report generated by EarnFlow*")

        return "\n".join(lines)

    # ========================================================
    # HTML 报告 / HTML Report
    # ========================================================

    def generate_html(
        self,
        stats: DashboardStats,
        tasks: Optional[List[Task]] = None,
        records: Optional[List[EarningRecord]] = None,
    ) -> str:
        """
        生成HTML格式报告（含内联CSS）/ Generate HTML format report (with inline CSS)

        Args:
            stats: 仪表盘统计数据 / Dashboard statistics
            tasks: 任务列表（可选）/ Task list (optional)
            records: 收益记录列表（可选）/ Earning record list (optional)

        Returns:
            HTML字符串 / HTML string
        """
        # 分类柱状图SVG / Category bar chart SVG
        category_chart = self._build_category_svg(stats.category_breakdown)

        # 趋势折线图SVG / Trend line chart SVG
        trend_chart = self._build_trend_svg(stats.daily_trend)

        # 任务表格行 / Task table rows
        task_rows = ""
        if tasks:
            for task in tasks[:20]:
                status_class = task.status.value
                task_rows += f"""
                <tr>
                    <td class="mono">{task.id[:12]}</td>
                    <td>{self._escape_html(task.title[:40])}</td>
                    <td><span class="badge">{task.category.value}</span></td>
                    <td><span class="status {status_class}">{task.status.value}</span></td>
                    <td class="mono">{format_currency(task.reward, self.currency)}</td>
                </tr>"""

        # 收益表格行 / Earnings table rows
        earning_rows = ""
        if records:
            for record in records[:20]:
                earning_rows += f"""
                <tr>
                    <td class="mono">{record.id[:12]}</td>
                    <td class="mono">{record.task_id[:12]}</td>
                    <td class="mono">{format_currency(record.amount, self.currency)}</td>
                    <td><span class="badge">{record.category}</span></td>
                    <td class="mono">{get_datetime_str(record.timestamp, '%m-%d %H:%M')}</td>
                </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EarnFlow Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{
            text-align: center;
            padding: 2rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        .header .subtitle {{ color: #888; font-size: 0.9rem; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-2px); }}
        .stat-card .label {{ font-size: 0.85rem; color: #888; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px; }}
        .stat-card .value {{ font-size: 2rem; font-weight: 700; color: #00d2ff; }}
        .stat-card .value.green {{ color: #00e676; }}
        .stat-card .value.orange {{ color: #ffab40; }}
        .section {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .section h2 {{
            font-size: 1.3rem;
            margin-bottom: 1rem;
            color: #fff;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .chart-container {{ text-align: center; padding: 1rem 0; }}
        .chart-container svg {{ max-width: 100%; height: auto; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        th {{
            text-align: left;
            padding: 0.75rem;
            color: #888;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 1px;
        }}
        td {{
            padding: 0.75rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        tr:hover td {{ background: rgba(255,255,255,0.03); }}
        .mono {{ font-family: 'SF Mono', 'Fira Code', monospace; font-size: 0.8rem; }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            background: rgba(58, 123, 213, 0.2);
            color: #3a7bd5;
        }}
        .status {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }}
        .status.completed {{ background: rgba(0, 230, 118, 0.2); color: #00e676; }}
        .status.running {{ background: rgba(0, 210, 255, 0.2); color: #00d2ff; }}
        .status.pending {{ background: rgba(255, 255, 255, 0.1); color: #888; }}
        .status.failed {{ background: rgba(255, 82, 82, 0.2); color: #ff5252; }}
        .status.skipped {{ background: rgba(255, 171, 64, 0.2); color: #ffab40; }}
        .footer {{
            text-align: center;
            padding: 2rem 0;
            color: #555;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>EarnFlow Report</h1>
            <p class="subtitle">Generated at {get_datetime_str(fmt=self.date_format)}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Earnings</div>
                <div class="value">{format_currency(stats.total_earnings, self.currency)}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Tasks</div>
                <div class="value">{stats.total_tasks}</div>
            </div>
            <div class="stat-card">
                <div class="label">Success Rate</div>
                <div class="value green">{stats.success_rate}%</div>
            </div>
            <div class="stat-card">
                <div class="label">Avg Reward</div>
                <div class="value orange">{format_currency(stats.avg_reward, self.currency)}</div>
            </div>
        </div>

        <div class="section">
            <h2>Category Breakdown</h2>
            <div class="chart-container">{category_chart}</div>
        </div>

        <div class="section">
            <h2>Daily Trend (Last 7 Days)</h2>
            <div class="chart-container">{trend_chart}</div>
        </div>

        {"<div class='section'><h2>Recent Tasks</h2><table><tr><th>ID</th><th>Title</th><th>Category</th><th>Status</th><th>Reward</th></tr>" + task_rows + "</table></div>" if tasks else ""}

        {"<div class='section'><h2>Recent Earnings</h2><table><tr><th>ID</th><th>Task</th><th>Amount</th><th>Category</th><th>Time</th></tr>" + earning_rows + "</table></div>" if records else ""}

        <div class="footer">
            <p>Powered by EarnFlow - Lightweight AI Automated Task Earning Engine</p>
        </div>
    </div>
</body>
</html>"""
        return html

    # ========================================================
    # 通用导出 / Generic Export
    # ========================================================

    def generate(
        self,
        fmt: str,
        stats: DashboardStats,
        tasks: Optional[List[Task]] = None,
        records: Optional[List[EarningRecord]] = None,
    ) -> str:
        """
        根据格式生成报告 / Generate report in specified format

        Args:
            fmt: 报告格式（json/csv/markdown/html）/ Report format
            stats: 仪表盘统计数据 / Dashboard statistics
            tasks: 任务列表（可选）/ Task list (optional)
            records: 收益记录列表（可选）/ Earning record list (optional)

        Returns:
            报告字符串 / Report string

        Raises:
            ValueError: 不支持的格式 / Unsupported format
        """
        generators = {
            "json": lambda: self.generate_json(stats, tasks, records),
            "csv": lambda: self.generate_csv(records or []),
            "markdown": lambda: self.generate_markdown(stats, tasks, records),
            "md": lambda: self.generate_markdown(stats, tasks, records),
            "html": lambda: self.generate_html(stats, tasks, records),
        }

        generator = generators.get(fmt.lower())
        if not generator:
            raise ValueError(
                f"Unsupported format: {fmt}. Supported: {', '.join(generators.keys())}"
            )
        return generator()

    def save_report(
        self,
        fmt: str,
        output_path: str,
        stats: DashboardStats,
        tasks: Optional[List[Task]] = None,
        records: Optional[List[EarningRecord]] = None,
    ) -> str:
        """
        生成并保存报告到文件 / Generate and save report to file

        Args:
            fmt: 报告格式 / Report format
            output_path: 输出文件路径 / Output file path
            stats: 仪表盘统计数据 / Dashboard statistics
            tasks: 任务列表（可选）/ Task list (optional)
            records: 收益记录列表（可选）/ Earning record list (optional)

        Returns:
            保存的文件路径 / Saved file path
        """
        content = self.generate(fmt, stats, tasks, records)

        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    # ========================================================
    # 图表生成 / Chart Generation
    # ========================================================

    @staticmethod
    def _build_category_svg(category_breakdown: Dict[str, float]) -> str:
        """
        构建分类柱状图SVG / Build category bar chart SVG

        Args:
            category_breakdown: 分类收益数据 / Category earnings data

        Returns:
            SVG字符串 / SVG string
        """
        if not category_breakdown:
            return "<p>No category data available.</p>"

        sorted_cats = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)
        max_val = max(v for _, v in sorted_cats) or 1

        colors = ["#00d2ff", "#3a7bd5", "#00e676", "#ffab40", "#ff5252", "#e040fb", "#7c4dff"]
        bar_width = 60
        gap = 20
        chart_width = len(sorted_cats) * (bar_width + gap) + 40
        chart_height = 200
        svg_parts: List[str] = []

        svg_parts.append(
            f'<svg width="{chart_width}" height="{chart_height}" '
            f'xmlns="http://www.w3.org/2000/svg">'
        )

        for i, (cat, amount) in enumerate(sorted_cats):
            x = 30 + i * (bar_width + gap)
            bar_height = int((amount / max_val) * (chart_height - 60))
            y = chart_height - 30 - bar_height
            color = colors[i % len(colors)]

            # 柱体 / Bar
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" '
                f'rx="4" fill="{color}" opacity="0.8">'
            )
            svg_parts.append(
                f'<animate attributeName="height" from="0" to="{bar_height}" '
                f'dur="0.8s" fill="freeze"/>'
            )
            svg_parts.append(
                f'<animate attributeName="y" from="{chart_height - 30}" to="{y}" '
                f'dur="0.8s" fill="freeze"/>'
            )
            svg_parts.append('</rect>')

            # 标签 / Label
            svg_parts.append(
                f'<text x="{x + bar_width // 2}" y="{chart_height - 10}" '
                f'text-anchor="middle" fill="#888" font-size="10">{cat[:10]}</text>'
            )

            # 数值 / Value
            svg_parts.append(
                f'<text x="{x + bar_width // 2}" y="{y - 5}" '
                f'text-anchor="middle" fill="#fff" font-size="11" font-weight="bold">'
                f'{amount:.1f}</text>'
            )

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)

    @staticmethod
    def _build_trend_svg(daily_trend: Dict[str, float]) -> str:
        """
        构建趋势折线图SVG / Build trend line chart SVG

        Args:
            daily_trend: 每日趋势数据 / Daily trend data

        Returns:
            SVG字符串 / SVG string
        """
        if not daily_trend:
            return "<p>No trend data available.</p>"

        sorted_dates = sorted(daily_trend.items())
        amounts = [v for _, v in sorted_dates]
        dates = [k for k, _ in sorted_dates]

        max_val = max(amounts) if max(amounts) > 0 else 1
        chart_width = 600
        chart_height = 200
        padding = 40
        plot_width = chart_width - 2 * padding
        plot_height = chart_height - 2 * padding

        svg_parts: List[str] = []
        svg_parts.append(
            f'<svg width="{chart_width}" height="{chart_height}" '
            f'xmlns="http://www.w3.org/2000/svg">'
        )

        # 网格线 / Grid lines
        for i in range(5):
            y = padding + int((plot_height / 4) * i)
            val = max_val - (max_val / 4) * i
            svg_parts.append(
                f'<line x1="{padding}" y1="{y}" x2="{chart_width - padding}" y2="{y}" '
                f'stroke="rgba(255,255,255,0.05)" stroke-width="1"/>'
            )
            svg_parts.append(
                f'<text x="{padding - 5}" y="{y + 4}" text-anchor="end" '
                f'fill="#555" font-size="9">{val:.1f}</text>'
            )

        # 数据点坐标 / Data point coordinates
        if len(amounts) > 1:
            points: List[str] = []
            for i, amount in enumerate(amounts):
                x = padding + int((plot_width / (len(amounts) - 1)) * i)
                y = padding + plot_height - int((amount / max_val) * plot_height)
                points.append(f"{x},{y}")

            # 渐变填充区域 / Gradient fill area
            first_x = padding
            last_x = padding + plot_width
            area_points = f"{first_x},{padding + plot_height} " + " ".join(points) + f" {last_x},{padding + plot_height}"
            svg_parts.append(f'<defs><linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">')
            svg_parts.append(f'<stop offset="0%" stop-color="#00d2ff" stop-opacity="0.3"/>')
            svg_parts.append(f'<stop offset="100%" stop-color="#00d2ff" stop-opacity="0.02"/>')
            svg_parts.append(f'</linearGradient></defs>')
            svg_parts.append(
                f'<polygon points="{area_points}" fill="url(#trendGrad)"/>'
            )

            # 折线 / Line
            svg_parts.append(
                f'<polyline points="{" ".join(points)}" fill="none" '
                f'stroke="#00d2ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            )

            # 数据点 / Data points
            for i, (px, amount) in enumerate(zip(points, amounts)):
                x, y = px.split(",")
                svg_parts.append(
                    f'<circle cx="{x}" cy="{y}" r="4" fill="#00d2ff" stroke="#0f0c29" stroke-width="2"/>'
                )

        # X轴标签 / X-axis labels
        for i, date in enumerate(dates):
            x = padding + int((plot_width / max(len(dates) - 1, 1)) * i)
            svg_parts.append(
                f'<text x="{x}" y="{chart_height - 5}" text-anchor="middle" '
                f'fill="#555" font-size="9">{date[-5:]}</text>'
            )

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)

    # ========================================================
    # 辅助方法 / Helper Methods
    # ========================================================

    @staticmethod
    def _escape_html(text: str) -> str:
        """
        转义HTML特殊字符 / Escape HTML special characters

        Args:
            text: 输入文本 / Input text

        Returns:
            转义后的文本 / Escaped text
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
