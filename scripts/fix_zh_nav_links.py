#!/usr/bin/env python3
"""
修复中文文档中的语言导航链接

用途：将中文文档中的语言导航链接中的"[中文]"修改为纯文本"中文"
"""

import os
import re
from pathlib import Path


def fix_zh_nav_links(docs_root: Path) -> int:
    """修复中文文档中的语言导航链接"""
    fixed_count = 0
    zh_dir = docs_root / "zh"
    
    if not zh_dir.exists():
        print("错误: 中文文档目录不存在")
        return 0
    
    # 递归查找所有中文markdown文件
    for md_file in zh_dir.glob("**/*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找语言导航链接
        nav_line_match = re.search(r'\*\[(.*?)\](.*?)\s*\|\s*(.*?)\*', content)
        if nav_line_match:
            nav_line = nav_line_match.group(0)
            
            # 检查是否需要修复
            if "[中文]" in nav_line:
                # 替换 [中文](链接) 为 中文
                fixed_nav_line = re.sub(r'\[中文\]\([^)]*\)', '中文', nav_line)
                
                # 更新文件内容
                new_content = content.replace(nav_line, fixed_nav_line)
                
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"已修复: {md_file}")
                fixed_count += 1
    
    return fixed_count

def main():
    docs_root = Path("docs")
    if not docs_root.exists():
        print("错误: 'docs' 目录不存在")
        return
    
    print("开始修复中文文档中的语言导航链接...\n")
    
    fixed_count = fix_zh_nav_links(docs_root)
    
    print(f"\n完成! 已修复 {fixed_count} 个文件。")

if __name__ == "__main__":
    main()
