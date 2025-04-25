# Testing Guide

*English | [中文](../../zh/technical/testing.md) | [Français](../../fr/technical/testing.md) | [Español](../../es/technical/testing.md) | [العربية](../../ar/technical/testing.md) | [Русский](../../ru/technical/testing.md)*

## Testing Framework

MCP Database Utilities uses the following testing frameworks and tools:

- **pytest**: Main testing framework
- **pytest-asyncio**: For asynchronous testing support
- **pytest-docker**: For database integration testing
- **pytest-cov**: For code coverage analysis

## Test Structure

The test directory structure is as follows:

```
tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
│   ├── fixtures.py    # Test helpers
│   └── conftest.py    # pytest configuration and utilities
```

## Running Tests

### Running All Tests

```bash
# Install test dependencies
uv pip install -e ".[test]"

# Run all tests
pytest
```

### Running Specific Tests

```bash
# Run unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_base.py

# Run specific test function
pytest tests/unit/test_base.py::test_function_name
```

### Generating Coverage Reports

```bash
# Generate coverage report
pytest --cov=src/mcp_dbutils --cov-report=term --cov-report=xml:coverage.xml tests/
```

## Test Types

### Unit Tests

Unit tests are located in the `tests/unit/` directory and focus on testing individual component functionality, typically using mock objects to replace external dependencies.

Example:

```python
def test_database_handler_factory():
    # Test database handler factory function
    config = {"type": "sqlite", "path": ":memory:"}
    handler = create_handler(config)
    assert isinstance(handler, SQLiteHandler)
```

### Integration Tests

Integration tests are located in the `tests/integration/` directory and test the interaction between multiple components, typically using real database connections.

Example:

```python
@pytest.mark.asyncio
async def test_sqlite_query_execution(sqlite_handler):
    # Test SQLite query execution
    result = await sqlite_handler.execute_query("SELECT 1 as test")
    assert "test" in result
    assert result["test"] == 1
```

## Test Helpers

### fixtures.py

The `tests/integration/fixtures.py` file contains test helper classes and functions, such as:

- `TestConnectionHandler`: For testing connection handlers
- `MockSession`: Mock MCP session
- `create_test_database`: Create test databases

### conftest.py

The `tests/conftest.py` file contains pytest configuration and global fixtures:

```python
@pytest.fixture
async def sqlite_handler():
    """Provide SQLite test handler"""
    config = {"type": "sqlite", "path": ":memory:"}
    handler = SQLiteHandler(config)
    yield handler
    await handler.cleanup()
```

## Best Practices

1. **Test Coverage**: Maintain at least 80% code coverage
2. **Isolated Tests**: Ensure tests don't depend on the state of other tests
3. **Resource Cleanup**: Use fixture teardown mechanisms to clean up resources
4. **Mock External Dependencies**: Use unittest.mock to mock external dependencies
5. **Test Error Cases**: Test error handling and edge cases
6. **Parameterized Tests**: Use pytest.mark.parametrize to test multiple inputs

## SonarCloud Integration

Test results are automatically uploaded to SonarCloud for analysis. SonarCloud checks:

- Code coverage
- Test success rate
- Code quality issues
- Security vulnerabilities

You can view test results and code quality reports on the [SonarCloud dashboard](https://sonarcloud.io/dashboard?id=donghao1393_mcp-dbutils).