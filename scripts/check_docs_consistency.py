#!/usr/bin/env python3
"""
多语言文档一致性检查工具

用途：检查多语言文档的结构一致性，确保所有语言版本符合项目标准
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 支持的语言列表
LANGUAGES = ["en", "zh", "fr", "es", "ar", "ru"]

# 语言显示名称
LANGUAGE_NAMES = {
    "en": "English",
    "zh": "中文",
    "fr": "Français",
    "es": "Español",
    "ar": "العربية",
    "ru": "Русский"
}

def find_markdown_files(docs_root: Path) -> Dict[str, List[Path]]:
    """查找所有语言的markdown文件"""
    files_by_lang = {}

    for lang in LANGUAGES:
        lang_dir = docs_root / lang
        if lang_dir.exists():
            files_by_lang[lang] = list(lang_dir.glob("**/*.md"))

    return files_by_lang

def get_relative_path(file_path: Path, lang_dir: Path) -> Path:
    """获取文件相对于语言目录的路径"""
    return file_path.relative_to(lang_dir)

def check_file_existence(files_by_lang: Dict[str, List[Path]]) -> List[Tuple[str, str]]:
    """检查所有语言版本的文档是否存在"""
    issues = []

    # 获取中文文档的相对路径作为参考
    if "zh" not in files_by_lang:
        return [("docs/zh", "中文文档目录不存在或为空")]

    zh_files = {get_relative_path(f, Path("docs/zh")) for f in files_by_lang["zh"]}

    # 检查其他语言是否缺少文件
    for lang in LANGUAGES:
        if lang == "zh" or lang not in files_by_lang:
            continue

        lang_files = {get_relative_path(f, Path(f"docs/{lang}")) for f in files_by_lang[lang]}
        missing = zh_files - lang_files

        for file in missing:
            issues.append((f"docs/{lang}/{file}", f"文件在中文版本中存在，但在{lang}版本中缺失"))

    return issues

def check_language_links(files_by_lang: Dict[str, List[Path]]) -> List[Tuple[str, str]]:
    """检查语言导航链接的正确性"""
    issues = []

    for lang, files in files_by_lang.items():
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 检查语言导航链接
                # 根据语言选择正则表达式模式
                if lang == "en":
                    pattern = r'\*English\s*\|\s*\[中文\]'
                elif lang == "zh":
                    pattern = r'\*\[English\].*\|\s*中文\s*\|'
                elif lang == "fr":
                    pattern = r'\*\[English\].*\|\s*\[中文\].*\|\s*Français\s*\|'
                elif lang == "es":
                    pattern = r'\*\[English\].*\|\s*\[中文\].*\|\s*\[Français\].*\|\s*Español\s*\|'
                elif lang == "ar":
                    pattern = r'\*\[English\].*\|\s*\[中文\].*\|\s*\[Français\].*\|\s*\[Español\].*\|\s*العربية\s*\|'
                elif lang == "ru":
                    pattern = r'\*\[English\].*\|\s*\[中文\].*\|\s*\[Français\].*\|\s*\[Español\].*\|\s*\[العربية\].*\|\s*Русский\s*\*'
                else:
                    pattern = r'\*\[English\]|\*English|\*中文|\*Français|\*Español|\*العربية|\*Русский'

                nav_line_match = re.search(pattern, content)
                if not nav_line_match:
                    issues.append((str(file_path), "缺少语言导航链接或格式不正确"))
                    continue

                # 提取语言导航链接行
                lines = content.split("\n")
                nav_line = ""
                for line in lines:
                    if "*English" in line or "*[English]" in line or "*中文" in line or "*Français" in line or "*Español" in line or "*العربية" in line or "*Русский" in line:
                        nav_line = line
                        break

                # 检查当前语言是否为纯文本
                lang_text = LANGUAGE_NAMES.get(lang, lang)

                if f"[{lang_text}]" in nav_line and f"[{lang_text}] " not in nav_line:
                    issues.append((str(file_path), f"当前语言'{lang_text}'不应该是链接"))
                elif lang_text not in nav_line:
                    issues.append((str(file_path), f"语言导航链接中缺少当前语言'{lang_text}'"))

                # 检查是否包含所有语言
                for check_lang, check_lang_text in LANGUAGE_NAMES.items():
                    if check_lang == lang:
                        continue  # 当前语言应该是纯文本

                    if check_lang_text not in nav_line:
                        issues.append((str(file_path), f"语言导航链接中缺少'{check_lang_text}'"))

                # 检查相对路径是否正确
                relative_path = get_relative_path(file_path, Path(f"docs/{lang}"))
                depth = len(relative_path.parts)

                # 如果文件不在语言根目录，检查相对路径
                if depth > 0:
                    for check_lang, check_lang_text in LANGUAGE_NAMES.items():
                        if check_lang == lang:
                            continue  # 当前语言不需要链接

                        # 查找该语言的链接
                        lang_link_match = re.search(rf'\[{check_lang_text}\]\((.*?)\)', nav_line)
                        if lang_link_match:
                            link_path = lang_link_match.group(1)
                            if not link_path.startswith("../"):
                                issues.append((str(file_path), f"'{check_lang_text}'链接的相对路径格式不正确，应使用相对路径"))

    return issues

def check_document_structure(files_by_lang: Dict[str, List[Path]]) -> List[Tuple[str, str]]:
    """检查文档结构的基本一致性和空文档"""
    issues = []

    # 我们不再需要中文文档作为参考，直接检查每个文档本身

    # 检查所有语言的文档
    for lang in LANGUAGES:
        if lang not in files_by_lang:
            continue

        for file_path in files_by_lang[lang]:
            # 我们不再需要比较相对路径，只需检查文档本身
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

                # 检查文档是否为空或几乎为空（占位符文档）
                if not content:
                    issues.append((str(file_path), "文档为空"))
                elif len(content) < 100:  # 如果内容少于100个字符，可能是占位符
                    issues.append((str(file_path), f"文档内容过少，可能是占位符文档 ({len(content)} 字符)"))

                # 检查是否至少有一个H1标题
                headings = re.findall(r'^(#+)\s+(.*?)$', content, re.MULTILINE)
                h1_headings = [h for h in headings if len(h[0]) == 1]
                if not h1_headings:
                    issues.append((str(file_path), "文档缺少H1标题"))

    return issues

def check_special_elements(files_by_lang: Dict[str, List[Path]]) -> List[Tuple[str, str]]:
    """检查特殊元素（如Mermaid图表）的一致性"""
    issues = []

    # 获取中文文档中的特殊元素作为参考
    if "zh" not in files_by_lang:
        return issues

    zh_elements = {}
    for file_path in files_by_lang["zh"]:
        relative_path = get_relative_path(file_path, Path("docs/zh"))
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 检查Mermaid图表
            mermaid_count = content.count("```mermaid")
            zh_elements[str(relative_path)] = {"mermaid": mermaid_count}

    # 检查其他语言的特殊元素
    for lang in LANGUAGES:
        if lang == "zh" or lang not in files_by_lang:
            continue

        for file_path in files_by_lang[lang]:
            relative_path = get_relative_path(file_path, Path(f"docs/{lang}"))
            rel_path_str = str(relative_path)

            if rel_path_str not in zh_elements:
                continue  # 中文版本中没有对应文件

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 检查Mermaid图表
                mermaid_count = content.count("```mermaid")

                if mermaid_count != zh_elements[rel_path_str]["mermaid"]:
                    issues.append((str(file_path), f"Mermaid图表数量与中文版本不一致 ({mermaid_count} vs {zh_elements[rel_path_str]['mermaid']})"))

    return issues

def main():
    parser = argparse.ArgumentParser(description="检查多语言文档的一致性")
    parser.add_argument("--docs-dir", default="docs", help="文档根目录的路径")
    parser.add_argument("--verbose", action="store_true", help="显示详细输出")
    parser.add_argument("--check-type", choices=["all", "existence", "links", "structure", "elements"],
                        default="all", help="指定要检查的类型")
    args = parser.parse_args()

    docs_root = Path(args.docs_dir)
    if not docs_root.exists():
        print(f"错误: '{args.docs_dir}' 目录不存在")
        sys.exit(1)

    print("检查多语言文档一致性...\n")

    # 查找所有markdown文件
    files_by_lang = find_markdown_files(docs_root)

    # 执行各种检查
    existence_issues = []
    link_issues = []
    structure_issues = []
    element_issues = []

    if args.check_type in ["all", "existence"]:
        existence_issues = check_file_existence(files_by_lang)

    if args.check_type in ["all", "links"]:
        link_issues = check_language_links(files_by_lang)

    if args.check_type in ["all", "structure"]:
        structure_issues = check_document_structure(files_by_lang)

    if args.check_type in ["all", "elements"]:
        element_issues = check_special_elements(files_by_lang)

    all_issues = existence_issues + link_issues + structure_issues + element_issues

    # 输出结果
    if all_issues:
        print("发现问题:")

        if existence_issues and args.check_type in ["all", "existence"]:
            print("\n文件存在性问题:")
            for file, issue in existence_issues:
                print(f"  - {file}: {issue}")

        if link_issues and args.check_type in ["all", "links"]:
            print("\n语言导航链接问题:")
            for file, issue in link_issues:
                print(f"  - {file}: {issue}")

        if structure_issues and args.check_type in ["all", "structure"]:
            print("\n文档结构问题:")
            for file, issue in structure_issues:
                print(f"  - {file}: {issue}")

        if element_issues and args.check_type in ["all", "elements"]:
            print("\n特殊元素问题:")
            for file, issue in element_issues:
                print(f"  - {file}: {issue}")

        print(f"\n总计: {len(all_issues)} 个问题")
        sys.exit(1)
    else:
        print(f"恭喜！所有{args.check_type}类型的文档检查通过。")
        sys.exit(0)

if __name__ == "__main__":
    main()
