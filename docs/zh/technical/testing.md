# 测试指南

*[English](../../en/technical/testing.md) | 中文 | [Français](../../fr/technical/testing.md) | [Español](../../es/technical/testing.md) | [العربية](../../ar/technical/testing.md) | [Русский](../../ru/technical/testing.md)*

## 测试框架

MCP数据库工具使用以下测试框架和工具：

- **pytest**：主要测试框架
- **pytest-asyncio**：用于异步测试支持
- **pytest-docker**：用于数据库集成测试
- **pytest-cov**：用于代码覆盖率分析

## 测试结构

测试目录结构如下：

```
tests/
├── unit/               # 单元测试
├── integration/        # 集成测试
│   ├── fixtures.py    # 测试辅助类
│   └── conftest.py    # pytest配置和工具
```

## 运行测试

### 运行所有测试

```bash
# 安装测试依赖
uv pip install -e ".[test]"

# 运行所有测试
pytest
```

### 运行特定测试

```bash
# 运行单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/test_base.py

# 运行特定测试函数
pytest tests/unit/test_base.py::test_function_name
```

### 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest --cov=src/mcp_dbutils --cov-report=term --cov-report=xml:coverage.xml tests/
```

## 测试类型

### 单元测试

单元测试位于 `tests/unit/` 目录，专注于测试单个组件的功能，通常使用模拟对象替代外部依赖。

示例：

```python
def test_database_handler_factory():
    # 测试数据库处理器工厂函数
    config = {"type": "sqlite", "path": ":memory:"}
    handler = create_handler(config)
    assert isinstance(handler, SQLiteHandler)
```

### 集成测试

集成测试位于 `tests/integration/` 目录，测试多个组件的交互，通常使用真实的数据库连接。

示例：

```python
@pytest.mark.asyncio
async def test_sqlite_query_execution(sqlite_handler):
    # 测试SQLite查询执行
    result = await sqlite_handler.execute_query("SELECT 1 as test")
    assert "test" in result
    assert result["test"] == 1
```

## 测试辅助工具

### fixtures.py

`tests/integration/fixtures.py` 文件包含测试辅助类和函数，如：

- `TestConnectionHandler`：用于测试连接处理器
- `MockSession`：模拟MCP会话
- `create_test_database`：创建测试数据库

### conftest.py

`tests/conftest.py` 文件包含pytest配置和全局fixture：

```python
@pytest.fixture
async def sqlite_handler():
    """提供SQLite测试处理器"""
    config = {"type": "sqlite", "path": ":memory:"}
    handler = SQLiteHandler(config)
    yield handler
    await handler.cleanup()
```

## 最佳实践

1. **测试覆盖率**：保持至少80%的代码覆盖率
2. **隔离测试**：确保测试不依赖于其他测试的状态
3. **清理资源**：使用fixture的teardown机制清理资源
4. **模拟外部依赖**：使用unittest.mock模拟外部依赖
5. **测试异常情况**：测试错误处理和边缘情况
6. **参数化测试**：使用pytest.mark.parametrize测试多种输入

## SonarCloud集成

测试结果会自动上传到SonarCloud进行分析。SonarCloud会检查：

- 代码覆盖率
- 测试成功率
- 代码质量问题
- 安全漏洞

您可以在[SonarCloud仪表板](https://sonarcloud.io/dashboard?id=donghao1393_mcp-dbutils)上查看测试结果和代码质量报告。