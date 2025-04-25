#!/usr/bin/env python3
"""
修复英文文档中的语言导航链接

用途：将英文文档中的语言导航链接中的"[English]"修改为纯文本"English"
"""

import os
import re
from pathlib import Path


def fix_en_nav_links(docs_root: Path) -> int:
    """修复英文文档中的语言导航链接"""
    fixed_count = 0
    en_dir = docs_root / "en"
    
    if not en_dir.exists():
        print("错误: 英文文档目录不存在")
        return 0
    
    # 递归查找所有英文markdown文件
    for md_file in en_dir.glob("**/*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找语言导航链接
        nav_line_match = re.search(r'\*\[(.*?)\](.*?)\s*\|\s*(.*?)\*', content)
        if nav_line_match:
            nav_line = nav_line_match.group(0)
            
            # 检查是否需要修复
            if "[English]" in nav_line:
                # 替换 [English](链接) 为 English
                fixed_nav_line = re.sub(r'\[English\]\([^)]*\)', 'English', nav_line)
                
                # 更新文件内容
                new_content = content.replace(nav_line, fixed_nav_line)
                
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"已修复: {md_file}")
                fixed_count += 1
        else:
            # 如果没有找到语言导航链接，添加一个
            lines = content.split('\n')
            title_line = None
            
            # 查找标题行
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    title_line = i
                    break
            
            if title_line is not None:
                # 获取文件相对路径
                relative_path = md_file.relative_to(en_dir)
                depth = len(relative_path.parts)
                prefix = "../" * depth
                
                # 构建语言导航链接
                nav_line = f"*English | [{LANGUAGE_NAMES['zh']}]({prefix}zh/{relative_path}) | [{LANGUAGE_NAMES['fr']}]({prefix}fr/{relative_path}) | [{LANGUAGE_NAMES['es']}]({prefix}es/{relative_path}) | [{LANGUAGE_NAMES['ar']}]({prefix}ar/{relative_path}) | [{LANGUAGE_NAMES['ru']}]({prefix}ru/{relative_path})*"
                
                # 插入语言导航链接
                lines.insert(title_line + 1, "")
                lines.insert(title_line + 2, nav_line)
                lines.insert(title_line + 3, "")
                
                # 更新文件内容
                new_content = '\n'.join(lines)
                
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"已添加语言导航链接: {md_file}")
                fixed_count += 1
    
    return fixed_count

# 语言显示名称
LANGUAGE_NAMES = {
    "en": "English",
    "zh": "中文",
    "fr": "Français",
    "es": "Español",
    "ar": "العربية",
    "ru": "Русский"
}

def main():
    docs_root = Path("docs")
    if not docs_root.exists():
        print("错误: 'docs' 目录不存在")
        return
    
    print("开始修复英文文档中的语言导航链接...\n")
    
    fixed_count = fix_en_nav_links(docs_root)
    
    print(f"\n完成! 已修复 {fixed_count} 个文件。")

if __name__ == "__main__":
    main()
