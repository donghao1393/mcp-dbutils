#!/usr/bin/env python3
"""
Fix import issues in test files.
"""

import os
import re
import glob

# 要修改的测试文件目录
TEST_DIR = "../tests/integration"

def fix_file(file_path):
    """修复单个文件的导入问题"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 修复错误的导入
    content = re.sub(
        r'from unittest\.mock import os',
        'import os',
        content
    )
    
    content = re.sub(
        r'from pathlib import os',
        'import os',
        content
    )
    
    # 确保导入块正确排序
    lines = content.split('\n')
    import_block_start = None
    import_block_end = None
    
    # 查找导入块
    for i, line in enumerate(lines):
        if import_block_start is None and (line.startswith('import ') or line.startswith('from ')):
            import_block_start = i
        elif import_block_start is not None and not (line.startswith('import ') or line.startswith('from ')) and line.strip() != '':
            import_block_end = i
            break
    
    if import_block_start is not None:
        if import_block_end is None:
            import_block_end = len(lines)
        
        # 提取导入块
        import_lines = lines[import_block_start:import_block_end]
        
        # 按照标准库、第三方库和本地模块排序
        stdlib_imports = []
        thirdparty_imports = []
        local_imports = []
        
        for line in import_lines:
            if line.strip() == '':
                continue
                
            if line.startswith('import os') or line.startswith('from os'):
                stdlib_imports.insert(0, line)  # 确保os排在最前面
            elif line.startswith('import ') or line.startswith('from '):
                module = line.split()[1].split('.')[0]
                if module in ('pytest', 'yaml', 'anyio'):
                    thirdparty_imports.append(line)
                elif module in ('unittest', 'tempfile', 'pathlib'):
                    stdlib_imports.append(line)
                else:
                    local_imports.append(line)
        
        # 排序每个类别
        stdlib_imports.sort()
        thirdparty_imports.sort()
        local_imports.sort()
        
        # 重建导入块
        sorted_imports = []
        if stdlib_imports:
            sorted_imports.extend(stdlib_imports)
            sorted_imports.append('')
        if thirdparty_imports:
            sorted_imports.extend(thirdparty_imports)
            sorted_imports.append('')
        if local_imports:
            sorted_imports.extend(local_imports)
        
        # 替换原始导入块
        lines[import_block_start:import_block_end] = sorted_imports
        content = '\n'.join(lines)
    
    # 写回文件
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

def main():
    """主函数"""
    # 获取所有测试文件
    test_files = glob.glob(os.path.join(TEST_DIR, "test_*.py"))
    
    # 处理每个文件
    for file_path in test_files:
        fix_file(file_path)
    
    print(f"Processed {len(test_files)} files")

if __name__ == "__main__":
    main()
