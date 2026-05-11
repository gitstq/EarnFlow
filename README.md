<div align="center">

# 🌊 EarnFlow

**轻量级 AI 自动化任务收益引擎**

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-success.svg)
![Tests](https://img.shields.io/badge/Tests-69%20Passed-brightgreen.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)

<p>
  <b>零依赖</b> · <b>纯标准库</b> · <b>TF-IDF 智能匹配</b> · <b>多格式报告</b> · <b>TUI 仪表盘</b>
</p>

</div>

---

## 简体中文

### 🎉 项目介绍

**EarnFlow** 是一款面向独立开发者与自动化爱好者的轻量级 AI 自动化任务收益引擎。它以命令行为核心交互方式，帮助用户高效管理、执行和追踪各类自动化任务的收益情况。

#### 🎯 项目定位

EarnFlow 定位为**个人自动化任务的"收益中枢"**——将分散在各个平台、各种脚本中的自动化任务统一纳管，提供从任务匹配、执行调度到收益追踪、报告生成的完整闭环。

#### 💎 核心价值

| 维度 | 说明 |
|:---:|:---|
| **零门槛** | 纯 Python 标准库实现，无需安装任何第三方依赖，`pip install` 即可使用 |
| **智能化** | 内置 TF-IDF 语义匹配引擎，自动将技能与任务精准配对 |
| **可视化** | TUI 仪表盘 + 多格式报告导出，收益数据一目了然 |
| **可扩展** | 插件化架构，6 个内置处理器 + 自定义插件，轻松扩展能力边界 |

#### 🔥 解决的用户痛点

- **任务分散**：自动化脚本散落各处，无法统一管理和追踪收益
- **匹配低效**：手动筛选适合自己技能的任务耗时耗力
- **收益模糊**：缺乏系统化的收益统计与趋势分析工具
- **依赖地狱**：现有工具动辄依赖数十个第三方包，部署困难
- **报告缺失**：难以生成专业格式的收益报告用于复盘和分享

#### ✨ 自研差异化亮点

- **完全零外部依赖**：整个项目仅使用 Python 3.8+ 标准库，包括 TF-IDF 计算、HTML 生成、CSV 处理等全部自研实现
- **自研 TF-IDF 匹配引擎**：不依赖 scikit-learn 或 NLTK，纯手工实现词频-逆文档频率算法，精准度媲美主流方案
- **ASCII 图表引擎**：在终端中渲染专业的收益趋势图，无需 matplotlib 等图形库
- **插件热加载**：支持运行时动态加载自定义插件，无需重启即可扩展功能

#### 🌟 灵感来源

EarnFlow 的灵感来源于独立开发者在接单平台、众包任务和自动化脚本变现过程中遇到的效率瓶颈。我们希望打造一个**极简但强大**的工具，让每一位开发者都能像管理投资组合一样管理自己的自动化任务收益。

---

### ✨ 核心特性

#### 🧠 智能任务匹配引擎

基于自研 **TF-IDF（词频-逆文档频率）** 算法，对任务描述与用户技能标签进行语义相似度评分，实现精准的任务-技能自动匹配。

```python
# 匹配引擎自动计算相似度分数
# score = Σ(tf_idf(term) × weight) / normalization
```

> 💡 **提示**：匹配引擎支持自定义权重配置，可根据实际需求调整技能关键词的匹配优先级。

#### 📊 全维度收益追踪

提供**日 / 周 / 月**三个时间维度的收益统计，内置趋势分析算法，自动识别收益波动规律。

| 统计维度 | 功能说明 |
|:---:|:---|
| **日报** | 每日收益明细、任务完成数、成功率 |
| **周报** | 周收益汇总、环比增长、最佳任务类型 |
| **月报** | 月度趋势图、收益预测、ROI 分析 |

#### 📝 多格式报告导出

支持 **JSON / CSV / Markdown / HTML** 四种报告格式，满足不同场景需求：

- **JSON**：程序化处理与 API 集成
- **CSV**：Excel 导入与数据分析
- **Markdown**：文档归档与版本管理
- **HTML**：浏览器查看与邮件分享

```bash
# 一键生成多种格式报告
earnflow report --format json    # JSON 格式
earnflow report --format csv     # CSV 格式
earnflow report --format md      # Markdown 格式
earnflow report --format html    # HTML 格式（带图表）
```

> 🔥 **重点**：HTML 报告内置 CSS 样式和交互式图表，可直接在浏览器中查看，无需额外依赖。

#### 🖥️ TUI 仪表盘

基于终端的实时仪表盘，使用 **ASCII 图表** 在命令行中渲染专业的收益趋势可视化界面。

```
┌─────────────────────────────────────────┐
│         EarnFlow 收益仪表盘              │
├─────────────────────────────────────────┤
│  今日收益: ¥128.50  │  本周: ¥856.30    │
│  任务完成: 12/15     │  成功率: 80.0%    │
├─────────────────────────────────────────┤
│  收益趋势 (近7天)                       │
│  ¥900 ┤     ╭──╮                       │
│  ¥700 ┤  ╭──╯  ╰──╮                    │
│  ¥500 ┤──╯        ╰──╮                 │
│  ¥300 ┤              ╰──               │
│       └──────────────────              │
│       Mon Tue Wed Thu Fri Sat Sun       │
└─────────────────────────────────────────┘
```

#### 🔌 插件系统

内置 **6 个任务处理器**，覆盖常见自动化场景，同时支持自定义插件扩展：

| 插件名称 | 功能描述 |
|:---:|:---|
| `ContentProcessor` | 内容生成与处理 |
| `DataProcessor` | 数据清洗与转换 |
| `TranslationProcessor` | 多语言翻译处理 |
| `CodeProcessor` | 代码生成与审查 |
| `AnalysisProcessor` | 数据分析与洞察 |
| `MediaProcessor` | 多媒体内容处理 |

#### 📋 8 个默认任务模板

开箱即用的预置任务模板，覆盖主流自动化变现场景：

1. **内容写作** - 文章撰写、SEO 优化内容
2. **数据标注** - 图像标注、文本分类
3. **代码审查** - 代码质量检测、安全审计
4. **翻译任务** - 多语言互译、本地化
5. **数据分析** - 报表生成、趋势预测
6. **API 测试** - 接口自动化测试
7. **监控告警** - 服务监控、异常检测
8. **批量处理** - 文件批处理、格式转换

> ⚠️ **注意**：任务模板可通过 `templates/default_tasks.json` 进行自定义修改，也可通过插件系统添加新模板。

#### 🧪 完善的测试体系

**69 个单元测试全部通过**，覆盖核心模块的所有关键路径：

```
tests/
├── test_engine.py    # 任务引擎测试
├── test_matcher.py   # 匹配引擎测试
├── test_reporter.py  # 报告生成测试
└── test_tracker.py   # 收益追踪测试
```

---

### 🚀 快速开始

#### 📋 环境要求

| 项目 | 要求 |
|:---:|:---|
| **Python** | 3.8 及以上版本 |
| **操作系统** | Windows / macOS / Linux |
| **外部依赖** | 无（纯标准库） |
| **磁盘空间** | < 5 MB |

> 💡 **提示**：无需安装 pip、virtualenv 等工具之外的任何东西。EarnFlow 的设计哲学就是"零摩擦"。

#### 🔧 安装方式

**方式一：从 GitHub 安装（推荐）**

```bash
pip install git+https://github.com/gitstq/EarnFlow.git
```

**方式二：克隆后本地安装**

```bash
# 克隆仓库
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow

# 安装
pip install .

# 或者使用传统方式
python setup.py install
```

**方式三：开发模式安装**

```bash
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow
pip install -e .
```

> ⚠️ **注意**：中国大陆用户如果遇到 GitHub 访问问题，可使用镜像源加速：
> ```bash
> pip install git+https://ghproxy.com/https://github.com/gitstq/EarnFlow.git
> ```

#### ⚡ 一键运行

安装完成后，即可通过 `earnflow` 命令使用：

```bash
# 运行 5 个演示任务，快速体验
earnflow run --demo --count 5

# 列出所有可用任务
earnflow list

# 查看收益统计
earnflow stats

# 生成 HTML 格式报告
earnflow report --format html

# 打开 TUI 仪表盘
earnflow dashboard

# 管理配置
earnflow config
```

---

### 📖 详细使用指南

#### 🎮 基础命令

**运行任务**

```bash
# 运行演示任务
earnflow run --demo --count 5

# 运行指定类型的任务
earnflow run --type content --count 10

# 运行所有匹配的任务
earnflow run --all

# 并发运行（指定 worker 数量）
earnflow run --demo --count 20 --workers 3
```

**查看任务列表**

```bash
# 列出所有可用任务
earnflow list

# 按类型筛选
earnflow list --type data

# 显示详细信息
earnflow list --verbose
```

#### 📊 收益统计

```bash
# 查看总体统计
earnflow stats

# 查看今日统计
earnflow stats --period daily

# 查看本周统计
earnflow stats --period weekly

# 查看本月统计
earnflow stats --period monthly

# 导出统计数据
earnflow stats --export csv
```

#### 📝 报告生成

```bash
# 生成 JSON 报告
earnflow report --format json --output report.json

# 生成 CSV 报告
earnflow report --format csv --output report.csv

# 生成 Markdown 报告
earnflow report --format md --output report.md

# 生成 HTML 报告（带图表）
earnflow report --format html --output report.html

# 指定时间范围
earnflow report --format html --from 2025-01-01 --to 2025-12-31
```

#### 🖥️ TUI 仪表盘

```bash
# 启动仪表盘
earnflow dashboard

# 指定刷新间隔（秒）
earnflow dashboard --interval 5

# 指定显示的时间范围
earnflow dashboard --days 30
```

#### ⚙️ 配置管理

```bash
# 查看当前配置
earnflow config

# 设置配置项
earnflow config set matcher.threshold 0.75
earnflow config set tracker.currency CNY

# 重置为默认配置
earnflow config reset
```

#### 📋 命令参数速查表

| 命令 | 参数 | 说明 |
|:---|:---|:---|
| `run` | `--demo` | 运行演示模式 |
| `run` | `--count N` | 执行 N 个任务 |
| `run` | `--type TYPE` | 指定任务类型 |
| `run` | `--workers N` | 并发 worker 数 |
| `list` | `--type TYPE` | 按类型筛选 |
| `list` | `--verbose` | 显示详细信息 |
| `stats` | `--period PERIOD` | 统计周期 |
| `stats` | `--export FMT` | 导出格式 |
| `report` | `--format FMT` | 报告格式 |
| `report` | `--output FILE` | 输出文件路径 |
| `report` | `--from DATE` | 起始日期 |
| `report` | `--to DATE` | 结束日期 |
| `dashboard` | `--interval N` | 刷新间隔 |
| `dashboard` | `--days N` | 显示天数 |
| `config` | `set KEY VAL` | 设置配置 |
| `config` | `reset` | 重置配置 |

#### 🎯 典型使用场景

**场景一：日常自动化任务管理**

```bash
# 每天早上运行一次，查看昨日收益
earnflow stats --period daily
earnflow dashboard --days 7
```

**场景二：周度收益复盘**

```bash
# 每周生成收益报告
earnflow report --format html --period weekly --output weekly_report.html
```

**场景三：批量任务执行**

```bash
# 一次性执行多个任务并生成报告
earnflow run --type content --count 50 --workers 5
earnflow report --format csv --output batch_results.csv
```

---

### 💡 设计思路与迭代规划

#### 🏗️ 设计理念

EarnFlow 遵循以下核心设计原则：

1. **零依赖哲学**：不引入任何第三方库，降低部署复杂度，提升可移植性
2. **约定优于配置**：合理的默认设置，开箱即用，减少配置负担
3. **渐进式复杂度**：简单场景一条命令搞定，复杂场景提供丰富的配置选项
4. **数据本地化**：所有数据存储在本地，保障用户隐私和数据安全

#### 🔧 技术选型原因

| 技术决策 | 原因 |
|:---|:---|
| **纯标准库** | 消除依赖冲突，简化部署流程，提升稳定性 |
| **TF-IDF 算法** | 轻量级语义匹配，无需训练模型，适合中小规模任务集 |
| **JSON 数据存储** | 人类可读、易于调试、跨平台兼容 |
| **CLI 交互模式** | 自动化友好、远程服务器可用、脚本集成方便 |
| **插件化架构** | 核心功能与扩展功能解耦，便于社区贡献 |

#### 🗺️ 后续迭代计划

- [ ] **v1.1** - Web 仪表盘界面（基于内置 HTTP 服务器）
- [ ] **v1.2** - 任务调度系统（Cron 表达式支持）
- [ ] **v1.3** - 多用户支持与数据隔离
- [ ] **v1.4** - 任务市场与模板共享
- [ ] **v2.0** - 分布式任务执行引擎
- [ ] **v2.1** - AI 驱动的智能任务推荐

---

### 📦 打包与部署指南

#### 🔨 打包流程

```bash
# 克隆项目
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow

# 使用 Makefile 打包
make build

# 或手动打包
python setup.py sdist bdist_wheel
```

#### 🚀 部署方法

**本地部署**

```bash
pip install .
```

**虚拟环境部署**

```bash
python -m venv earnflow_env
source earnflow_env/bin/activate  # Linux/macOS
# earnflow_env\Scripts\activate   # Windows
pip install .
```

**Docker 部署**

```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install .
CMD ["earnflow", "dashboard"]
```

```bash
docker build -t earnflow .
docker run -it earnflow
```

> ⚠️ **注意**：由于 EarnFlow 零外部依赖，Docker 镜像体积可控制在 100MB 以内。

---

### 🤝 贡献指南

我们欢迎并感谢每一位贡献者！在提交贡献前，请阅读以下指南。

#### 📝 PR 提交规范

1. **Fork** 本仓库并创建特性分支：`git checkout -b feature/your-feature`
2. **编写代码** 并确保通过所有测试：`make test`
3. **提交信息** 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：
   ```
   feat: 添加新的任务处理器插件
   fix: 修复收益统计计算精度问题
   docs: 更新 API 使用文档
   test: 增加匹配引擎边界测试
   refactor: 优化 TF-IDF 计算性能
   ```
4. **推送** 到远程分支：`git push origin feature/your-feature`
5. 创建 **Pull Request** 并填写变更说明

#### 🐛 Issue 反馈规则

提交 Issue 时，请包含以下信息：

- **环境信息**：操作系统、Python 版本
- **复现步骤**：最小可复现示例
- **期望行为**：描述你期望的结果
- **实际行为**：描述实际发生的情况
- **日志输出**：相关的错误日志或截图

#### 🧪 本地测试

```bash
# 运行全部测试
make test

# 或使用 pytest
python -m pytest tests/ -v

# 运行特定模块测试
python -m pytest tests/test_engine.py -v

# 查看测试覆盖率
python -m pytest tests/ --cov=earnflow
```

---

### 📄 开源协议

本项目基于 **[MIT License](https://opensource.org/licenses/MIT)** 开源。

```
MIT License

Copyright (c) 2025 EarnFlow Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

> 💡 **提示**：EarnFlow 是自由软件，你可以自由使用、修改和分发。如果你觉得这个项目有价值，欢迎给它一个 ⭐ Star！

---

## 繁體中文

### 🎉 專案介紹

**EarnFlow** 是一款面向獨立開發者與自動化愛好者的輕量級 AI 自動化任務收益引擎。它以命令行為核心互動方式，幫助用戶高效管理、執行和追蹤各類自動化任務的收益情況。

#### 🎯 專案定位

EarnFlow 定位為**個人自動化任務的「收益中樞」**——將分散在各個平台、各種腳本中的自動化任務統一納管，提供從任務匹配、執行調度到收益追蹤、報告生成的完整閉環。

#### 💎 核心價值

| 維度 | 說明 |
|:---:|:---|
| **零門檻** | 純 Python 標準庫實現，無需安裝任何第三方依賴，`pip install` 即可使用 |
| **智慧化** | 內建 TF-IDF 語義匹配引擎，自動將技能與任務精準配對 |
| **視覺化** | TUI 儀表盤 + 多格式報告匯出，收益數據一目了然 |
| **可擴展** | 插件化架構，6 個內建處理器 + 自訂插件，輕鬆擴展能力邊界 |

#### 🔥 解決的用戶痛點

- **任務分散**：自動化腳本散落各處，無法統一管理和追蹤收益
- **匹配低效**：手動篩選適合自己技能的任務耗時耗力
- **收益模糊**：缺乏系統化的收益統計與趨勢分析工具
- **依賴地獄**：現有工具動輒依賴數十個第三方套件，部署困難
- **報告缺失**：難以生成專業格式的收益報告用於復盤和分享

#### ✨ 自研差異化亮點

- **完全零外部依賴**：整個專案僅使用 Python 3.8+ 標準庫，包括 TF-IDF 計算、HTML 生成、CSV 處理等全部自研實現
- **自研 TF-IDF 匹配引擎**：不依賴 scikit-learn 或 NLTK，純手工實現詞頻-逆文檔頻率算法，精準度媲美主流方案
- **ASCII 圖表引擎**：在終端中渲染專業的收益趨勢圖，無需 matplotlib 等圖形庫
- **插件熱載入**：支援運行時動態載入自訂插件，無需重啟即可擴展功能

#### 🌟 靈感來源

EarnFlow 的靈感來源於獨立開發者在接單平台、眾包任務和自動化腳本變現過程中遇到的效率瓶頸。我們希望打造一個**極簡但強大**的工具，讓每一位開發者都能像管理投資組合一樣管理自己的自動化任務收益。

---

### ✨ 核心特性

#### 🧠 智慧任務匹配引擎

基於自研 **TF-IDF（詞頻-逆文檔頻率）** 算法，對任務描述與用戶技能標籤進行語義相似度評分，實現精準的任務-技能自動匹配。

```python
# 匹配引擎自動計算相似度分數
# score = Σ(tf_idf(term) × weight) / normalization
```

> 💡 **提示**：匹配引擎支援自訂權重配置，可根據實際需求調整技能關鍵詞的匹配優先級。

#### 📊 全維度收益追蹤

提供**日 / 週 / 月**三個時間維度的收益統計，內建趨勢分析算法，自動識別收益波動規律。

| 統計維度 | 功能說明 |
|:---:|:---|
| **日報** | 每日收益明細、任務完成數、成功率 |
| **週報** | 週收益彙總、環比增長、最佳任務類型 |
| **月報** | 月度趨勢圖、收益預測、ROI 分析 |

#### 📝 多格式報告匯出

支援 **JSON / CSV / Markdown / HTML** 四種報告格式，滿足不同場景需求：

- **JSON**：程式化處理與 API 整合
- **CSV**：Excel 匯入與數據分析
- **Markdown**：文件歸檔與版本管理
- **HTML**：瀏覽器查看與郵件分享

```bash
# 一鍵生成多種格式報告
earnflow report --format json    # JSON 格式
earnflow report --format csv     # CSV 格式
earnflow report --format md      # Markdown 格式
earnflow report --format html    # HTML 格式（帶圖表）
```

> 🔥 **重點**：HTML 報告內建 CSS 樣式和互動式圖表，可直接在瀏覽器中查看，無需額外依賴。

#### 🖥️ TUI 儀表盤

基於終端的即時儀表盤，使用 **ASCII 圖表** 在命令行中渲染專業的收益趨勢視覺化介面。

```
┌─────────────────────────────────────────┐
│         EarnFlow 收益儀表盤              │
├─────────────────────────────────────────┤
│  今日收益: ¥128.50  │  本週: ¥856.30    │
│  任務完成: 12/15     │  成功率: 80.0%    │
├─────────────────────────────────────────┤
│  收益趨勢 (近7天)                       │
│  ¥900 ┤     ╭──╮                       │
│  ¥700 ┤  ╭──╯  ╰──╮                    │
│  ¥500 ┤──╯        ╰──╮                 │
│  ¥300 ┤              ╰──               │
│       └──────────────────              │
│       Mon Tue Wed Thu Fri Sat Sun       │
└─────────────────────────────────────────┘
```

#### 🔌 插件系統

內建 **6 個任務處理器**，覆蓋常見自動化場景，同時支援自訂插件擴展：

| 插件名稱 | 功能描述 |
|:---:|:---|
| `ContentProcessor` | 內容生成與處理 |
| `DataProcessor` | 數據清洗與轉換 |
| `TranslationProcessor` | 多語言翻譯處理 |
| `CodeProcessor` | 程式碼生成與審查 |
| `AnalysisProcessor` | 數據分析與洞察 |
| `MediaProcessor` | 多媒體內容處理 |

#### 📋 8 個預設任務模板

開箱即用的預置任務模板，覆蓋主流自動化變現場景：

1. **內容寫作** - 文章撰寫、SEO 最佳化內容
2. **數據標註** - 影像標註、文本分類
3. **程式碼審查** - 程式碼品質檢測、安全審計
4. **翻譯任務** - 多語言互譯、在地化
5. **數據分析** - 報表生成、趨勢預測
6. **API 測試** - 介面自動化測試
7. **監控告警** - 服務監控、異常檢測
8. **批次處理** - 檔案批次處理、格式轉換

> ⚠️ **注意**：任務模板可透過 `templates/default_tasks.json` 進行自訂修改，也可透過插件系統新增模板。

#### 🧪 完善的測試體系

**69 個單元測試全部通過**，覆蓋核心模組的所有關鍵路徑：

```
tests/
├── test_engine.py    # 任務引擎測試
├── test_matcher.py   # 匹配引擎測試
├── test_reporter.py  # 報告生成測試
└── test_tracker.py   # 收益追蹤測試
```

---

### 🚀 快速開始

#### 📋 環境要求

| 項目 | 要求 |
|:---:|:---|
| **Python** | 3.8 及以上版本 |
| **作業系統** | Windows / macOS / Linux |
| **外部依賴** | 無（純標準庫） |
| **磁碟空間** | < 5 MB |

> 💡 **提示**：無需安裝 pip、virtualenv 等工具之外的任何東西。EarnFlow 的設計哲學就是「零摩擦」。

#### 🔧 安裝方式

**方式一：從 GitHub 安裝（推薦）**

```bash
pip install git+https://github.com/gitstq/EarnFlow.git
```

**方式二：複製後本地安裝**

```bash
# 複製倉庫
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow

# 安裝
pip install .

# 或者使用傳統方式
python setup.py install
```

**方式三：開發模式安裝**

```bash
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow
pip install -e .
```

> ⚠️ **注意**：中國大陸用戶如果遇到 GitHub 存取問題，可使用鏡像源加速：
> ```bash
> pip install git+https://ghproxy.com/https://github.com/gitstq/EarnFlow.git
> ```

#### ⚡ 一鍵運行

安裝完成後，即可透過 `earnflow` 命令使用：

```bash
# 運行 5 個演示任務，快速體驗
earnflow run --demo --count 5

# 列出所有可用任務
earnflow list

# 查看收益統計
earnflow stats

# 生成 HTML 格式報告
earnflow report --format html

# 打開 TUI 儀表盤
earnflow dashboard

# 管理配置
earnflow config
```

---

### 📖 詳細使用指南

#### 🎮 基礎命令

**運行任務**

```bash
# 運行演示任務
earnflow run --demo --count 5

# 運行指定類型的任務
earnflow run --type content --count 10

# 運行所有匹配的任務
earnflow run --all

# 並發運行（指定 worker 數量）
earnflow run --demo --count 20 --workers 3
```

**查看任務列表**

```bash
# 列出所有可用任務
earnflow list

# 按類型篩選
earnflow list --type data

# 顯示詳細資訊
earnflow list --verbose
```

#### 📊 收益統計

```bash
# 查看總體統計
earnflow stats

# 查看今日統計
earnflow stats --period daily

# 查看本週統計
earnflow stats --period weekly

# 查看本月統計
earnflow stats --period monthly

# 匯出統計數據
earnflow stats --export csv
```

#### 📝 報告生成

```bash
# 生成 JSON 報告
earnflow report --format json --output report.json

# 生成 CSV 報告
earnflow report --format csv --output report.csv

# 生成 Markdown 報告
earnflow report --format md --output report.md

# 生成 HTML 報告（帶圖表）
earnflow report --format html --output report.html

# 指定時間範圍
earnflow report --format html --from 2025-01-01 --to 2025-12-31
```

#### 🖥️ TUI 儀表盤

```bash
# 啟動儀表盤
earnflow dashboard

# 指定刷新間隔（秒）
earnflow dashboard --interval 5

# 指定顯示的時間範圍
earnflow dashboard --days 30
```

#### ⚙️ 配置管理

```bash
# 查看當前配置
earnflow config

# 設定配置項
earnflow config set matcher.threshold 0.75
earnflow config set tracker.currency CNY

# 重置為預設配置
earnflow config reset
```

#### 📋 命令參數速查表

| 命令 | 參數 | 說明 |
|:---|:---|:---|
| `run` | `--demo` | 運行演示模式 |
| `run` | `--count N` | 執行 N 個任務 |
| `run` | `--type TYPE` | 指定任務類型 |
| `run` | `--workers N` | 並發 worker 數 |
| `list` | `--type TYPE` | 按類型篩選 |
| `list` | `--verbose` | 顯示詳細資訊 |
| `stats` | `--period PERIOD` | 統計週期 |
| `stats` | `--export FMT` | 匯出格式 |
| `report` | `--format FMT` | 報告格式 |
| `report` | `--output FILE` | 輸出檔案路徑 |
| `report` | `--from DATE` | 起始日期 |
| `report` | `--to DATE` | 結束日期 |
| `dashboard` | `--interval N` | 刷新間隔 |
| `dashboard` | `--days N` | 顯示天數 |
| `config` | `set KEY VAL` | 設定配置 |
| `config` | `reset` | 重置配置 |

#### 🎯 典型使用場景

**場景一：日常自動化任務管理**

```bash
# 每天早上運行一次，查看昨日收益
earnflow stats --period daily
earnflow dashboard --days 7
```

**場景二：週度收益復盤**

```bash
# 每週生成收益報告
earnflow report --format html --period weekly --output weekly_report.html
```

**場景三：批次任務執行**

```bash
# 一次性執行多個任務並生成報告
earnflow run --type content --count 50 --workers 5
earnflow report --format csv --output batch_results.csv
```

---

### 💡 設計思路與迭代規劃

#### 🏗️ 設計理念

EarnFlow 遵循以下核心設計原則：

1. **零依賴哲學**：不引入任何第三方庫，降低部署複雜度，提升可移植性
2. **約定優於配置**：合理的預設設定，開箱即用，減少配置負擔
3. **漸進式複雜度**：簡單場景一條命令搞定，複雜場景提供豐富的配置選項
4. **數據本地化**：所有數據儲存在本地，保障用戶隱私和數據安全

#### 🔧 技術選型原因

| 技術決策 | 原因 |
|:---|:---|
| **純標準庫** | 消除依賴衝突，簡化部署流程，提升穩定性 |
| **TF-IDF 算法** | 輕量級語義匹配，無需訓練模型，適合中小規模任務集 |
| **JSON 數據儲存** | 人類可讀、易於除錯、跨平台相容 |
| **CLI 互動模式** | 自動化友善、遠端伺服器可用、腳本整合方便 |
| **插件化架構** | 核心功能與擴展功能解耦，便於社群貢獻 |

#### 🗺️ 後續迭代計畫

- [ ] **v1.1** - Web 儀表盤介面（基於內建 HTTP 伺服器）
- [ ] **v1.2** - 任務排程系統（Cron 運算式支援）
- [ ] **v1.3** - 多用戶支援與數據隔離
- [ ] **v1.4** - 任務市場與模板共享
- [ ] **v2.0** - 分散式任務執行引擎
- [ ] **v2.1** - AI 驅動的智慧任務推薦

---

### 📦 打包與部署指南

#### 🔨 打包流程

```bash
# 複製專案
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow

# 使用 Makefile 打包
make build

# 或手動打包
python setup.py sdist bdist_wheel
```

#### 🚀 部署方法

**本地部署**

```bash
pip install .
```

**虛擬環境部署**

```bash
python -m venv earnflow_env
source earnflow_env/bin/activate  # Linux/macOS
# earnflow_env\Scripts\activate   # Windows
pip install .
```

**Docker 部署**

```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install .
CMD ["earnflow", "dashboard"]
```

```bash
docker build -t earnflow .
docker run -it earnflow
```

> ⚠️ **注意**：由於 EarnFlow 零外部依賴，Docker 映像檔體積可控制在 100MB 以內。

---

### 🤝 貢獻指南

我們歡迎並感謝每一位貢獻者！在提交貢獻前，請閱讀以下指南。

#### 📝 PR 提交規範

1. **Fork** 本倉庫並建立特性分支：`git checkout -b feature/your-feature`
2. **編寫程式碼** 並確保通過所有測試：`make test`
3. **提交資訊** 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：
   ```
   feat: 新增新的任務處理器插件
   fix: 修復收益統計計算精度問題
   docs: 更新 API 使用文件
   test: 增加匹配引擎邊界測試
   refactor: 最佳化 TF-IDF 計算效能
   ```
4. **推送** 到遠端分支：`git push origin feature/your-feature`
5. 建立 **Pull Request** 並填寫變更說明

#### 🐛 Issue 回饋規則

提交 Issue 時，請包含以下資訊：

- **環境資訊**：作業系統、Python 版本
- **重現步驟**：最小可重現示例
- **期望行為**：描述你期望的結果
- **實際行為**：描述實際發生的情況
- **日誌輸出**：相關的錯誤日誌或截圖

#### 🧪 本地測試

```bash
# 運行全部測試
make test

# 或使用 pytest
python -m pytest tests/ -v

# 運行特定模組測試
python -m pytest tests/test_engine.py -v

# 查看測試覆蓋率
python -m pytest tests/ --cov=earnflow
```

---

### 📄 開源協議

本專案基於 **[MIT License](https://opensource.org/licenses/MIT)** 開源。

```
MIT License

Copyright (c) 2025 EarnFlow Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

> 💡 **提示**：EarnFlow 是自由軟體，你可以自由使用、修改和分發。如果你覺得這個專案有價值，歡迎給它一個 ⭐ Star！

---

## English

### 🎉 Introduction

**EarnFlow** is a lightweight AI-powered automated task revenue engine designed for indie developers and automation enthusiasts. It uses the command line as its primary interaction method, helping users efficiently manage, execute, and track revenue from various automated tasks.

#### 🎯 Project Positioning

EarnFlow is positioned as the **"Revenue Hub" for personal automated tasks** -- unifying scattered automation scripts across platforms into a single management system, providing a complete closed loop from task matching and execution scheduling to revenue tracking and report generation.

#### 💎 Core Value

| Dimension | Description |
|:---:|:---|
| **Zero Barrier** | Pure Python standard library, no third-party dependencies, `pip install` and go |
| **Intelligent** | Built-in TF-IDF semantic matching engine for automatic skill-task pairing |
| **Visual** | TUI dashboard + multi-format report export, revenue data at a glance |
| **Extensible** | Plugin architecture with 6 built-in processors + custom plugin support |

#### 🔥 Pain Points Solved

- **Scattered Tasks**: Automation scripts spread everywhere with no unified management or revenue tracking
- **Inefficient Matching**: Manually filtering tasks suited to your skills is time-consuming
- **Revenue Blindness**: Lack of systematic revenue statistics and trend analysis tools
- **Dependency Hell**: Existing tools often depend on dozens of third-party packages, making deployment difficult
- **Missing Reports**: Hard to generate professional revenue reports for review and sharing

#### ✨ Differentiating Highlights

- **Truly Zero External Dependencies**: The entire project uses only Python 3.8+ standard library -- TF-IDF computation, HTML generation, CSV processing, all self-implemented
- **Custom TF-IDF Matching Engine**: No dependency on scikit-learn or NLTK; hand-crafted Term Frequency-Inverse Document Frequency algorithm with accuracy comparable to mainstream solutions
- **ASCII Chart Engine**: Renders professional revenue trend charts in the terminal without matplotlib or any graphics library
- **Hot-Loading Plugins**: Supports runtime dynamic loading of custom plugins, extending functionality without restart

#### 🌟 Inspiration

EarnFlow was inspired by the efficiency bottlenecks indie developers face when monetizing through freelance platforms, crowdsourcing tasks, and automation scripts. We aim to build a **minimalist yet powerful** tool that lets every developer manage their automated task revenue like an investment portfolio.

---

### ✨ Core Features

#### 🧠 Intelligent Task Matching Engine

Based on a custom **TF-IDF (Term Frequency-Inverse Document Frequency)** algorithm, it computes semantic similarity scores between task descriptions and user skill tags for precise automatic task-skill matching.

```python
# The matching engine automatically calculates similarity scores
# score = Σ(tf_idf(term) × weight) / normalization
```

> 💡 **Tip**: The matching engine supports custom weight configuration, allowing you to adjust the matching priority of skill keywords based on your needs.

#### 📊 Comprehensive Revenue Tracking

Provides revenue statistics across **daily / weekly / monthly** time dimensions, with built-in trend analysis algorithms that automatically identify revenue fluctuation patterns.

| Dimension | Description |
|:---:|:---|
| **Daily** | Daily revenue breakdown, tasks completed, success rate |
| **Weekly** | Weekly revenue summary, week-over-week growth, best task type |
| **Monthly** | Monthly trend charts, revenue forecasting, ROI analysis |

#### 📝 Multi-Format Report Export

Supports **JSON / CSV / Markdown / HTML** report formats for different scenarios:

- **JSON**: Programmatic processing and API integration
- **CSV**: Excel import and data analysis
- **Markdown**: Documentation archiving and version control
- **HTML**: Browser viewing and email sharing

```bash
# Generate reports in multiple formats with one command
earnflow report --format json    # JSON format
earnflow report --format csv     # CSV format
earnflow report --format md      # Markdown format
earnflow report --format html    # HTML format (with charts)
```

> 🔥 **Highlight**: HTML reports include built-in CSS styling and interactive charts, viewable directly in the browser with no additional dependencies.

#### 🖥️ TUI Dashboard

A terminal-based real-time dashboard that uses **ASCII charts** to render professional revenue trend visualizations right in your command line.

```
┌─────────────────────────────────────────┐
│         EarnFlow Revenue Dashboard       │
├─────────────────────────────────────────┤
│  Today:    $18.50   │  This Week: $123.30│
│  Completed: 12/15   │  Success:   80.0%  │
├─────────────────────────────────────────┤
│  Revenue Trend (Last 7 Days)            │
│  $180 ┤     ╭──╮                        │
│  $140 ┤  ╭──╯  ╰──╮                     │
│  $100 ┤──╯        ╰──╮                  │
│   $60 ┤              ╰──                │
│       └──────────────────                │
│       Mon Tue Wed Thu Fri Sat Sun        │
└─────────────────────────────────────────┘
```

#### 🔌 Plugin System

Built-in **6 task processors** covering common automation scenarios, with support for custom plugin extensions:

| Plugin | Description |
|:---:|:---|
| `ContentProcessor` | Content generation and processing |
| `DataProcessor` | Data cleaning and transformation |
| `TranslationProcessor` | Multi-language translation |
| `CodeProcessor` | Code generation and review |
| `AnalysisProcessor` | Data analysis and insights |
| `MediaProcessor` | Multimedia content processing |

#### 📋 8 Default Task Templates

Ready-to-use preset task templates covering mainstream automation monetization scenarios:

1. **Content Writing** - Article creation, SEO-optimized content
2. **Data Annotation** - Image labeling, text classification
3. **Code Review** - Code quality detection, security auditing
4. **Translation** - Multi-language translation, localization
5. **Data Analysis** - Report generation, trend prediction
6. **API Testing** - Interface automated testing
7. **Monitoring & Alerts** - Service monitoring, anomaly detection
8. **Batch Processing** - File batch processing, format conversion

> ⚠️ **Note**: Task templates can be customized via `templates/default_tasks.json`, and new templates can be added through the plugin system.

#### 🧪 Comprehensive Test Suite

**69 unit tests, all passing**, covering all critical paths of core modules:

```
tests/
├── test_engine.py    # Task engine tests
├── test_matcher.py   # Matching engine tests
├── test_reporter.py  # Report generation tests
└── test_tracker.py   # Revenue tracking tests
```

---

### 🚀 Quick Start

#### 📋 Requirements

| Item | Requirement |
|:---:|:---|
| **Python** | 3.8 or higher |
| **OS** | Windows / macOS / Linux |
| **External Dependencies** | None (pure standard library) |
| **Disk Space** | < 5 MB |

> 💡 **Tip**: Nothing beyond pip or virtualenv is needed. EarnFlow's design philosophy is "zero friction."

#### 🔧 Installation

**Option 1: Install from GitHub (Recommended)**

```bash
pip install git+https://github.com/gitstq/EarnFlow.git
```

**Option 2: Clone and Install Locally**

```bash
# Clone the repository
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow

# Install
pip install .

# Or use the traditional method
python setup.py install
```

**Option 3: Development Mode**

```bash
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow
pip install -e .
```

> ⚠️ **Note**: If you encounter GitHub access issues in certain regions, you can use a mirror proxy:
> ```bash
> pip install git+https://ghproxy.com/https://github.com/gitstq/EarnFlow.git
> ```

#### ⚡ Quick Run

Once installed, use the `earnflow` command:

```bash
# Run 5 demo tasks for a quick experience
earnflow run --demo --count 5

# List all available tasks
earnflow list

# View revenue statistics
earnflow stats

# Generate an HTML report
earnflow report --format html

# Open the TUI dashboard
earnflow dashboard

# Manage configuration
earnflow config
```

---

### 📖 Detailed Usage Guide

#### 🎮 Basic Commands

**Running Tasks**

```bash
# Run demo tasks
earnflow run --demo --count 5

# Run tasks of a specific type
earnflow run --type content --count 10

# Run all matching tasks
earnflow run --all

# Run concurrently (specify worker count)
earnflow run --demo --count 20 --workers 3
```

**Listing Tasks**

```bash
# List all available tasks
earnflow list

# Filter by type
earnflow list --type data

# Show detailed information
earnflow list --verbose
```

#### 📊 Revenue Statistics

```bash
# View overall statistics
earnflow stats

# View daily statistics
earnflow stats --period daily

# View weekly statistics
earnflow stats --period weekly

# View monthly statistics
earnflow stats --period monthly

# Export statistics
earnflow stats --export csv
```

#### 📝 Report Generation

```bash
# Generate JSON report
earnflow report --format json --output report.json

# Generate CSV report
earnflow report --format csv --output report.csv

# Generate Markdown report
earnflow report --format md --output report.md

# Generate HTML report (with charts)
earnflow report --format html --output report.html

# Specify date range
earnflow report --format html --from 2025-01-01 --to 2025-12-31
```

#### 🖥️ TUI Dashboard

```bash
# Launch the dashboard
earnflow dashboard

# Set refresh interval (seconds)
earnflow dashboard --interval 5

# Set display time range
earnflow dashboard --days 30
```

#### ⚙️ Configuration Management

```bash
# View current configuration
earnflow config

# Set configuration values
earnflow config set matcher.threshold 0.75
earnflow config set tracker.currency USD

# Reset to default configuration
earnflow config reset
```

#### 📋 Command Reference Table

| Command | Argument | Description |
|:---|:---|:---|
| `run` | `--demo` | Run in demo mode |
| `run` | `--count N` | Execute N tasks |
| `run` | `--type TYPE` | Specify task type |
| `run` | `--workers N` | Number of concurrent workers |
| `list` | `--type TYPE` | Filter by type |
| `list` | `--verbose` | Show detailed info |
| `stats` | `--period PERIOD` | Statistics period |
| `stats` | `--export FMT` | Export format |
| `report` | `--format FMT` | Report format |
| `report` | `--output FILE` | Output file path |
| `report` | `--from DATE` | Start date |
| `report` | `--to DATE` | End date |
| `dashboard` | `--interval N` | Refresh interval |
| `dashboard` | `--days N` | Number of days to display |
| `config` | `set KEY VAL` | Set configuration |
| `config` | `reset` | Reset configuration |

#### 🎯 Typical Use Cases

**Use Case 1: Daily Automation Management**

```bash
# Run once every morning to check yesterday's revenue
earnflow stats --period daily
earnflow dashboard --days 7
```

**Use Case 2: Weekly Revenue Review**

```bash
# Generate a weekly revenue report
earnflow report --format html --period weekly --output weekly_report.html
```

**Use Case 3: Batch Task Execution**

```bash
# Execute multiple tasks at once and generate a report
earnflow run --type content --count 50 --workers 5
earnflow report --format csv --output batch_results.csv
```

---

### 💡 Design Philosophy & Roadmap

#### 🏗️ Design Principles

EarnFlow follows these core design principles:

1. **Zero Dependency Philosophy**: No third-party libraries, reducing deployment complexity and improving portability
2. **Convention Over Configuration**: Sensible defaults, ready to use out of the box, minimizing configuration burden
3. **Progressive Complexity**: Simple scenarios solved with a single command; complex scenarios offer rich configuration options
4. **Local-First Data**: All data stored locally, ensuring user privacy and data security

#### 🔧 Technical Decisions

| Decision | Rationale |
|:---|:---|
| **Pure Standard Library** | Eliminates dependency conflicts, simplifies deployment, improves stability |
| **TF-IDF Algorithm** | Lightweight semantic matching, no model training needed, suitable for small-to-medium task sets |
| **JSON Data Storage** | Human-readable, easy to debug, cross-platform compatible |
| **CLI Interaction** | Automation-friendly, works on remote servers, easy script integration |
| **Plugin Architecture** | Decouples core from extension features, facilitates community contributions |

#### 🗺️ Roadmap

- [ ] **v1.1** - Web dashboard (built-in HTTP server)
- [ ] **v1.2** - Task scheduling system (Cron expression support)
- [ ] **v1.3** - Multi-user support with data isolation
- [ ] **v1.4** - Task marketplace and template sharing
- [ ] **v2.0** - Distributed task execution engine
- [ ] **v2.1** - AI-driven intelligent task recommendations

---

### 📦 Packaging & Deployment Guide

#### 🔨 Packaging

```bash
# Clone the project
git clone https://github.com/gitstq/EarnFlow.git
cd EarnFlow

# Build using Makefile
make build

# Or build manually
python setup.py sdist bdist_wheel
```

#### 🚀 Deployment

**Local Deployment**

```bash
pip install .
```

**Virtual Environment Deployment**

```bash
python -m venv earnflow_env
source earnflow_env/bin/activate  # Linux/macOS
# earnflow_env\Scripts\activate   # Windows
pip install .
```

**Docker Deployment**

```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install .
CMD ["earnflow", "dashboard"]
```

```bash
docker build -t earnflow .
docker run -it earnflow
```

> ⚠️ **Note**: Thanks to zero external dependencies, the Docker image size can be kept under 100MB.

---

### 🤝 Contributing Guide

We welcome and appreciate every contributor! Please read the following guidelines before submitting.

#### 📝 PR Submission Guidelines

1. **Fork** this repository and create a feature branch: `git checkout -b feature/your-feature`
2. **Write code** and ensure all tests pass: `make test`
3. **Commit messages** should follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
   ```
   feat: add new task processor plugin
   fix: resolve revenue statistics calculation precision issue
   docs: update API usage documentation
   test: add boundary tests for matching engine
   refactor: optimize TF-IDF computation performance
   ```
4. **Push** to the remote branch: `git push origin feature/your-feature`
5. Create a **Pull Request** with a description of the changes

#### 🐛 Issue Reporting Guidelines

When submitting an issue, please include the following information:

- **Environment**: Operating system, Python version
- **Reproduction Steps**: Minimal reproducible example
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Logs**: Relevant error logs or screenshots

#### 🧪 Local Testing

```bash
# Run all tests
make test

# Or use pytest
python -m pytest tests/ -v

# Run tests for a specific module
python -m pytest tests/test_engine.py -v

# Check test coverage
python -m pytest tests/ --cov=earnflow
```

---

### 📄 License

This project is licensed under the **[MIT License](https://opensource.org/licenses/MIT)**.

```
MIT License

Copyright (c) 2025 EarnFlow Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

> 💡 **Tip**: EarnFlow is free software. You are free to use, modify, and distribute it. If you find this project valuable, please give it a ⭐ Star!

---

<div align="center">

**Made with ❤️ by the EarnFlow Contributors**

</div>
