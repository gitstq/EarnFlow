"""
EarnFlow 配置管理模块 / Configuration Management Module

管理应用的配置加载、保存和验证。使用JSON格式作为配置文件格式，
避免YAML解析的外部依赖。
Manages application configuration loading, saving, and validation.
Uses JSON format for configuration files to avoid YAML parsing dependencies.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from earnflow.utils import validate_config


# ============================================================
# 默认配置 / Default Configuration
# ============================================================

DEFAULT_CONFIG: Dict[str, Any] = {
    # 基本设置 / Basic settings
    "currency": "CNY",                    # 货币单位 / Currency unit
    "work_dir": "./earnflow_data",        # 工作目录 / Working directory
    "output_dir": "./earnflow_reports",   # 报告输出目录 / Report output directory

    # 引擎设置 / Engine settings
    "max_concurrent": 4,                  # 最大并发数 / Max concurrent tasks
    "task_timeout": 300,                  # 任务超时时间（秒）/ Task timeout (seconds)
    "retry_limit": 2,                     # 失败重试次数 / Retry limit on failure
    "queue_size": 100,                    # 任务队列大小 / Task queue size

    # 匹配设置 / Matcher settings
    "min_match_score": 30,                # 最低匹配分数 / Minimum match score
    "keyword_weight": 0.4,                # 关键词权重 / Keyword weight
    "category_weight": 0.3,               # 分类权重 / Category weight
    "tag_weight": 0.3,                    # 标签权重 / Tag weight

    # 报告设置 / Report settings
    "default_format": "markdown",         # 默认报告格式 / Default report format
    "include_charts": True,               # 是否包含图表 / Whether to include charts
    "date_format": "%Y-%m-%d %H:%M:%S",  # 日期格式 / Date format

    # 仪表盘设置 / Dashboard settings
    "dashboard_refresh": 5,               # 仪表盘刷新间隔（秒）/ Dashboard refresh interval (seconds)
    "history_days": 30,                   # 历史数据天数 / History data days

    # 插件设置 / Plugin settings
    "enabled_handlers": [
        "content_gen",
        "data_label",
        "translation",
        "code_review",
    ],
}


# ============================================================
# 配置管理器 / Configuration Manager
# ============================================================


class ConfigManager:
    """
    配置管理器 / Configuration Manager

    负责加载、保存和管理应用配置。支持从文件加载和合并默认配置。
    Responsible for loading, saving, and managing application configuration.
    Supports loading from files and merging with default configuration.

    Attributes:
        config: 当前配置字典 / Current configuration dictionary
        config_path: 配置文件路径 / Configuration file path
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        初始化配置管理器 / Initialize configuration manager

        Args:
            config_path: 配置文件路径（可选）/ Configuration file path (optional)
        """
        self.config: Dict[str, Any] = {}
        self.config_path: Optional[str] = config_path
        self._load()

    def _load(self) -> None:
        """
        加载配置 / Load configuration

        按以下优先级合并配置：
        1. 默认配置 / Default configuration
        2. 配置文件配置 / Configuration file
        """
        # 从默认配置开始 / Start with default configuration
        self.config = DEFAULT_CONFIG.copy()

        # 尝试从文件加载 / Try to load from file
        if self.config_path and os.path.exists(self.config_path):
            file_config = self._load_file(self.config_path)
            self.config = self._merge(self.config, file_config)
        else:
            # 尝试默认路径 / Try default paths
            default_paths = [
                "earnflow_config.json",
                os.path.expanduser("~/.earnflow/config.json"),
            ]
            for path in default_paths:
                if os.path.exists(path):
                    file_config = self._load_file(path)
                    self.config = self._merge(self.config, file_config)
                    self.config_path = path
                    break

    @staticmethod
    def _load_file(path: str) -> Dict[str, Any]:
        """
        从JSON文件加载配置 / Load configuration from JSON file

        Args:
            path: 文件路径 / File path

        Returns:
            配置字典 / Configuration dictionary
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Config] Warning: Failed to load config from {path}: {e}")
            return {}

    @staticmethod
    def _merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        深度合并两个字典 / Deep merge two dictionaries

        Args:
            base: 基础字典 / Base dictionary
            override: 覆盖字典 / Override dictionary

        Returns:
            合并后的字典 / Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值 / Get configuration value

        Args:
            key: 配置键（支持点号分隔的嵌套键）/ Config key (supports dot-separated nested keys)
            default: 默认值 / Default value

        Returns:
            配置值 / Configuration value
        """
        keys = key.split(".")
        value: Any = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值 / Set configuration value

        Args:
            key: 配置键 / Config key
            value: 配置值 / Config value
        """
        self.config[key] = value

    def save(self, path: Optional[str] = None) -> None:
        """
        保存配置到文件 / Save configuration to file

        Args:
            path: 文件路径（默认使用当前路径）/ File path (defaults to current path)
        """
        save_path = path or self.config_path
        if not save_path:
            save_path = "earnflow_config.json"

        # 确保目录存在 / Ensure directory exists
        dir_path = os.path.dirname(save_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

        self.config_path = save_path

    def validate(self) -> Tuple[bool, List[str]]:
        """
        验证当前配置 / Validate current configuration

        Returns:
            元组：(是否有效, 错误消息列表) / Tuple: (is_valid, error_messages)
        """
        return validate_config(self.config)

    def reset(self) -> None:
        """重置为默认配置 / Reset to default configuration"""
        self.config = DEFAULT_CONFIG.copy()

    def to_dict(self) -> Dict[str, Any]:
        """
        获取配置字典副本 / Get a copy of the configuration dictionary

        Returns:
            配置字典 / Configuration dictionary
        """
        return self.config.copy()

    def ensure_dirs(self) -> None:
        """
        确保工作目录和输出目录存在 / Ensure work and output directories exist
        """
        work_dir = self.get("work_dir", "./earnflow_data")
        output_dir = self.get("output_dir", "./earnflow_reports")
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

    def __repr__(self) -> str:
        return f"ConfigManager(path={self.config_path!r})"
