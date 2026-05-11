#!/usr/bin/env python3
"""
EarnFlow 安装配置 / EarnFlow Setup Configuration
"""

import os
from setuptools import setup, find_packages

# 读取版本号 / Read version number
about: dict = {}
with open("earnflow/__init__.py", "r", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="earnflow",
    version=about.get("__version__", "1.0.0"),
    description=about.get(
        "__description__",
        "Lightweight AI Automated Task Earning Engine",
    ),
    long_description=open("README.md", "r", encoding="utf-8").read()
    if os.path.exists("README.md")
    else "",
    long_description_content_type="text/markdown",
    author=about.get("__author__", "EarnFlow Team"),
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    package_data={
        "earnflow": [],
    },
    include_package_data=True,
    install_requires=[],  # 零外部依赖 / Zero external dependencies
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "earnflow=earnflow.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    zip_safe=False,
)
