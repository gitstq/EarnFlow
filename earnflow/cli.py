"""
EarnFlow CLI入口模块 / CLI Entry Module

提供命令行接口，支持以下命令：
- earnflow run       - 运行任务引擎
- earnflow list      - 列出可用任务
- earnflow stats     - 查看收益统计
- earnflow report    - 生成报告
- earnflow dashboard - 打开TUI仪表盘
- earnflow config    - 管理配置

Provides command-line interface with the following commands:
- earnflow run       - Run task engine
- earnflow list      - List available tasks
- earnflow stats     - View earnings statistics
- earnflow report    - Generate report
- earnflow dashboard - Open TUI dashboard
- earnflow config    - Manage configuration
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import List, Optional

# 确保可以导入包内模块 / Ensure intra-package imports work
try:
    from earnflow import __version__
except ImportError:
    # 开发模式下的导入回退 / Import fallback for development mode
    __version__ = "1.0.0"

from earnflow.config import ConfigManager
from earnflow.engine import TaskEngine
from earnflow.models import Task, TaskCategory, TaskPriority, TaskTemplate
from earnflow.plugins import PluginRegistry
from earnflow.reporter import ReportGenerator
from earnflow.tracker import EarningTracker
from earnflow.utils import (
    color_text,
    format_currency,
    format_duration,
    get_datetime_str,
    print_colored,
)


# ============================================================
# CLI 命令处理器 / CLI Command Handlers
# ============================================================


def cmd_run(args: argparse.Namespace) -> int:
    """
    执行 run 命令 - 运行任务引擎 / Execute run command - Run task engine

    Args:
        args: 命令行参数 / Command-line arguments

    Returns:
        退出码 / Exit code
    """
    print_colored("EarnFlow Task Engine", "bold", "cyan")
    print_colored("=" * 50, "dim")
    print()

    # 初始化引擎 / Initialize engine
    config = ConfigManager(args.config)
    engine = TaskEngine(config=config)

    # 加载模板并创建任务 / Load templates and create tasks
    template_path = args.template
    if template_path and os.path.exists(template_path):
        task_ids = engine.create_tasks_from_templates(
            template_path,
            count=args.count,
            priority=TaskPriority(args.priority) if args.priority else TaskPriority.MEDIUM,
        )
        print_colored(f"  Created {len(task_ids)} tasks from templates.", "green")
    elif args.demo:
        # 演示模式：生成模拟任务 / Demo mode: generate simulated tasks
        print_colored("  Demo mode: generating sample tasks...", "yellow")
        _generate_demo_tasks(engine, args.count)
        print_colored(f"  Generated {args.count} demo tasks.", "green")
    else:
        print_colored("  No tasks to run. Use --template or --demo.", "yellow")
        return 0

    print()
    print_colored(f"  Queue size: {engine.queue_size}", "dim")
    print_colored(f"  Max concurrent: {config.get('max_concurrent', 4)}", "dim")
    print()

    # 注册进度回调 / Register progress callback
    def progress_cb(task: Task, message: str) -> None:
        status_colors = {
            "Completed": "green",
            "failed": "red",
            "started": "cyan",
            "added": "dim",
        }
        color = "dim"
        for key, c in status_colors.items():
            if key.lower() in message.lower():
                color = c
                break
        print_colored(f"  [{task.id[:8]}] {message}", color)

    engine.on_progress(progress_cb)

    # 运行引擎 / Run engine
    print_colored("  Starting engine...", "bold")
    print_colored("-" * 50, "dim")

    start = time.time()
    summary = engine.run(max_tasks=args.max_tasks)
    elapsed = time.time() - start

    print_colored("-" * 50, "dim")
    print()

    # 显示结果 / Show results
    print_colored("  Execution Summary", "bold", "cyan")
    print_colored(f"  Status:        {summary['status']}", "green" if summary["status"] == "completed" else "yellow")
    print_colored(f"  Executed:      {summary['executed']}", "dim")
    print_colored(f"  Completed:     {color_text(str(summary['completed']), 'green')}", "dim")
    print_colored(f"  Failed:        {color_text(str(summary['failed']), 'red' if summary['failed'] > 0 else 'dim')}", "dim")
    print_colored(f"  Success Rate:  {summary['success_rate']}%", "green" if summary['success_rate'] >= 80 else "yellow")
    print_colored(f"  Total Earnings:{format_currency(summary['total_earnings'], config.get('currency', 'CNY'))}", "green", "bold")
    print_colored(f"  Duration:      {format_duration(elapsed)}", "dim")
    print()

    # 保存状态 / Save state
    engine.save_state()
    print_colored("  State saved.", "dim")

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """
    执行 list 命令 - 列出可用任务和处理器 / Execute list command

    Args:
        args: 命令行参数 / Command-line arguments

    Returns:
        退出码 / Exit code
    """
    registry = PluginRegistry()

    if args.type in ("handlers", "all"):
        print_colored("  Registered Task Handlers", "bold", "cyan")
        print_colored("  " + "-" * 55, "dim")
        handlers = registry.list_handlers()
        for h in handlers:
            print_colored(f"    {h['name']:<18} {h['category']:<16} {h['description']}", "dim")
        print()

    if args.type in ("templates", "all"):
        print_colored("  Task Templates", "bold", "cyan")
        print_colored("  " + "-" * 55, "dim")

        # 查找模板文件 / Find template files
        template_dirs = [
            args.template,
            "templates/default_tasks.json",
            os.path.join(os.path.dirname(__file__), "..", "templates", "default_tasks.json"),
        ]

        engine = TaskEngine()
        for tpath in template_dirs:
            if tpath and os.path.exists(tpath):
                templates = engine.load_templates(tpath)
                for t in templates:
                    print_colored(
                        f"    {t.name:<25} [{t.category}] "
                        f"reward={t.base_reward:.2f}  tags={t.required_tags}",
                        "dim",
                    )
                break
        else:
            print_colored("    No template files found.", "yellow")
        print()

    if args.type in ("categories", "all"):
        print_colored("  Task Categories", "bold", "cyan")
        print_colored("  " + "-" * 55, "dim")
        for cat in TaskCategory:
            print_colored(f"    {cat.value:<20} {cat.name}", "dim")
        print()

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """
    执行 stats 命令 - 查看收益统计 / Execute stats command

    Args:
        args: 命令行参数 / Command-line arguments

    Returns:
        退出码 / Exit code
    """
    config = ConfigManager(args.config)
    tracker = EarningTracker(
        currency=config.get("currency", "CNY"),
        storage_path=os.path.join(config.get("work_dir", "./earnflow_data"), "earnings.json"),
    )

    print_colored("  Earnings Statistics", "bold", "cyan")
    print_colored("=" * 50, "dim")
    print()

    # 基本信息 / Basic info
    print_colored(f"  Total Earnings:   {format_currency(tracker.total_earnings, tracker.currency)}", "green", "bold")
    print_colored(f"  Today's Earnings: {format_currency(tracker.get_today_earnings(), tracker.currency)}", "green")
    print_colored(f"  Total Records:    {tracker.record_count}", "dim")
    print_colored(f"  Avg per Record:   {format_currency(tracker.get_average_earnings(), tracker.currency)}", "dim")
    print()

    # 分类明细 / Category breakdown
    if args.detailed:
        cat_earnings = tracker.get_earnings_by_category()
        if cat_earnings:
            print_colored("  Category Breakdown:", "bold")
            for cat, amount in sorted(cat_earnings.items(), key=lambda x: x[1], reverse=True):
                pct = (amount / tracker.total_earnings * 100) if tracker.total_earnings > 0 else 0
                bar = "#" * int(pct / 5)
                print_colored(
                    f"    {cat:<18} {format_currency(amount, tracker.currency):>10}  "
                    f"{color_text(bar, 'cyan')} {pct:.1f}%",
                    "dim",
                )
            print()

        # 每日趋势 / Daily trend
        daily = tracker.get_daily_earnings(7)
        if daily:
            print_colored("  Daily Trend (7 days):", "bold")
            for date, amount in sorted(daily.items()):
                bar = "#" * max(1, int(amount / max(daily.values()) * 20)) if max(daily.values()) > 0 else ""
                print_colored(
                    f"    {date}  {format_currency(amount, tracker.currency):>10}  {color_text(bar, 'green')}",
                    "dim",
                )
            print()

    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """
    执行 report 命令 - 生成报告 / Execute report command

    Args:
        args: 命令行参数 / Command-line arguments

    Returns:
        退出码 / Exit code
    """
    config = ConfigManager(args.config)

    # 加载数据 / Load data
    tracker = EarningTracker(
        currency=config.get("currency", "CNY"),
        storage_path=os.path.join(config.get("work_dir", "./earnflow_data"), "earnings.json"),
    )

    engine = TaskEngine(config=config, tracker=tracker)
    engine.load_state()

    # 生成统计 / Generate statistics
    summary = engine.get_summary()
    stats = tracker.get_dashboard_stats(
        total_tasks=summary["total_tasks"],
        success_count=summary["completed"],
    )

    # 生成报告 / Generate report
    reporter = ReportGenerator(
        currency=config.get("currency", "CNY"),
        date_format=config.get("date_format", "%Y-%m-%d %H:%M:%S"),
    )

    fmt = args.format or config.get("default_format", "markdown")
    output_dir = config.get("output_dir", "./earnflow_reports")

    if args.output:
        output_path = args.output
    else:
        ext = {"markdown": "md", "md": "md", "html": "html", "json": "json", "csv": "csv"}.get(fmt, "txt")
        output_path = os.path.join(output_dir, f"earnflow_report.{ext}")

    try:
        saved_path = reporter.save_report(
            fmt=fmt,
            output_path=output_path,
            stats=stats,
            tasks=engine.all_tasks,
            records=tracker.records,
        )
        print_colored(f"  Report generated: {saved_path}", "green")
        print_colored(f"  Format: {fmt}", "dim")
        print_colored(f"  Total earnings: {format_currency(stats.total_earnings, tracker.currency)}", "dim")
        return 0
    except ValueError as e:
        print_colored(f"  Error: {e}", "red")
        return 1


def cmd_dashboard(args: argparse.Namespace) -> int:
    """
    执行 dashboard 命令 - 打开TUI仪表盘 / Execute dashboard command

    Args:
        args: 命令行参数 / Command-line arguments

    Returns:
        退出码 / Exit code
    """
    from earnflow.dashboard import Dashboard

    config = ConfigManager(args.config)
    tracker = EarningTracker(
        currency=config.get("currency", "CNY"),
        storage_path=os.path.join(config.get("work_dir", "./earnflow_data"), "earnings.json"),
    )

    engine = TaskEngine(config=config, tracker=tracker)
    engine.load_state()

    dashboard = Dashboard(
        tracker=tracker,
        tasks=engine.all_tasks,
        refresh_interval=config.get("dashboard_refresh", 5),
    )

    dashboard.show(one_shot=args.once)
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """
    执行 config 命令 - 管理配置 / Execute config command

    Args:
        args: 命令行参数 / Command-line arguments

    Returns:
        退出码 / Exit code
    """
    config = ConfigManager(args.config)

    if args.action == "show":
        import json
        print_colored("  Current Configuration", "bold", "cyan")
        print_colored("=" * 50, "dim")
        print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
        return 0

    elif args.action == "reset":
        config.reset()
        config.save()
        print_colored("  Configuration reset to defaults.", "green")
        return 0

    elif args.action == "save":
        config.save(args.output)
        print_colored(f"  Configuration saved to: {args.output or config.config_path}", "green")
        return 0

    elif args.action == "validate":
        is_valid, errors = config.validate()
        if is_valid:
            print_colored("  Configuration is valid.", "green")
        else:
            print_colored("  Configuration errors:", "red")
            for err in errors:
                print_colored(f"    - {err}", "red")
        return 0 if is_valid else 1

    else:
        print_colored(f"  Unknown action: {args.action}", "red")
        return 1


# ============================================================
# 辅助函数 / Helper Functions
# ============================================================


def _generate_demo_tasks(engine: TaskEngine, count: int = 5) -> None:
    """
    生成演示任务 / Generate demo tasks

    Args:
        engine: 任务引擎 / Task engine
        count: 任务数量 / Task count
    """
    demo_templates = [
        TaskTemplate(
            name="Blog Article Writing",
            description="Write a blog article on a given topic",
            category="content_gen",
            base_reward=15.0,
            steps=["Research topic", "Write draft", "Edit and polish"],
            required_tags=["writing", "blog"],
        ),
        TaskTemplate(
            name="Image Data Labeling",
            description="Label images for machine learning training",
            category="data_label",
            base_reward=8.0,
            steps=["Review images", "Apply labels", "Verify accuracy"],
            required_tags=["labeling", "images"],
        ),
        TaskTemplate(
            name="Technical Translation",
            description="Translate technical documents between languages",
            category="translation",
            base_reward=12.0,
            steps=["Analyze source", "Translate", "Review quality"],
            required_tags=["translation", "technical"],
        ),
        TaskTemplate(
            name="Code Review",
            description="Review code for quality, security, and best practices",
            category="code_review",
            base_reward=20.0,
            steps=["Read code", "Check patterns", "Write feedback"],
            required_tags=["code", "review"],
        ),
        TaskTemplate(
            name="QA Test Generation",
            description="Generate test cases for software modules",
            category="qa_test",
            base_reward=10.0,
            steps=["Analyze requirements", "Generate tests", "Validate coverage"],
            required_tags=["testing", "qa"],
        ),
        TaskTemplate(
            name="Market Research",
            description="Research market trends and compile analysis",
            category="research",
            base_reward=18.0,
            steps=["Gather data", "Analyze trends", "Write report"],
            required_tags=["research", "analysis"],
        ),
    ]

    priorities = list(TaskPriority)
    import random
    for i in range(count):
        template = demo_templates[i % len(demo_templates)]
        priority = random.choice(priorities)
        multiplier = random.uniform(0.8, 1.5)
        engine.add_task_from_template(
            template,
            priority=priority,
            reward_multiplier=round(multiplier, 2),
        )


# ============================================================
# 参数解析 / Argument Parsing
# ============================================================


def build_parser() -> argparse.ArgumentParser:
    """
    构建命令行参数解析器 / Build command-line argument parser

    Returns:
        ArgumentParser实例 / ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="earnflow",
        description="EarnFlow - Lightweight AI Automated Task Earning Engine",
        epilog="Example: earnflow run --demo --count 10",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"EarnFlow v{__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # run 命令 / run command
    run_parser = subparsers.add_parser("run", help="Run the task engine")
    run_parser.add_argument(
        "-t", "--template",
        help="Path to task template file (JSON)",
    )
    run_parser.add_argument(
        "-n", "--count",
        type=int,
        default=5,
        help="Number of tasks to create (default: 5)",
    )
    run_parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with sample tasks",
    )
    run_parser.add_argument(
        "--max-tasks",
        type=int,
        default=0,
        help="Max tasks to execute (0 = all, default: 0)",
    )
    run_parser.add_argument(
        "-p", "--priority",
        choices=["low", "medium", "high", "urgent"],
        default="medium",
        help="Task priority (default: medium)",
    )
    run_parser.add_argument(
        "-c", "--config",
        help="Path to configuration file",
    )

    # list 命令 / list command
    list_parser = subparsers.add_parser("list", help="List available tasks and handlers")
    list_parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["handlers", "templates", "categories", "all"],
        help="What to list (default: all)",
    )
    list_parser.add_argument(
        "--template",
        help="Path to template file",
    )

    # stats 命令 / stats command
    stats_parser = subparsers.add_parser("stats", help="View earnings statistics")
    stats_parser.add_argument(
        "-d", "--detailed",
        action="store_true",
        help="Show detailed statistics",
    )
    stats_parser.add_argument(
        "-c", "--config",
        help="Path to configuration file",
    )

    # report 命令 / report command
    report_parser = subparsers.add_parser("report", help="Generate a report")
    report_parser.add_argument(
        "-f", "--format",
        choices=["json", "csv", "markdown", "html"],
        help="Report format (default: from config)",
    )
    report_parser.add_argument(
        "-o", "--output",
        help="Output file path",
    )
    report_parser.add_argument(
        "-c", "--config",
        help="Path to configuration file",
    )

    # dashboard 命令 / dashboard command
    dash_parser = subparsers.add_parser("dashboard", help="Open TUI dashboard")
    dash_parser.add_argument(
        "--once",
        action="store_true",
        help="Show dashboard once (no auto-refresh)",
    )
    dash_parser.add_argument(
        "-c", "--config",
        help="Path to configuration file",
    )

    # config 命令 / config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "action",
        choices=["show", "reset", "save", "validate"],
        default="show",
        nargs="?",
        help="Config action (default: show)",
    )
    config_parser.add_argument(
        "-c", "--config",
        help="Path to configuration file",
    )
    config_parser.add_argument(
        "-o", "--output",
        help="Output file path (for save action)",
    )

    return parser


# ============================================================
# 主入口 / Main Entry Point
# ============================================================


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI主入口 / CLI main entry point

    Args:
        argv: 命令行参数（默认使用sys.argv）/ Command-line args (defaults to sys.argv)

    Returns:
        退出码 / Exit code
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    # 命令分发 / Command dispatch
    commands = {
        "run": cmd_run,
        "list": cmd_list,
        "stats": cmd_stats,
        "report": cmd_report,
        "dashboard": cmd_dashboard,
        "config": cmd_config,
    }

    handler = commands.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print_colored("\n  Interrupted.", "yellow")
            return 130
        except Exception as e:
            print_colored(f"  Error: {e}", "red")
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
