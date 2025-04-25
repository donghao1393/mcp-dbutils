# 使用指南

*[English](../en/usage.md) | 中文 | [Français](../fr/usage.md) | [Español](../es/usage.md) | [العربية](../ar/usage.md) | [Русский](../ru/usage.md)*

本文档提供了 MCP 数据库工具的详细使用说明，帮助您充分利用其功能与 AI 进行数据分析。

## 基本操作流程

MCP 数据库工具的基本操作流程如下：

1. **配置数据库连接**：在 `config.yaml` 文件中定义您的数据库连接
2. **启动 MCP 服务**：通过 AI 客户端配置启动服务
3. **与 AI 交互**：使用自然语言向 AI 提问关于您数据库的问题
4. **查看结果**：AI 将执行必要的查询并以易于理解的方式呈现结果

## 可用工具

MCP 数据库工具提供了几个您的 AI 可以使用的工具：

### dbutils-list-connections

列出配置中定义的所有可用数据库连接。

**示例交互**：

**您**："我有哪些可用的数据库连接？"

**AI**："我来为您查看可用的数据库连接。以下是我找到的连接：

1. **postgres-db**
   - 类型：PostgreSQL
   - 主机：localhost
   - 数据库：analytics
   - 用户：analyst

2. **sqlite-db**
   - 类型：SQLite
   - 路径：/path/to/database.db

3. **mysql-db**
   - 类型：MySQL
   - 主机：db.example.com
   - 数据库：customer_data
   - 用户：reader"

### dbutils-list-tables

列出指定数据库中的所有表。

**示例交互**：

**您**："列出我的 postgres 数据库中的所有表。"

**AI**："我来为您查看。以下是您的 postgres 数据库中的表：
- customers（客户）
- products（产品）
- orders（订单）
- inventory（库存）
- employees（员工）"

### dbutils-run-query

在指定数据库上执行 SQL 查询（仅限 SELECT 操作）。

**示例交互**：

**您**："查询 customers 表中过去 30 天内注册的客户数量。"

**AI**："让我为您查询。根据数据，过去 30 天内有 42 位新客户注册。"

### dbutils-get-stats

获取表的统计信息，如行数、大小和列统计数据。

**示例交互**：

**您**："获取 products 表的统计信息。"

**AI**："products 表的统计信息如下：
- 总行数：1,245
- 表大小：2.3 MB
- 列统计：
  * product_id：唯一值 1,245 个
  * category：共 8 个不同类别
  * price：平均价格 $45.99，最低 $5.99，最高 $299.99"

### dbutils-list-constraints

列出表的约束条件，如主键、外键等。

**示例交互**：

**您**："显示 orders 表的约束条件。"

**AI**："orders 表有以下约束条件：
- 主键：order_id
- 外键：customer_id 引用 customers(id)
- 外键：product_id 引用 products(id)
- 检查约束：order_amount > 0"

### dbutils-explain-query

获取查询执行计划和成本估算。

**示例交互**：

**您**："解释这个查询的执行计划：SELECT * FROM orders WHERE customer_id = 123"

**AI**："该查询的执行计划如下：
1. 索引扫描：使用 customer_id_idx 索引
2. 估计成本：12.5
3. 估计行数：8
4. 过滤条件：customer_id = 123"

### dbutils-get-performance

获取数据库性能指标。

**示例交互**：

**您**："获取数据库的性能指标。"

**AI**："当前数据库性能指标：
- 查询执行时间：平均 45ms
- 缓存命中率：87%
- 活跃连接数：3
- 最近错误率：0.2%"

### dbutils-analyze-query

分析 SQL 查询的性能并提供优化建议。

**示例交互**：

**您**："分析这个查询：SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id WHERE order_date > '2023-01-01'"

**AI**："查询分析结果：
1. 性能问题：使用了 SELECT *，获取了不必要的列
2. 缺少索引：order_date 列没有索引
3. 优化建议：
   - 只选择需要的列
   - 在 order_date 列上添加索引
   - 考虑添加 LIMIT 子句限制结果数量"

## 常见使用场景

### 1. 数据探索

**您**："我想了解我的数据库结构。"

**AI**："我可以帮您探索数据库结构。让我列出所有表，然后您可以选择一个表进一步了解其结构。"

**您**："好的，列出所有表。"

**AI**："您的数据库包含以下表：
- customers
- products
- orders
- inventory
- employees

您想了解哪个表的详细结构？"

**您**："请告诉我 customers 表的结构。"

**AI**："customers 表的结构如下：
- id (integer, 主键)
- name (varchar(100), 非空)
- email (varchar(100), 唯一, 非空)
- registration_date (date, 非空)
- last_login (timestamp)
- status (enum: 'active', 'inactive', 'suspended')"

### 2. 数据分析

**您**："分析过去 6 个月的销售趋势。"

**AI**："我将分析过去 6 个月的销售趋势。让我执行一些查询..."

[AI 执行多个查询，分析销售数据]

**AI**："根据过去 6 个月的数据分析：
1. 总销售额：$1,245,678，比上一个 6 个月增长 15%
2. 最畅销产品：Product X，占总销售额的 23%
3. 销售高峰期：周五和周六，占总销售额的 45%
4. 客户留存率：78%，比上一个 6 个月提高 5%"

### 3. 跨数据库分析

**您**："比较生产数据库和测试数据库中的 users 表结构差异。"

**AI**："我将比较两个数据库中的 users 表结构..."

[AI 查询两个数据库的表结构]

**AI**："生产数据库和测试数据库的 users 表结构差异：
1. 生产数据库多了 'last_login_ip' 列 (varchar(45))
2. 测试数据库的 'email' 列没有唯一约束
3. 生产数据库有额外的索引：idx_user_status
4. 测试数据库缺少外键约束：fk_user_role"

## 最佳实践

### 查询优化

1. **限制结果集大小**：使用 LIMIT 子句限制返回的行数
2. **只选择必要的列**：避免使用 SELECT *
3. **使用索引列**：在 WHERE 子句中使用有索引的列
4. **避免复杂计算**：将复杂计算移至应用层

### 安全建议

1. **使用只读账户**：为 AI 访问创建专用的只读数据库账户
2. **限制表访问**：只授予对必要表的访问权限
3. **使用 SSL/TLS**：对远程数据库连接启用加密
4. **定期更新密码**：定期更改数据库密码

### 性能优化

1. **连接池配置**：根据您的使用情况调整连接池大小
2. **查询超时设置**：设置合理的查询超时时间
3. **结果缓存**：对频繁查询的数据考虑使用缓存
4. **监控性能**：定期检查性能指标，识别潜在问题

## 故障排除

如果您在使用过程中遇到问题，请参考[安装指南](installation.md)中的故障排除部分，或查看[技术文档](technical/architecture.md)获取更多详细信息。