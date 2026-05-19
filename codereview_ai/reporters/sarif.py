"""
SARIF报告生成器
SARIF (Static Analysis Results Interchange Format) 是静态分析结果的标准格式
兼容GitHub/GitLab等平台的代码扫描功能
"""
import json
from datetime import datetime
from typing import Dict, List, Any
from .base import BaseReporter, AnalysisResult
from ..analyzer.base import Issue, IssueSeverity


class SARIFReporter(BaseReporter):
    """SARIF报告生成器"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.tool_name = self.config.get("tool_name", "CodeReview-AI")
        self.tool_version = self.config.get("tool_version", "1.0.0")
    
    @property
    def name(self) -> str:
        return "sarif"
    
    @property
    def extension(self) -> str:
        return "sarif"
    
    def generate(self, result: AnalysisResult) -> str:
        """生成SARIF报告"""
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [self._create_run(result)]
        }
        
        return json.dumps(sarif, ensure_ascii=False, indent=2)
    
    def _create_run(self, result: AnalysisResult) -> Dict[str, Any]:
        """创建SARIF run对象"""
        # 收集所有规则
        rules = {}
        for issue in result.issues:
            rule_id = issue.rule_id or issue.rule_name or "UNKNOWN"
            if rule_id not in rules:
                rules[rule_id] = self._create_rule(issue)
        
        # 创建结果
        results = [self._create_result(issue) for issue in result.issues]
        
        run = {
            "tool": {
                "driver": {
                    "name": self.tool_name,
                    "version": self.tool_version,
                    "informationUri": "https://github.com/yourusername/codereview-ai",
                    "rules": list(rules.values()),
                }
            },
            "results": results,
            "invocations": [{
                "executionSuccessful": True,
                "startTimeUtc": result.start_time.isoformat() if result.start_time else datetime.now().isoformat(),
                "endTimeUtc": result.end_time.isoformat() if result.end_time else datetime.now().isoformat(),
            }],
        }
        
        return run
    
    def _create_rule(self, issue: Issue) -> Dict[str, Any]:
        """创建SARIF规则对象"""
        severity_map = {
            IssueSeverity.CRITICAL: "error",
            IssueSeverity.HIGH: "error",
            IssueSeverity.MEDIUM: "warning",
            IssueSeverity.LOW: "note",
            IssueSeverity.INFO: "note",
        }
        
        rule_id = issue.rule_id or issue.rule_name or "UNKNOWN"
        
        rule = {
            "id": rule_id,
            "name": issue.rule_name or rule_id,
            "shortDescription": {
                "text": issue.message,
            },
            "fullDescription": {
                "text": issue.description or issue.message,
            },
            "defaultConfiguration": {
                "level": severity_map.get(issue.severity, "warning"),
            },
        }
        
        # 添加帮助文本
        if issue.suggestion:
            rule["help"] = {
                "text": issue.suggestion,
                "markdown": issue.suggestion,
            }
        
        # 添加属性
        rule["properties"] = {
            "category": issue.category.value,
            "severity": issue.severity.value,
        }
        
        return rule
    
    def _create_result(self, issue: Issue) -> Dict[str, Any]:
        """创建SARIF结果对象"""
        severity_map = {
            IssueSeverity.CRITICAL: "error",
            IssueSeverity.HIGH: "error",
            IssueSeverity.MEDIUM: "warning",
            IssueSeverity.LOW: "note",
            IssueSeverity.INFO: "note",
        }
        
        rule_id = issue.rule_id or issue.rule_name or "UNKNOWN"
        
        result = {
            "ruleId": rule_id,
            "ruleIndex": 0,  # 简化处理
            "level": severity_map.get(issue.severity, "warning"),
            "message": {
                "text": issue.message,
            },
            "locations": [self._create_location(issue)],
        }
        
        # 添加代码片段
        if issue.code_snippet:
            result["locations"][0]["physicalLocation"]["region"]["snippet"] = {
                "text": issue.code_snippet,
            }
        
        return result
    
    def _create_location(self, issue: Issue) -> Dict[str, Any]:
        """创建SARIF位置对象"""
        location = {
            "physicalLocation": {
                "artifactLocation": {
                    "uri": issue.file_path,
                },
            }
        }
        
        # 添加区域信息
        if issue.line > 0:
            region = {
                "startLine": issue.line,
            }
            
            if issue.column > 0:
                region["startColumn"] = issue.column
            
            if issue.end_line > 0:
                region["endLine"] = issue.end_line
            
            if issue.end_column > 0:
                region["endColumn"] = issue.end_column
            
            location["physicalLocation"]["region"] = region
        
        return location
