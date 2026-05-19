"""
CodeReview-AI 安装配置
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# 读取版本
version_path = Path(__file__).parent / "codereview_ai" / "__init__.py"
version = "1.0.0"
for line in version_path.read_text(encoding="utf-8").split("\n"):
    if line.startswith("__version__"):
        version = line.split("=")[1].strip().strip('"').strip("'")
        break

setup(
    name="codereview-ai",
    version=version,
    description="轻量级AI驱动代码审查与质量分析引擎",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CodeReview-AI Team",
    author_email="",
    url="https://github.com/yourusername/codereview-ai",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "yaml": ["pyyaml>=5.4.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "codereview-ai=codereview_ai.cli:main",
            "crai=codereview_ai.cli:main",
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
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    keywords="code review, static analysis, ai, llm, quality assurance, linter",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/codereview-ai/issues",
        "Source": "https://github.com/yourusername/codereview-ai",
    },
)
