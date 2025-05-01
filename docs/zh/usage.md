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

列出配置中的所有可用数据库连接，包括数据库类型、主机、端口和数据库名称等详细信息，同时隐藏密码等敏感信息。可选参数check_status允许验证每个连接是否可用，但这可能会增加响应时间。当您需要了解可用的数据库资源或诊断连接问题时使用此工具。

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

列出指定数据库连接中的所有表，包括表名、URI和可用的表描述。结果按数据库类型分组并清晰标记，便于快速识别。当您需要了解数据库结构或查找特定表时使用此工具。只在允许的连接范围内工作。

**示例交互**：

**您**："列出我的 postgres 数据库中的所有表。"

**AI**："我来为您查看。以下是您的 postgres 数据库中的表：
- customers（客户）
- products（产品）
- orders（订单）
- inventory（库存）
- employees（员工）"

### dbutils-run-query

在指定数据库连接上执行只读SQL查询。为确保安全，仅支持SELECT语句。查询结果以结构化格式返回，包含列名和数据行。支持复杂查询，包括JOIN、GROUP BY、ORDER BY和聚合函数。当您需要分析数据、验证假设或提取特定信息时使用此工具。查询执行受到资源限制和超时保护，以防止过度消耗系统资源。

**示例交互**：

**您**："查询 customers 表中过去 30 天内注册的客户数量。"

**AI**："让我为您查询。根据数据，过去 30 天内有 42 位新客户注册。"

### dbutils-describe-table

获取表结构的详细信息，包括列名、数据类型、是否可为空、默认值和注释。结果格式化为易读的层次结构，清晰显示每列的所有属性。当您需要深入了解表结构、分析数据模型或准备查询时使用此工具。支持所有主要数据库类型，并保持一致的输出格式。

**示例交互**：

**您**："描述 customers 表的结构。"

**AI**："customers 表的结构如下：
- id: 整数, 主键, 非空, 自增
- name: 字符串(100), 非空
- email: 字符串(100), 唯一, 非空
- registration_date: 日期, 非空, 默认值: 当前日期
- status: 枚举('active','inactive','suspended'), 默认值: 'active'
- last_login: 时间戳, 可为空"

### dbutils-get-ddl

获取创建指定表的完整DDL（数据定义语言）语句。返回原始的CREATE TABLE语句，包括所有列定义、约束、索引和表选项。当您需要理解表的完整结构、复制表结构或进行数据库迁移时，此工具非常有用。DDL语句格式会根据数据库类型而有所不同。

**示例交互**：

**您**："获取 products 表的 DDL。"

**AI**："products 表的 DDL 语句如下：
```sql
CREATE TABLE products (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  category_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_category (category_id),
  CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```"

### dbutils-get-stats

获取表的统计信息，包括估计行数、平均行长度、数据大小、索引大小和列信息。这些统计数据对于了解表的大小、增长趋势和存储特性非常有价值。当您需要进行容量规划、性能优化或数据库维护时使用此工具。统计信息的精确度和可用性可能因数据库类型而异。

**示例交互**：

**您**："获取 products 表的统计信息。"

**AI**："products 表的统计信息如下：
- 总行数：1,245
- 表大小：2.3 MB
- 列统计：
  * product_id：唯一值 1,245 个
  * category：共 8 个不同类别
  * price：平均价格 $45.99，最低 $5.99，最高 $299.99"

### dbutils-list-indexes

列出指定表上的所有索引，包括索引名称、类型（唯一/非唯一）、索引方法（如B树）和包含的列。结果按索引名称分组，清晰显示多列索引的结构。当您需要优化查询性能、理解表的访问模式或诊断性能问题时使用此工具。

**示例交互**：

**您**："列出 orders 表的所有索引。"

**AI**："orders 表有以下索引：
1. **PRIMARY** (主键索引)
   - 列: order_id
   - 类型: 唯一索引
   - 方法: B树

2. **idx_customer** (普通索引)
   - 列: customer_id
   - 类型: 非唯一索引
   - 方法: B树

3. **idx_order_date** (普通索引)
   - 列: order_date
   - 类型: 非唯一索引
   - 方法: B树

4. **idx_status_created** (复合索引)
   - 列: status, created_at
   - 类型: 非唯一索引
   - 方法: B树"

### dbutils-list-constraints

列出表上的所有约束，包括主键、外键、唯一约束和检查约束。结果按约束类型分组，清晰显示约束名称和涉及的列。对于外键约束，还会显示引用的表和列。当您需要理解数据完整性规则、表间关系或数据验证逻辑时使用此工具。

**示例交互**：

**您**："显示 orders 表的约束条件。"

**AI**："orders 表有以下约束条件：
- 主键：order_id
- 外键：customer_id 引用 customers(id)
- 外键：product_id 引用 products(id)
- 检查约束：order_amount > 0"

### dbutils-explain-query

获取SQL查询的执行计划，显示数据库引擎将如何处理查询。返回详细的执行计划，包括访问方法、连接类型、排序操作和估计成本。同时提供实际执行统计（如可用）。当您需要优化查询性能、理解复杂查询的行为或诊断慢查询时使用此工具。执行计划格式会根据数据库类型而有所不同。

**示例交互**：

**您**："解释这个查询的执行计划：SELECT * FROM orders WHERE customer_id = 123"

**AI**："该查询的执行计划如下：
1. 索引扫描：使用 customer_id_idx 索引
2. 估计成本：12.5
3. 估计行数：8
4. 过滤条件：customer_id = 123"

### dbutils-get-performance

获取数据库连接的性能指标，包括查询计数、平均执行时间、内存使用情况和错误统计。这些指标反映了当前会话的资源使用情况，有助于监控和优化数据库操作。当您需要评估查询效率、识别性能瓶颈或监控资源使用时使用此工具。

**示例交互**：

**您**："获取数据库的性能指标。"

**AI**："当前数据库性能指标：
- 查询执行时间：平均 45ms
- 缓存命中率：87%
- 活跃连接数：3
- 最近错误率：0.2%"

### dbutils-analyze-query

分析SQL查询的性能特性，提供执行计划、实际执行时间和优化建议。工具会执行查询（仅限SELECT语句）并测量性能，然后基于结果提供具体的优化建议，如添加索引、重构连接条件或调整查询结构。当您需要提高查询性能、理解性能瓶颈或学习查询优化技术时使用此工具。

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