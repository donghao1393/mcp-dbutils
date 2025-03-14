# 代码风格指南

本项目使用Ruff进行代码风格检查和格式化，确保代码质量和一致性。

## 代码风格规范

### 基本规则

1. **行长度**：最大88个字符
2. **缩进**：使用4个空格（不使用制表符）
3. **引号**：使用双引号作为字符串引号
4. **命名规范**：
   - 类名：使用CamelCase（如`DatabaseHandler`）
   - 函数和变量：使用snake_case（如`execute_query`）
   - 常量：使用大写加下划线（如`MAX_CONNECTIONS`）
   - 私有方法和属性：使用单下划线前缀（如`_connect`）

### 导入规则

1. 导入顺序：
   - 标准库
   - 第三方库
   - 本地应用/库

2. 每个导入组之间应有一个空行

### 代码组织

1. 类定义之间应有两个空行
2. 方法定义之间应有一个空行
3. 相关的代码应该分组在一起

## Ruff规则集

本项目使用以下Ruff规则集：

- `E`: pycodestyle错误
- `F`: pyflakes
- `I`: isort
- `N`: pep8-naming
- `UP`: pyupgrade
- `B`: flake8-bugbear
- `C4`: flake8-comprehensions
- `SIM`: flake8-simplify
- `T20`: flake8-print

## 本地开发

### 安装工具

```bash
# 安装Ruff
uv pip install ruff

# 安装pre-commit
uv pip install pre-commit
pre-commit install
```

### 使用方法

#### 代码检查

```bash
# 检查整个项目
ruff check .

# 自动修复问题
ruff check --fix .
```

#### 代码格式化

```bash
# 检查格式
ruff format --check .

# 自动格式化
ruff format .
```

#### 使用pre-commit

项目已配置pre-commit钩子，提交代码时会自动运行Ruff检查和格式化。

```bash
# 手动运行pre-commit
pre-commit run --all-files
```

## CI/CD集成

GitHub Actions会在每次推送和PR时自动运行Ruff检查和格式化，确保代码符合规范。

## 常见问题

### 如何忽略特定规则？

在代码中使用注释忽略特定行的规则：

```python
# 忽略整行
some_code_here  # noqa

# 忽略特定规则
some_code_here  # noqa: E501

# 忽略多个规则
some_code_here  # noqa: E501, F401
```

### 如何在项目级别忽略规则？

在`pyproject.toml`的`[tool.ruff]`部分添加：

```toml
ignore = ["E501"]
```

### 如何处理第三方库导入问题？

如果第三方库导入顺序有问题，可以在`pyproject.toml`中配置：

```toml
[tool.ruff.isort]
known-third-party = ["third_party_lib"]
```
