# 开发指南

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
我们使用Ruff进行代码风格检查和格式化：

所有代码必须遵循我们的风格指南：
- 行长度：88个字符
- 缩进：4个空格
- 引号：双引号
- 命名：PEP8约定

有关详细指南，请参阅[STYLE_GUIDE.md](../../../docs/STYLE_GUIDE.md)。

### 本地开发
要在本地检查代码质量：
1. 运行带覆盖率的测试：
   ```bash
   pytest --cov=src/mcp_dbutils --cov-report=xml:coverage.xml tests/
   ```
2. 在IDE中使用SonarLint及早发现问题
3. 在PR评论中查看SonarCloud分析结果
4. 运行Ruff进行代码风格检查：
   ```bash
   # 安装Ruff
   uv pip install ruff

   # 检查代码风格
   ruff check .

   # 格式化代码
   ruff format .
   ```
5. 使用pre-commit钩子进行自动检查：
   ```bash
   # 安装pre-commit
   uv pip install pre-commit
   pre-commit install
   ```

## 版本更新

MCP数据库工具会定期发布更新，包含新功能、性能改进和错误修复。大多数情况下，更新过程由MCP客户端自动管理，您无需手动干预。

### 获取最新版本

- **使用MCP客户端**：大多数MCP客户端（如Claude Desktop、Cursor等）会自动更新到最新版本

- **手动检查更新**：
  - 访问[GitHub仓库](https://github.com/donghao1393/mcp-dbutils)查看最新版本
  - 阅读[发布说明](https://github.com/donghao1393/mcp-dbutils/releases)了解新功能和变更

- **问题报告**：
  - 如果您在更新后遇到问题，请[提交issue](https://github.com/donghao1393/mcp-dbutils/issues)