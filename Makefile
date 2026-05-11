.PHONY: help install dev test clean run demo list stats report dashboard config

# 默认目标 / Default target
help:
	@echo "EarnFlow - Lightweight AI Automated Task Earning Engine"
	@echo ""
	@echo "Available targets:"
	@echo "  make install   - Install the package in development mode"
	@echo "  make dev       - Install with dev dependencies"
	@echo "  make test      - Run all tests"
	@echo "  make clean     - Clean build artifacts and cache"
	@echo "  make run       - Run the task engine (demo mode)"
	@echo "  make demo      - Run demo with 10 tasks"
	@echo "  make list      - List available handlers and templates"
	@echo "  make stats     - Show earnings statistics"
	@echo "  make report    - Generate a report"
	@echo "  make dashboard - Open TUI dashboard"
	@echo "  make config    - Show current configuration"

# 安装 / Install
install:
	pip install -e .

# 开发模式安装 / Install in dev mode
dev:
	pip install -e ".[dev]"

# 运行测试 / Run tests
test:
	python -m pytest tests/ -v --tb=short

# 快速测试（unittest） / Quick test with unittest
test-quick:
	python -m unittest discover -s tests -v

# 清理 / Clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/
	rm -rf earnflow_data/ earnflow_reports/
	rm -f earnflow_config.json

# 运行引擎 / Run engine
run:
	python -m earnflow.cli run --demo --count 5

# 演示模式 / Demo mode
demo:
	python -m earnflow.cli run --demo --count 10 --priority medium

# 列出可用项 / List available items
list:
	python -m earnflow.cli list all

# 查看统计 / View statistics
stats:
	python -m earnflow.cli stats --detailed

# 生成报告 / Generate report
report:
	python -m earnflow.cli report --format markdown

# 生成HTML报告 / Generate HTML report
report-html:
	python -m earnflow.cli report --format html

# 仪表盘 / Dashboard
dashboard:
	python -m earnflow.cli dashboard

# 一次性仪表盘 / One-shot dashboard
dashboard-once:
	python -m earnflow.cli dashboard --once

# 配置管理 / Configuration
config:
	python -m earnflow.cli config show

# 验证配置 / Validate configuration
config-validate:
	python -m earnflow.cli config validate

# 重置配置 / Reset configuration
config-reset:
	python -m earnflow.cli config reset
