#!/usr/bin/env python3
"""
Fix specific import issues in test files.
"""

import os
import re

# 要修复的文件和对应的修复
FIXES = {
    "../tests/integration/test_logging.py": [
        (r"import MagicMock, patch", "from unittest.mock import MagicMock, patch"),
    ],
    "../tests/integration/test_sqlite_config.py": [
        (r"import Path", "from pathlib import Path"),
    ],
    "../tests/integration/test_mysql_handler_extended.py": [
        # 检查并修复语法错误
        (r"import\s+\n\s+pytest_asyncio", "import pytest"),
    ],
    "../tests/integration/test_sqlite_handler_extended.py": [
        # 检查并修复语法错误
        (r"import\s+\n\s+pytest_asyncio", "import pytest"),
    ],
}

def fix_file(file_path, fixes):
    """修复单个文件的特定问题"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # 应用所有修复
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        # 写回文件
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

def main():
    """主函数"""
    for file_path, fixes in FIXES.items():
        if os.path.exists(file_path):
            fix_file(file_path, fixes)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
