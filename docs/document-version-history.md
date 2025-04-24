# 文档版本历史

本文件记录了 MCP 数据库工具文档的版本历史和重要更新。

## 版本命名规则

文档版本使用以下格式：`vX.Y.Z`，其中：

- `X`：主版本号，表示重大结构或内容变更
- `Y`：次版本号，表示功能添加或重要内容更新
- `Z`：修订版本号，表示错误修复或小幅内容改进

## 版本历史

### v1.0.0 (2024-04-24)

**主要更新**：
- 完成文档重组，按照语言（中英文）和文档类型进行分类
- 创建了详细的 PostgreSQL 和 MySQL 示例文档
- 整合 STYLE_GUIDE.md 到开发指南中
- 将 technical-guide.md 的内容分解到各个技术文档中
- 处理 SonarCloud 集成文档，创建中英文版本
- 更新 README 中的文档链接

**新增文档**：
- docs/zh/examples/postgresql-examples.md
- docs/zh/examples/mysql-examples.md
- docs/en/examples/postgresql-examples.md
- docs/en/examples/mysql-examples.md
- docs/zh/technical/sonarcloud-integration.md
- docs/en/technical/sonarcloud-integration.md

**删除文档**：
- docs/STYLE_GUIDE.md
- docs/technical-guide.md
- docs/configuration-examples.md
- docs/sonarcloud-ai-integration.md

### v1.1.0 (2024-04-25)

**主要更新**：
- 添加平台特定安装指南，针对不同操作系统提供详细安装说明
- 创建高级 LLM 交互示例文档，展示与各类 LLM 的交互潜力
- 进行文档一致性检查，确保所有文档符合统一标准
- 实施文档版本控制，添加版本信息和更新历史
- 更新 README 中的文档链接

**新增文档**：
- docs/zh/installation-platform-specific.md
- docs/en/installation-platform-specific.md
- docs/zh/examples/advanced-llm-interactions.md
- docs/en/examples/advanced-llm-interactions.md
- docs/document-consistency-check.md
- docs/document-version-history.md

## 文档维护指南

### 更新文档版本

当对文档进行更新时，请遵循以下步骤：

1. 确定更新的性质（主要结构变更、功能添加或错误修复）
2. 根据更新性质，增加相应的版本号
3. 在本文件中添加新版本的条目，记录主要更新内容和变更的文件
4. 在更新的文档顶部更新版本号和最后更新日期

### 文档版本与软件版本的关系

文档版本与软件版本保持独立，但应在文档中明确说明其适用的软件版本范围。当软件发布新版本时，应相应地更新文档，并在版本历史中注明。
