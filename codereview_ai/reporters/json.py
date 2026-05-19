"""
JSON报告生成器
"""
import json
from .base import BaseReporter, AnalysisResult


class JSONReporter(BaseReporter):
    """JSON报告生成器"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.pretty = self.config.get("pretty", True)
    
    @property
    def name(self) -> str:
        return "json"
    
    @property
    def extension(self) -> str:
        return "json"
    
    def generate(self, result: AnalysisResult) -> str:
        """生成JSON报告"""
        data = result.to_dict()
        
        if self.pretty:
            return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            return json.dumps(data, ensure_ascii=False)
