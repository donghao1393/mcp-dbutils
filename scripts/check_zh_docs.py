#!/usr/bin/env python3
"""
中文文档一致性检查工具

用途：检查中文文档是否符合一致性标准，以便作为其他语言的模板
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def check_zh_docs(docs_root: Path) -> List[Tuple[str, str]]:
    """检查所有中文文档的一致性"""
    issues = []
    zh_dir = docs_root / "zh"
    
    if not zh_dir.exists():
        return [("docs/zh", "中文文档目录不存在")]
    
    # 递归查找所有中文markdown文件
    for md_file in zh_dir.glob("**/*.md"):
        relative_path = md_file.relative_to(zh_dir)
        
        # 检查文件内容
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查标题
            if not content.startswith("# "):
                issues.append((str(md_file), "文档应以H1标题开始"))
            
            # 检查语言导航链接
            nav_line_match = re.search(r'\*\[(.*?)\](.*?)\s*\|\s*(.*?)\*', content)
            if not nav_line_match:
                issues.append((str(md_file), "缺少语言导航链接"))
            else:
                nav_line = nav_line_match.group(0)
                
                # 检查当前语言（中文）是否为纯文本
                if "[中文]" in nav_line:
                    issues.append((str(md_file), "当前语言'中文'不应该是链接"))
                elif "中文" not in nav_line:
                    issues.append((str(md_file), "语言导航链接中缺少'中文'"))
                
                # 检查相对路径是否正确
                depth = len(relative_path.parts)
                correct_prefix = "../" * depth
                
                # 检查是否使用了正确的相对路径格式
                if depth > 0:
                    for lang in ["en", "fr", "es", "ar", "ru"]:
                        lang_text = {
                            "en": "English",
                            "fr": "Français",
                            "es": "Español",
                            "ar": "العربية",
                            "ru": "Русский"
                        }[lang]
                        
                        # 查找该语言的链接
                        lang_link_match = re.search(rf'\[{lang_text}\]\((.*?)\)', nav_line)
                        if lang_link_match:
                            link_path = lang_link_match.group(1)
                            if not link_path.startswith(correct_prefix):
                                issues.append((str(md_file), f"'{lang_text}'链接的相对路径不正确，应使用'{correct_prefix}'"))
            
            # 检查Mermaid图表
            if "```mermaid" in content:
                # 确保mermaid图表格式正确
                mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
                for block in mermaid_blocks:
                    if not block.strip():
                        issues.append((str(md_file), "存在空的Mermaid图表"))
    
    return issues

def main():
    docs_root = Path("docs")
    if not docs_root.exists():
        print("错误: 'docs' 目录不存在")
        sys.exit(1)
    
    print("检查中文文档一致性...\n")
    
    issues = check_zh_docs(docs_root)
    if issues:
        print("发现问题:")
        for file, issue in issues:
            print(f"  - {file}: {issue}")
        print(f"\n总计: {len(issues)} 个问题")
        sys.exit(1)
    else:
        print("恭喜！中文文档检查通过，可以作为模板。")
        sys.exit(0)

if __name__ == "__main__":
    main()
