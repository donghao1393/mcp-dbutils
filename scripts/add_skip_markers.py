#!/usr/bin/env python3
"""
Add skip markers to all integration test files.
"""

import glob
import os
import re

# 要修改的测试文件目录
TEST_DIR = "../tests/integration"

# 要添加的导入语句
IMPORT_OS = "import os"

# 要添加的跳过标记
SKIP_CODE = """
# 检查是否跳过数据库测试
skip_db_tests = os.environ.get("SKIP_DB_TESTS", "false").lower() == "true"
skip_reason = "Database tests are skipped in CI environment"
"""

# 要添加的装饰器
SKIP_DECORATOR = '@pytest.mark.skipif(skip_db_tests, reason=skip_reason)'

def process_file(file_path):
    """处理单个测试文件，添加跳过标记"""
    with open(file_path, 'r') as f:
        content = f.read()

    # 检查文件是否已经包含跳过标记
    if 'skip_db_tests' in content:
        print(f"Skipping {file_path}, already contains skip markers")
        return

    # 添加 import os
    if 'import os' not in content:
        content = re.sub(
            r'(import\s+[^\n]+)',
            r'import os\n\1',
            content,
            count=1
        )

    # 添加跳过标记
    if 'skip_reason' not in content:
        # 查找 logger 定义后的位置
        logger_match = re.search(r'logger\s*=\s*create_logger\([^)]+\)[^\n]*\n', content)
        if logger_match:
            pos = logger_match.end()
            content = content[:pos] + SKIP_CODE + content[pos:]
        else:
            # 如果没有找到 logger 定义，则在导入语句后添加
            import_match = re.search(r'(from\s+[^\n]+\n|import\s+[^\n]+\n)+', content)
            if import_match:
                pos = import_match.end()
                content = content[:pos] + "\n" + SKIP_CODE + content[pos:]

    # 添加装饰器到每个测试函数
    content = re.sub(
        r'(@pytest\.mark\.asyncio\s*\n)',
        r'\1' + SKIP_DECORATOR + r'\n',
        content
    )

    # 写回文件
    with open(file_path, 'w') as f:
        f.write(content)

    print(f"Updated {file_path}")

def main():
    """主函数"""
    # 获取所有测试文件
    test_files = glob.glob(os.path.join(TEST_DIR, "test_*.py"))

    # 排除已经处理过的文件
    test_files = [f for f in test_files if not any(x in f for x in ['test_mongodb.py', 'test_redis.py', 'test_list_connections.py', 'test_monitoring.py', 'test_monitoring_enhanced.py'])]

    # 处理每个文件
    for file_path in test_files:
        process_file(file_path)

    print(f"Processed {len(test_files)} files")

if __name__ == "__main__":
    main()
