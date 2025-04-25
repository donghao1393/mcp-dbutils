# 开发指南

*[English](../../en/technical/development.md) | 中文 | [Français](../../fr/technical/development.md) | [Español](../../es/technical/development.md) | [العربية](../../ar/technical/development.md) | [Русский](../../ru/technical/development.md)*

本文档提供了有关开发流程、代码标准和为 MCP 数据库工具项目做贡献的最佳实践的详细信息。

## 代码质量

### 质量门禁
我们使用SonarCloud维护高代码质量标准。所有拉取请求必须通过以下质量门禁：

- 代码覆盖率：≥ 80%
- 代码质量：
  * 无阻断或严重问题
  * 主要问题少于10个
  * 代码重复率 < 3%
- 安全性：
  * 无安全漏洞
  * 无安全热点

### 自动化检查
我们的CI/CD流程自动执行：
1. 完整测试套件执行
2. 代码覆盖率分析
3. SonarCloud静态代码分析
4. 质量门禁验证

不满足这些标准的拉取请求将自动被阻止合并。

### 代码风格

我们使用Ruff进行代码风格检查和格式化，确保代码质量和一致性。

#### 基本规则

1. **行长度**：最大88个字符
2. **缩进**：使用4个空格（不使用制表符）
3. **引号**：使用双引号作为字符串引号
4. **命名规范**：
   - 类名：使用CamelCase（如`DatabaseHandler`）
   - 函数和变量：使用snake_case（如`execute_query`）
   - 常量：使用大写加下划线（如`MAX_CONNECTIONS`）
   - 私有方法和属性：使用单下划线前缀（如`_connect`）

#### 导入规则

1. 导入顺序：
   - 标准库
   - 第三方库
   - 本地应用/库

2. 每个导入组之间应有一个空行

#### 代码组织

1. 类定义之间应有两个空行
2. 方法定义之间应有一个空行
3. 相关的代码应该分组在一起

#### Ruff规则集

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

### 本地开发

#### 安装工具

```bash
# 安装Ruff
uv pip install ruff

# 安装pre-commit
uv pip install pre-commit
pre-commit install
```

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

#### 测试与覆盖率

```bash
# 运行带覆盖率的测试
pytest --cov=src/mcp_dbutils --cov-report=xml:coverage.xml tests/
```

#### 其他开发工具

1. 在IDE中使用SonarLint及早发现问题
2. 在PR评论中查看SonarCloud分析结果

### 常见问题

#### 如何忽略特定规则？

在代码中使用注释忽略特定行的规则：

```python
# 忽略整行
some_code_here  # noqa

# 忽略特定规则
some_code_here  # noqa: E501

# 忽略多个规则
some_code_here  # noqa: E501, F401
```

#### 如何在项目级别忽略规则？

在`pyproject.toml`的`[tool.ruff]`部分添加：

```toml
ignore = ["E501"]
```

#### 如何处理第三方库导入问题？

如果第三方库导入顺序有问题，可以在`pyproject.toml`中配置：

```toml
[tool.ruff.isort]
known-third-party = ["third_party_lib"]
```

### CI/CD 集成

GitHub Actions 会在每次推送和 PR 时自动运行 Ruff 检查和格式化，确保代码符合规范。

#### 自动化流程

每个 PR 会触发以下自动化检查：

1. **代码风格检查**：使用 Ruff 验证代码是否符合项目风格规范
2. **单元测试**：运行所有测试确保功能正常
3. **代码覆盖率**：确保测试覆盖率达到要求
4. **SonarCloud 分析**：进行深度代码质量和安全性分析

#### 如何查看 CI 结果

1. 在 GitHub PR 页面查看 "Checks" 标签页
2. 点击具体的检查查看详细信息
3. 对于 SonarCloud 分析，可以点击链接查看完整报告

## 版本更新

MCP数据库工具会定期发布更新，包含新功能、性能改进和错误修复。大多数情况下，更新过程由MCP客户端自动管理，您无需手动干预。

### 获取最新版本

- **使用MCP客户端**：大多数MCP客户端（如Claude Desktop、Cursor等）会自动更新到最新版本

- **手动检查更新**：
  - 访问[GitHub仓库](https://github.com/donghao1393/mcp-dbutils)查看最新版本
  - 阅读[发布说明](https://github.com/donghao1393/mcp-dbutils/releases)了解新功能和变更

- **问题报告**：
  - 如果您在更新后遇到问题，请[提交issue](https://github.com/donghao1393/mcp-dbutils/issues)