# 🔍 CodeReview-AI

<div align="center">

**轻量级AI驱动代码审查与质量分析引擎**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="简体中文"></a>
## 🎉 项目介绍

**CodeReview-AI** 是一款轻量级、零依赖的AI驱动代码审查工具，专为追求代码质量的开发者打造。它结合了传统静态代码分析与先进的AI智能审查，帮助您在编码过程中及时发现潜在问题，提升代码质量。

### 💡 灵感来源

在日常开发中，我们发现：
- 现有代码审查工具配置复杂，上手门槛高
- AI代码审查工具大多依赖云服务，存在代码隐私风险
- 缺乏轻量级、开箱即用的本地代码审查方案
- 代码质量报告不够直观，难以快速定位问题

**CodeReview-AI** 正是为解决这些痛点而生！

### ✨ 核心特性

- 🚀 **零依赖设计** - 纯Python标准库实现，无需安装额外依赖
- 🔒 **本地优先** - 支持Ollama本地LLM，代码隐私零风险
- 🎯 **多维度分析** - 静态分析 + AI智能审查，双重保障
- 🎨 **美观TUI** - 终端交互界面，支持彩色输出
- 📊 **多格式报告** - 支持Markdown、JSON、HTML、SARIF
- 🔗 **Git集成** - 自动检测变更文件，支持pre-commit钩子

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Linux / macOS / Windows

### 安装

```bash
# 方式1: 直接克隆使用
git clone https://github.com/gitstq/CodeReview-AI.git
cd CodeReview-AI
python3 -m codereview_ai --help

# 方式2: 安装到系统
pip install -e .

# 方式3: 直接使用
python3 -m pip install pyyaml  # 可选，用于YAML配置
codereview-ai --help
```

### 基础用法

```bash
# 审查当前目录所有Python文件
codereview-ai

# 审查指定目录
codereview-ai src/

# 审查指定文件
codereview-ai main.py utils.py

# 生成Markdown报告
codereview-ai --format markdown -o report.md

# 生成HTML报告
codereview-ai --format html -o report.html
```

---

## 📖 详细使用指南

### Git集成

```bash
# 只审查Git变更的文件
codereview-ai --git

# 只审查暂存区的文件
codereview-ai --git --staged

# 审查最近3个commit的变更
codereview-ai --git --commit-range HEAD~3..HEAD
```

### AI审查

```bash
# 启用AI审查（需要配置API密钥）
codereview-ai --ai

# 使用OpenAI
codereview-ai --ai --backend openai --model gpt-4o-mini

# 使用Anthropic Claude
codereview-ai --ai --backend anthropic --model claude-3-haiku

# 使用Ollama本地模型
codereview-ai --ai --backend ollama --model codellama
```

### 配置

```bash
# 初始化配置文件
codereview-ai --init

# 使用指定配置文件
codereview-ai --config .codereview-ai.yml
```

配置文件示例 (`.codereview-ai.yml`):

```yaml
analyzers:
  complexity:
    enabled: true
    max_cyclomatic_complexity: 10
    max_function_lines: 50
  
  style:
    enabled: true
    max_line_length: 100
  
  security:
    enabled: true
  
  duplicate:
    enabled: true

ai:
  enabled: false
  backend: openai
  model: gpt-4o-mini
  # api_key: your-api-key-here

report:
  format: console
  color: true
  show_code: true

exclude:
  - "**/venv/**"
  - "**/__pycache__/**"
  - "**/tests/**"
```

---

## 💡 设计思路与迭代规划

### 技术选型

- **纯Python标准库** - 零依赖，安装即用
- **AST解析** - 精准分析Python代码结构
- **模块化设计** - 分析器、AI后端、报告器均可扩展
- **ANSI颜色** - 终端美化，无需第三方库

### 后续迭代计划

- [ ] 支持更多编程语言（JavaScript、TypeScript、Go）
- [ ] 自定义规则引擎
- [ ] IDE插件（VS Code、PyCharm）
- [ ] CI/CD集成模板
- [ ] 团队协作功能

---

## 📦 打包与部署

### 本地安装

```bash
pip install -e .
```

### 创建独立可执行文件

```bash
# 使用PyInstaller
pip install pyinstaller
pyinstaller --onefile codereview_ai/__main__.py --name codereview-ai
```

---

## 🤝 贡献指南

欢迎提交Issue和PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

<a name="english"></a>
## 🎉 Introduction

**CodeReview-AI** is a lightweight, zero-dependency AI-powered code review tool designed for developers who care about code quality. It combines traditional static code analysis with advanced AI intelligent review to help you identify potential issues during coding and improve code quality.

### 💡 Motivation

In daily development, we found that:
- Existing code review tools are complex to configure and have a high learning curve
- AI code review tools mostly rely on cloud services, posing code privacy risks
- There is a lack of lightweight, out-of-the-box local code review solutions
- Code quality reports are not intuitive enough to quickly locate issues

**CodeReview-AI** was born to solve these pain points!

### ✨ Key Features

- 🚀 **Zero Dependencies** - Pure Python standard library, no extra dependencies
- 🔒 **Local First** - Supports Ollama local LLM, zero code privacy risk
- 🎯 **Multi-dimensional Analysis** - Static analysis + AI intelligent review
- 🎨 **Beautiful TUI** - Terminal UI with color support
- 📊 **Multiple Report Formats** - Markdown, JSON, HTML, SARIF
- 🔗 **Git Integration** - Auto-detect changed files, pre-commit hook support

---

## 🚀 Quick Start

### Requirements

- **Python**: 3.8 or higher
- **OS**: Linux / macOS / Windows

### Installation

```bash
# Option 1: Clone and use directly
git clone https://github.com/gitstq/CodeReview-AI.git
cd CodeReview-AI
python3 -m codereview_ai --help

# Option 2: Install to system
pip install -e .

# Option 3: Direct usage
python3 -m pip install pyyaml  # Optional, for YAML config
codereview-ai --help
```

### Basic Usage

```bash
# Review all Python files in current directory
codereview-ai

# Review specific directory
codereview-ai src/

# Review specific files
codereview-ai main.py utils.py

# Generate Markdown report
codereview-ai --format markdown -o report.md

# Generate HTML report
codereview-ai --format html -o report.html
```

---

## 📖 Detailed Usage Guide

### Git Integration

```bash
# Review only Git changed files
codereview-ai --git

# Review only staged files
codereview-ai --git --staged

# Review changes in last 3 commits
codereview-ai --git --commit-range HEAD~3..HEAD
```

### AI Review

```bash
# Enable AI review (requires API key)
codereview-ai --ai

# Use OpenAI
codereview-ai --ai --backend openai --model gpt-4o-mini

# Use Anthropic Claude
codereview-ai --ai --backend anthropic --model claude-3-haiku

# Use Ollama local model
codereview-ai --ai --backend ollama --model codellama
```

---

## 📄 License

This project is licensed under the [MIT](LICENSE) License.

---

<a name="繁體中文"></a>
## 🎉 專案介紹

**CodeReview-AI** 是一款輕量級、零依賴的AI驅動程式碼審查工具，專為追求程式碼品質的開發者打造。它結合了傳統靜態程式碼分析與先進的AI智慧審查，幫助您在編碼過程中及時發現潛在問題，提升程式碼品質。

### ✨ 核心特性

- 🚀 **零依賴設計** - 純Python標準庫實現，無需安裝額外依賴
- 🔒 **本地優先** - 支援Ollama本地LLM，程式碼隱私零風險
- 🎯 **多維度分析** - 靜態分析 + AI智慧審查，雙重保障
- 🎨 **美觀TUI** - 終端互動介面，支援彩色輸出
- 📊 **多格式報告** - 支援Markdown、JSON、HTML、SARIF
- 🔗 **Git整合** - 自動檢測變更檔案，支援pre-commit鉤子

---

## 🚀 快速開始

### 環境要求

- **Python**: 3.8 或更高版本
- **作業系統**: Linux / macOS / Windows

### 安裝

```bash
# 方式1: 直接克隆使用
git clone https://github.com/gitstq/CodeReview-AI.git
cd CodeReview-AI
python3 -m codereview_ai --help

# 方式2: 安裝到系統
pip install -e .
```

### 基礎用法

```bash
# 審查當前目錄所有Python檔案
codereview-ai

# 審查指定目錄
codereview-ai src/

# 審查指定檔案
codereview-ai main.py utils.py

# 生成Markdown報告
codereview-ai --format markdown -o report.md
```

---

## 📄 開源協議

本專案採用 [MIT](LICENSE) 協議開源。

---

<div align="center">

Made with ❤️ by CodeReview-AI Team

</div>
