# SQLite 示例

*[English](../../en/examples/sqlite-examples.md) | 中文 | [Français](../../fr/examples/sqlite-examples.md) | [Español](../../es/examples/sqlite-examples.md) | [العربية](../../ar/examples/sqlite-examples.md) | [Русский](../../ru/examples/sqlite-examples.md)*

本文档提供了使用 MCP 数据库工具操作 SQLite 数据库的实用示例。

## 基本配置

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
```

## 常见操作

### 列出表格

**您**："列出我的 SQLite 数据库中的所有表。"

**AI**："以下是您的 SQLite 数据库中的表：
- users（用户）
- products（产品）
- orders（订单）
- categories（类别）"

### 查看表结构

**您**："显示 users 表的结构。"

**AI**："users 表的结构如下：
- id (INTEGER, PRIMARY KEY)
- username (TEXT, NOT NULL)
- email (TEXT, NOT NULL, UNIQUE)
- created_at (TIMESTAMP)
- last_login (TIMESTAMP)
- status (TEXT)"

### 基本查询

**您**："显示按最后登录日期排序的前 5 名用户。"

**AI**："以下是按最后登录日期排序的前 5 名用户：

| id | username | email | last_login |
|----|----------|-------|------------|
| 42 | johndoe | john@example.com | 2023-11-25 14:32:15 |
| 17 | janedoe | jane@example.com | 2023-11-24 09:45:22 |
| 31 | bobsmith | bob@example.com | 2023-11-23 18:12:05 |
| 8 | alicejones | alice@example.com | 2023-11-22 11:30:47 |
| 53 | mikebrown | mike@example.com | 2023-11-21 16:08:33 |"

## 高级查询

### 表连接

**您**："显示最近 3 个订单及其用户信息。"

**AI**："以下是最近 3 个订单及其用户信息：

| order_id | order_date | username | email | total_amount |
|----------|------------|----------|-------|--------------|
| 1042 | 2023-11-25 | johndoe | john@example.com | ¥125.99 |
| 1041 | 2023-11-24 | alicejones | alice@example.com | ¥89.50 |
| 1040 | 2023-11-23 | bobsmith | bob@example.com | ¥212.75 |"

### 聚合函数

**您**："每个类别的平均订单金额是多少？"

**AI**："以下是每个类别的平均订单金额：

| category | average_amount |
|----------|----------------|
| Electronics（电子产品） | ¥245.75 |
| Clothing（服装） | ¥78.30 |
| Books（图书） | ¥32.50 |
| Home & Kitchen（家居与厨房） | ¥124.90 |
| Sports & Outdoors（运动与户外） | ¥156.25 |"

## 性能分析

### 查询执行计划

**您**："解释这个查询的执行计划：SELECT * FROM orders WHERE user_id = 42"

**AI**："该查询的执行计划：
```
QUERY PLAN
------------------------------------------------------------
SEARCH TABLE orders USING INDEX idx_user_id (user_id=?)
```

此查询使用 `idx_user_id` 索引高效地查找 user_id 为 42 的订单。"

### 表统计信息

**您**："获取 orders 表的统计信息。"

**AI**："orders 表的统计信息：
- 行数：1,245
- 大小：2.3 MB
- 索引：3 个（主键、idx_user_id、idx_order_date）
- 平均行长度：1.9 KB"

## 使用 SQLite 特有功能

### 使用 FTS（全文搜索）

**您**："搜索包含'无线耳机'的产品。"

**AI**："以下是匹配'无线耳机'的产品：

| product_id | name | description | price |
|------------|------|-------------|-------|
| 123 | 高级无线耳机 | 带有 30 小时电池续航的降噪无线耳机 | ¥199.99 |
| 145 | 运动无线耳机 | 防水运动无线耳机 | ¥89.99 |
| 187 | 经济型无线耳机 | 音质优良的经济实惠无线耳机 | ¥49.99 |"

### 使用 JSON 函数

**您**："显示偏好设置中包含'premium'的用户。"

**AI**："以下是偏好设置中包含'premium'的用户：

| id | username | preferences |
|----|----------|-------------|
| 42 | johndoe | {\"subscription\": \"premium\", \"theme\": \"dark\"} |
| 17 | janedoe | {\"subscription\": \"premium\", \"theme\": \"light\"} |
| 53 | mikebrown | {\"subscription\": \"premium\", \"theme\": \"auto\"} |"

## 故障排除

### 常见问题

1. **文件未找到**
   - 确保 SQLite 数据库文件的路径正确
   - 检查文件权限
   - 验证文件是否存在

2. **数据库锁定**
   - SQLite 一次只允许一个写入者
   - 确保没有其他进程正在写入数据库
   - 考虑使用 WAL 模式以获得更好的并发性

3. **性能问题**
   - 为经常查询的列添加索引
   - 使用 EXPLAIN QUERY PLAN 识别慢查询
   - 考虑对重复查询使用预处理语句