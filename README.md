# 🔍 CodeReview-AI

<div align="center">

**轻量级AI代码审查助手 | Lightweight AI Code Review Assistant | 輕量級AI程式碼審查助手**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-19%20passed-success.svg)]()

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

</div>

---

## 简体中文

### 🎉 项目介绍

**CodeReview-AI** 是一款零依赖的轻量级AI代码审查CLI工具，专为开发者打造。它结合了静态代码分析和AI大模型能力，帮助您在代码提交前发现潜在问题，提升代码质量。

**核心价值：**
- 🚀 **开箱即用** - 纯Python标准库实现，无需安装任何依赖
- 🔒 **安全优先** - 内置50+安全规则，自动检测漏洞和风险
- 🤖 **AI增强** - 支持OpenAI、Anthropic、DeepSeek等多LLM后端
- 📊 **多格式报告** - Console/JSON/Markdown/HTML四种输出格式
- 🔧 **CI/CD集成** - 支持Git diff审查，轻松集成到流水线

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔐 **安全检测** | 硬编码密码、SQL注入、eval/exec危险调用、SSL验证禁用等 |
| 🐛 **Bug检测** | 空异常捕获、可变默认参数、不可达代码、类型比较等 |
| ⚡ **性能优化** | 循环内字符串拼接、重复正则编译、全局变量使用等 |
| 🎨 **代码规范** | 行长度检查、尾随空格、混合缩进等 |
| 📝 **可维护性** | TODO追踪、函数复杂度、魔法数字检测等 |
| 🤖 **AI分析** | 多LLM后端支持，智能识别复杂问题 |

### 🚀 快速开始

#### 环境要求
- Python 3.8+
- (可选) LLM API密钥用于AI增强分析

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/CodeReview-AI.git
cd CodeReview-AI

# 直接使用（零依赖）
python codereview_ai.py --help

# 或安装到系统
pip install -e .
```

#### 基本使用

```bash
# 审查单个文件
python codereview_ai.py review src/main.py

# 审查整个目录
python codereview_ai.py review ./src --format markdown -o report.md

# 审查Git变更
python codereview_ai.py diff HEAD~1

# 使用AI增强分析
export OPENAI_API_KEY="your-key"
python codereview_ai.py review ./src --llm openai

# 生成HTML报告
python codereview_ai.py review ./src --format html -o report.html
```

### 📖 详细使用指南

#### 命令说明

```bash
# 查看配置信息
python codereview_ai.py config

# 审查文件/目录
python codereview_ai.py review <path> [选项]
  -f, --format        输出格式: console/json/markdown/html
  -o, --output        输出文件路径
  --llm               LLM后端: openai/anthropic/deepseek
  --api-key           API密钥
  --no-static         禁用静态分析
  --exclude           排除目录

# 审查Git差异
python codereview_ai.py diff [base_ref] [选项]
  -r, --repo          仓库路径
```

#### 支持的语言

Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, R, Objective-C, C#, F#, Clojure, Erlang, Elixir, Haskell, Lua, Perl, Shell, SQL, HTML, CSS, SCSS, Vue, Svelte, JSON, YAML

### 💡 设计思路

**为什么选择零依赖？**
- 减少安装时间和环境冲突
- 提高工具的可移植性
- 降低安全风险面
- 便于集成到各种CI/CD环境

**技术选型原因：**
- **纯Python标准库** - 确保零依赖，跨平台兼容
- **正则+AST混合分析** - 兼顾性能和准确性
- **多LLM后端抽象** - 灵活适配不同AI服务
- **插件化报告器** - 易于扩展新输出格式

### 📦 打包与部署

```bash
# 构建分发包
python -m build

# 安装构建包
pip install dist/codereview_ai-1.0.0-py3-none-any.whl

# 使用命令
codereview-ai --help
crai review ./src
```

### 🤝 贡献指南

欢迎提交Issue和PR！请确保：
1. 代码通过所有测试 `python -m unittest discover tests/`
2. 遵循现有代码风格
3. 为新功能添加测试

### 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 繁體中文

### 🎉 專案介紹

**CodeReview-AI** 是一款零依賴的輕量級AI程式碼審查CLI工具，專為開發者打造。它結合了靜態程式碼分析和AI大模型能力，幫助您在程式碼提交前發現潛在問題，提升程式碼品質。

**核心價值：**
- 🚀 **開箱即用** - 純Python標準庫實現，無需安裝任何依賴
- 🔒 **安全優先** - 內建50+安全規則，自動檢測漏洞和風險
- 🤖 **AI增強** - 支援OpenAI、Anthropic、DeepSeek等多LLM後端
- 📊 **多格式報告** - Console/JSON/Markdown/HTML四種輸出格式
- 🔧 **CI/CD整合** - 支援Git diff審查，輕鬆整合到流水線

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔐 **安全檢測** | 硬編碼密碼、SQL注入、eval/exec危險呼叫、SSL驗證禁用等 |
| 🐛 **Bug檢測** | 空異常捕獲、可變預設參數、不可達程式碼、型別比較等 |
| ⚡ **效能最佳化** | 迴圈內字串拼接、重複正規表示式編譯、全域變數使用等 |
| 🎨 **程式碼規範** | 行長度檢查、尾隨空格、混合縮排等 |
| 📝 **可維護性** | TODO追蹤、函式複雜度、魔法數字檢測等 |
| 🤖 **AI分析** | 多LLM後端支援，智慧識別複雜問題 |

### 🚀 快速開始

#### 環境要求
- Python 3.8+
- (可選) LLM API金鑰用於AI增強分析

#### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/CodeReview-AI.git
cd CodeReview-AI

# 直接使用（零依賴）
python codereview_ai.py --help

# 或安裝到系統
pip install -e .
```

#### 基本使用

```bash
# 審查單個檔案
python codereview_ai.py review src/main.py

# 審查整個目錄
python codereview_ai.py review ./src --format markdown -o report.md

# 審查Git變更
python codereview_ai.py diff HEAD~1

# 使用AI增強分析
export OPENAI_API_KEY="your-key"
python codereview_ai.py review ./src --llm openai

# 生成HTML報告
python codereview_ai.py review ./src --format html -o report.html
```

### 📖 詳細使用指南

#### 命令說明

```bash
# 查看配置資訊
python codereview_ai.py config

# 審查檔案/目錄
python codereview_ai.py review <path> [選項]
  -f, --format        輸出格式: console/json/markdown/html
  -o, --output        輸出檔案路徑
  --llm               LLM後端: openai/anthropic/deepseek
  --api-key           API金鑰
  --no-static         禁用靜態分析
  --exclude           排除目錄

# 審查Git差異
python codereview_ai.py diff [base_ref] [選項]
  -r, --repo          倉庫路徑
```

### 📄 開源協議

MIT License - 詳見 [LICENSE](LICENSE) 檔案

---

## English

### 🎉 Introduction

**CodeReview-AI** is a zero-dependency lightweight AI code review CLI tool designed for developers. It combines static code analysis with AI large language model capabilities to help you identify potential issues before code submission and improve code quality.

**Core Values:**
- 🚀 **Out-of-the-box** - Pure Python standard library implementation, no dependencies required
- 🔒 **Security First** - Built-in 50+ security rules, automatic vulnerability and risk detection
- 🤖 **AI Enhanced** - Multi-LLM backend support (OpenAI, Anthropic, DeepSeek)
- 📊 **Multi-format Reports** - Console/JSON/Markdown/HTML output formats
- 🔧 **CI/CD Integration** - Git diff review support, easy pipeline integration

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔐 **Security Detection** | Hardcoded passwords, SQL injection, eval/exec dangerous calls, SSL verification bypass |
| 🐛 **Bug Detection** | Bare except clauses, mutable default arguments, unreachable code, type comparisons |
| ⚡ **Performance** | String concatenation in loops, regex recompilation, global variable usage |
| 🎨 **Code Style** | Line length, trailing whitespace, mixed indentation |
| 📝 **Maintainability** | TODO tracking, function complexity, magic number detection |
| 🤖 **AI Analysis** | Multi-LLM backend support, intelligent complex issue identification |

### 🚀 Quick Start

#### Requirements
- Python 3.8+
- (Optional) LLM API key for AI-enhanced analysis

#### Installation

```bash
# Clone repository
git clone https://github.com/gitstq/CodeReview-AI.git
cd CodeReview-AI

# Use directly (zero dependencies)
python codereview_ai.py --help

# Or install to system
pip install -e .
```

#### Basic Usage

```bash
# Review a single file
python codereview_ai.py review src/main.py

# Review entire directory
python codereview_ai.py review ./src --format markdown -o report.md

# Review Git changes
python codereview_ai.py diff HEAD~1

# Use AI-enhanced analysis
export OPENAI_API_KEY="your-key"
python codereview_ai.py review ./src --llm openai

# Generate HTML report
python codereview_ai.py review ./src --format html -o report.html
```

### 📖 Detailed Usage

#### Command Reference

```bash
# Show configuration
python codereview_ai.py config

# Review file/directory
python codereview_ai.py review <path> [options]
  -f, --format        Output format: console/json/markdown/html
  -o, --output        Output file path
  --llm               LLM backend: openai/anthropic/deepseek
  --api-key           API key
  --no-static         Disable static analysis
  --exclude           Directories to exclude

# Review Git diff
python codereview_ai.py diff [base_ref] [options]
  -r, --repo          Repository path
```

#### Supported Languages

Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, R, Objective-C, C#, F#, Clojure, Erlang, Elixir, Haskell, Lua, Perl, Shell, SQL, HTML, CSS, SCSS, Vue, Svelte, JSON, YAML

### 💡 Design Philosophy

**Why Zero Dependencies?**
- Reduce installation time and environment conflicts
- Improve tool portability
- Minimize security attack surface
- Easy integration into various CI/CD environments

**Technical Choices:**
- **Pure Python Standard Library** - Ensures zero dependencies, cross-platform compatibility
- **Regex + AST Hybrid Analysis** - Balances performance and accuracy
- **Multi-LLM Backend Abstraction** - Flexible adaptation to different AI services
- **Pluggable Reporters** - Easy to extend new output formats

### 📦 Packaging & Deployment

```bash
# Build distribution
python -m build

# Install built package
pip install dist/codereview_ai-1.0.0-py3-none-any.whl

# Use commands
codereview-ai --help
crai review ./src
```

### 🤝 Contributing

Issues and PRs are welcome! Please ensure:
1. All tests pass: `python -m unittest discover tests/`
2. Follow existing code style
3. Add tests for new features

### 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

<div align="center">

**Made with ❤️ by gitstq**

⭐ Star this repo if you find it helpful!

</div>