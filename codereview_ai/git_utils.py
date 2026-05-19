"""
Git工具模块
提供Git相关功能
"""
import os
import subprocess
from typing import List, Optional, Tuple
from pathlib import Path


class GitUtils:
    """Git工具类"""
    
    @staticmethod
    def is_git_repo(path: str = ".") -> bool:
        """检查路径是否是Git仓库"""
        git_dir = os.path.join(path, ".git")
        return os.path.isdir(git_dir)
    
    @staticmethod
    def get_repo_root(path: str = ".") -> Optional[str]:
        """获取Git仓库根目录"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def get_changed_files(path: str = ".", staged: bool = False, commit_range: Optional[str] = None) -> List[str]:
        """
        获取变更的文件列表
        
        Args:
            path: 仓库路径
            staged: 是否只检查暂存区
            commit_range: commit范围，如 "HEAD~3..HEAD"
        
        Returns:
            变更文件列表
        """
        try:
            if commit_range:
                # 检查指定commit范围
                result = subprocess.run(
                    ["git", "diff", "--name-only", commit_range],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            elif staged:
                # 检查暂存区
                result = subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                # 检查工作区变更
                result = subprocess.run(
                    ["git", "diff", "--name-only"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            
            files = result.stdout.strip().split("\n")
            return [f for f in files if f]
        except subprocess.CalledProcessError:
            return []
    
    @staticmethod
    def get_untracked_files(path: str = ".") -> List[str]:
        """获取未跟踪的文件"""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=path,
                capture_output=True,
                text=True,
                check=True,
            )
            files = result.stdout.strip().split("\n")
            return [f for f in files if f]
        except subprocess.CalledProcessError:
            return []
    
    @staticmethod
    def get_file_content_at_commit(file_path: str, commit: str = "HEAD") -> Optional[str]:
        """获取指定commit的文件内容"""
        try:
            result = subprocess.run(
                ["git", "show", f"{commit}:{file_path}"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def get_file_diff(path: str = ".", file_path: Optional[str] = None, staged: bool = False) -> str:
        """获取文件diff"""
        try:
            cmd = ["git", "diff"]
            if staged:
                cmd.append("--cached")
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    @staticmethod
    def get_current_branch(path: str = ".") -> Optional[str]:
        """获取当前分支名"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip() or None
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def get_last_commit_info(path: str = ".") -> Optional[dict]:
        """获取最后一次commit信息"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%an|%ae|%ad|%s"],
                cwd=path,
                capture_output=True,
                text=True,
                check=True,
            )
            parts = result.stdout.strip().split("|", 4)
            if len(parts) >= 5:
                return {
                    "hash": parts[0],
                    "author_name": parts[1],
                    "author_email": parts[2],
                    "date": parts[3],
                    "subject": parts[4],
                }
            return None
        except subprocess.CalledProcessError:
            return None
    
    @staticmethod
    def install_hook(path: str = ".", hook_name: str = "pre-commit") -> bool:
        """安装Git钩子"""
        hooks_dir = os.path.join(path, ".git", "hooks")
        if not os.path.isdir(hooks_dir):
            return False
        
        hook_path = os.path.join(hooks_dir, hook_name)
        
        hook_content = f"""#!/bin/sh
# CodeReview-AI {hook_name} hook
# Auto-generated by codereview-ai --init

echo "Running CodeReview-AI..."
codereview-ai --git --staged

if [ $? -ne 0 ]; then
    echo "CodeReview-AI found issues. Commit aborted."
    echo "Use --no-verify to bypass this check."
    exit 1
fi

exit 0
"""
        
        try:
            with open(hook_path, "w") as f:
                f.write(hook_content)
            os.chmod(hook_path, 0o755)
            return True
        except Exception:
            return False
