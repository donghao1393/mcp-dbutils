# 高级 LLM 交互示例

*[English](../../en/examples/advanced-llm-interactions.md) | 中文 | [Français](../../fr/examples/advanced-llm-interactions.md) | [Español](../../es/examples/advanced-llm-interactions.md) | [العربية](../../ar/examples/advanced-llm-interactions.md) | [Русский](../../ru/examples/advanced-llm-interactions.md)*

本文档展示了 MCP 数据库工具与各类大型语言模型（LLM）的高级交互示例，帮助您充分发挥数据分析潜力。

## 目录

- [使用 DeepSeek 生成数据分析报告](#使用-deepseek-生成数据分析报告)
- [在 Claude Desktop 中生成 BI 面板](#在-claude-desktop-中生成-bi-面板)
- [使用 GPT-4 进行数据异常检测](#使用-gpt-4-进行数据异常检测)
- [与 Gemini 协作进行预测分析](#与-gemini-协作进行预测分析)
- [使用 Llama 3 进行自然语言数据查询](#使用-llama-3-进行自然语言数据查询)

## 使用 DeepSeek 生成数据分析报告

DeepSeek 模型在数据分析和代码生成方面表现出色。以下示例展示如何使用 DeepSeek 生成完整的 HTML 数据分析报告。

### 步骤 1：准备数据查询

首先，使用 MCP 数据库工具查询所需数据：

```
您：能否帮我查询过去 12 个月的销售数据，按月份和产品类别分组？

AI：我来帮您查询这些数据。我将使用 dbutils-run-query 工具执行查询。

查询结果如下：

月份      | 产品类别   | 销售额    | 订单数量 | 平均订单金额
---------|-----------|----------|---------|------------
2023-01  | 电子产品   | ¥245,670 | 432     | ¥568.68
2023-01  | 家居用品   | ¥156,890 | 689     | ¥227.71
...
2023-12  | 食品饮料   | ¥98,320  | 1,290   | ¥76.22
```

### 步骤 2：请求 DeepSeek 生成分析报告

将查询结果提供给 DeepSeek，并请求生成分析报告：

```
您：请根据这些销售数据生成一个详细的 HTML 分析报告，包含趋势分析、季节性分析和产品类别对比。报告应包含交互式图表和关键发现。

DeepSeek：我将为您生成一个详细的 HTML 分析报告。以下是完整的 HTML 代码：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>销售数据分析报告 - 2023年</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }

        /* 更多样式... */
    </style>
</head>
<body>
    <header>
        <h1>销售数据分析报告</h1>
        <p class="subtitle">2023年1月 - 2023年12月</p>
    </header>

    <section id="executive-summary">
        <h2>执行摘要</h2>
        <div class="summary-cards">
            <div class="card">
                <h3>总销售额</h3>
                <p class="highlight">¥2,845,670</p>
                <p class="trend positive">↑ 同比增长 15.3%</p>
            </div>
            <!-- 更多卡片... -->
        </div>
        <div class="key-findings">
            <h3>关键发现</h3>
            <ul>
                <li>电子产品类别贡献了最高销售额，占总销售额的 42%</li>
                <li>第四季度销售额较第一季度增长了 28.5%</li>
                <li>家居用品类别在假日季节（10-12月）表现最佳</li>
            </ul>
        </div>
    </section>

    <!-- 更多报告内容... -->

    <script>
        // 月度销售趋势图表
        const monthlySalesCtx = document.getElementById('monthly-sales-chart').getContext('2d');
        const monthlySalesChart = new Chart(monthlySalesCtx, {
            type: 'line',
            data: {
                labels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
                datasets: [
                    {
                        label: '电子产品',
                        data: [245670, 234560, 256780, 267890, 278900, 289760, 301230, 312450, 325670, 345670, 367890, 389760],
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    // 更多数据集...
                ]
            },
            // 更多配置...
        });

        // 更多图表...
    </script>
</body>
</html>
```

这个 HTML 报告包含了完整的销售数据分析，包括交互式图表、趋势分析和关键发现。您可以将此代码保存为 HTML 文件并在浏览器中打开查看。
```

### 步骤 3：保存并使用报告

将生成的 HTML 代码保存为文件，并在浏览器中打开：

```bash
echo '<!DOCTYPE html>...' > sales_analysis_report.html
open sales_analysis_report.html  # 在 macOS 上
# 或 xdg-open sales_analysis_report.html  # 在 Linux 上
# 或 start sales_analysis_report.html  # 在 Windows 上
```

## 在 Claude Desktop 中生成 BI 面板

Claude Desktop 支持通过 artifact 输出生成可视化内容。以下示例展示如何使用 Claude 生成交互式 BI 面板。

### 步骤 1：准备数据

使用 MCP 数据库工具获取所需数据：

```
您：请帮我查询客户细分数据，包括客户 ID、购买频率、平均消费金额和最近一次购买日期。

AI：我将为您查询客户细分数据。

查询结果如下：

客户ID | 购买频率 | 平均消费金额 | 最近购买日期
-------|---------|------------|-------------
1001   | 12      | ¥1,245.67  | 2023-12-15
1002   | 3       | ¥567.89    | 2023-10-23
...
1100   | 8       | ¥876.54    | 2023-11-30
```

### 步骤 2：请求 Claude 生成 BI 面板

将数据提供给 Claude，并请求生成 BI 面板：

```
您：请根据这些客户数据生成一个交互式 BI 面板，用于客户细分分析。面板应包含 RFM 分析、客户价值分布和客户生命周期阶段。请将结果作为 HTML artifact 输出。

Claude：我将为您创建一个交互式 BI 面板用于客户细分分析。这个面板将包含 RFM 分析、客户价值分布和客户生命周期阶段的可视化。

以下是基于您提供的数据创建的 BI 面板：

[Claude 会生成一个 HTML artifact，包含交互式 BI 面板]
```

### 步骤 3：保存并使用 BI 面板

Claude 生成的 HTML artifact 可以直接下载并在浏览器中打开。面板通常包含：

- RFM (Recency, Frequency, Monetary) 分析图表
- 客户价值分布热图
- 客户生命周期阶段漏斗图
- 交互式筛选器和控件

## 使用 GPT-4 进行数据异常检测

GPT-4 擅长识别数据中的模式和异常。以下示例展示如何使用 GPT-4 进行数据异常检测。

### 步骤 1：获取时间序列数据

使用 MCP 数据库工具获取时间序列数据：

```
您：请帮我查询过去 30 天的系统登录数据，包括日期、时间、用户 ID 和登录 IP。

AI：我将为您查询系统登录数据。

查询结果如下：

日期       | 时间     | 用户ID | 登录IP
----------|---------|-------|---------------
2023-12-01 | 08:23:45 | user_a | 192.168.1.101
2023-12-01 | 09:15:32 | user_b | 192.168.1.102
...
2023-12-30 | 22:45:12 | user_a | 45.67.89.123
```

### 步骤 2：请求 GPT-4 进行异常检测

将数据提供给 GPT-4，并请求进行异常检测：

```
您：请分析这些登录数据，识别任何可能的安全异常，如不寻常的登录时间、异常的 IP 地址变化或可疑的登录模式。

GPT-4：我已分析了您提供的登录数据，发现了以下潜在安全异常：

1. **不寻常的登录时间**：
   - user_a 通常在工作时间（8:00-18:00）登录，但在 12月15日 凌晨 3:27 有一次登录记录
   - user_c 在 12月10日 和 12月11日 连续两天在午夜 00:15 左右登录

2. **异常的 IP 地址变化**：
   - user_b 通常从 192.168.1.x 网段登录，但在 12月20日 从 78.34.56.89（位于俄罗斯）登录
   - user_a 在 12月30日 22:45:12 从 45.67.89.123 登录，与其通常的 IP 范围不符

3. **可疑的登录模式**：
   - user_d 在 12月25日 的 10分钟内从3个不同的 IP 地址登录
   - user_e 和 user_f 显示完全相同的登录模式（相同时间、相似 IP），可能表明账户共享或自动化脚本

4. **地理位置异常**：
   - user_b 在 12月19日 16:30:45 从美国 IP 登录，而在 12月20日 02:15:33 从俄罗斯 IP 登录，物理上不可能在这么短时间内完成的旅行

建议采取的措施：
1. 对 user_a、user_b 和 user_d 的账户实施临时锁定并要求密码重置
2. 调查 user_e 和 user_f 的账户共享情况
3. 实施双因素认证，特别是对管理员账户
4. 设置基于时间和地理位置的登录规则
```

## 与 Gemini 协作进行预测分析

Gemini 在处理结构化数据和预测分析方面表现出色。以下示例展示如何使用 Gemini 进行销售预测。

### 步骤 1：获取历史销售数据

使用 MCP 数据库工具获取历史销售数据：

```
您：请帮我查询过去 24 个月的月度销售数据，按产品类别分组。

AI：我将为您查询过去 24 个月的月度销售数据。

查询结果如下：

年月     | 产品类别   | 销售额    | 单位销量
--------|-----------|----------|--------
2022-01 | 电子产品   | ¥198,450 | 324
2022-01 | 家居用品   | ¥123,670 | 567
...
2023-12 | 食品饮料   | ¥98,320  | 1,290
```

### 步骤 2：请求 Gemini 进行预测分析

将数据提供给 Gemini，并请求进行预测分析：

```
您：请基于这些历史销售数据，预测未来 6 个月的销售趋势。请考虑季节性因素、增长趋势和产品类别间的相关性。

Gemini：基于您提供的 24 个月历史销售数据，我已进行了时间序列分析并生成了未来 6 个月的销售预测。以下是我的分析结果：

## 预测概述

我使用了 SARIMA (季节性自回归综合移动平均) 模型进行预测，该模型考虑了季节性模式、整体趋势和产品类别间的相关性。

## 未来 6 个月销售预测

| 年月     | 产品类别   | 预测销售额  | 预测单位销量 | 预测区间 (95% 置信度) |
|---------|-----------|------------|------------|---------------------|
| 2024-01 | 电子产品   | ¥267,830   | 437        | ¥245,670 - ¥289,990 |
| 2024-01 | 家居用品   | ¥168,450   | 734        | ¥154,320 - ¥182,580 |
| ...     | ...       | ...        | ...        | ...                 |
| 2024-06 | 食品饮料   | ¥112,780   | 1,456      | ¥98,540 - ¥127,020  |

## 关键预测发现

1. **季节性模式**：
   - 电子产品在假日季节（11月-1月）销售额预计增长 35%
   - 家居用品在春季（3月-5月）预计有 22% 的销售增长
   - 食品饮料类别显示相对稳定的月度销售，波动性最小

2. **增长趋势**：
   - 电子产品预计年增长率为 12.5%
   - 家居用品预计年增长率为 8.3%
   - 食品饮料预计年增长率为 5.7%

3. **产品类别相关性**：
   - 电子产品和家居用品销售呈现中度正相关 (r=0.65)
   - 食品饮料与其他类别相关性较低 (r<0.3)

## 预测方法说明

我使用了以下步骤进行预测：
1. 对每个产品类别的时间序列数据进行季节性分解
2. 应用 SARIMA 模型，参数通过 AIC 准则优化
3. 进行交叉验证以确保模型稳健性
4. 生成未来 6 个月的点预测和预测区间

预测准确度评估：MAPE (平均绝对百分比误差) = 7.2%，表明预测相对可靠。
```

## 使用 Llama 3 进行自然语言数据查询

Llama 3 在自然语言理解和 SQL 生成方面表现出色。以下示例展示如何使用 Llama 3 进行自然语言数据查询。

### 步骤 1：了解数据库结构

首先，使用 MCP 数据库工具了解数据库结构：

```
您：请帮我列出数据库中的所有表及其结构。

AI：我将为您列出数据库中的所有表及其结构。

数据库包含以下表：

1. customers（客户表）
   - id: INTEGER (主键)
   - name: TEXT
   - email: TEXT
   - registration_date: DATE
   - city: TEXT
   - status: TEXT

2. products（产品表）
   - id: INTEGER (主键)
   - name: TEXT
   - category: TEXT
   - price: DECIMAL
   - stock: INTEGER
   - description: TEXT

3. orders（订单表）
   - id: INTEGER (主键)
   - customer_id: INTEGER (外键 -> customers.id)
   - order_date: DATETIME
   - total_amount: DECIMAL
   - status: TEXT

4. order_items（订单项表）
   - id: INTEGER (主键)
   - order_id: INTEGER (外键 -> orders.id)
   - product_id: INTEGER (外键 -> products.id)
   - quantity: INTEGER
   - price: DECIMAL
```

### 步骤 2：使用自然语言提问

向 Llama 3 提出自然语言问题：

```
您：我想了解过去 3 个月中，哪些客户购买了电子产品类别的商品，他们的平均消费金额是多少，以及他们最常购买的产品是什么？

Llama 3：我将帮您分析过去 3 个月购买电子产品的客户数据。为了回答您的问题，我需要编写一个 SQL 查询。

首先，我会分析您的问题：
1. 查找过去 3 个月购买了电子产品的客户
2. 计算这些客户的平均消费金额
3. 确定这些客户最常购买的产品

以下是我构建的 SQL 查询：

```sql
WITH electronics_customers AS (
    -- 找出过去 3 个月购买了电子产品的客户
    SELECT DISTINCT c.id, c.name, c.email
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    WHERE p.category = '电子产品'
    AND o.order_date >= DATE('now', '-3 months')
    AND o.status = 'completed'
),
customer_spending AS (
    -- 计算这些客户的平均消费金额
    SELECT
        ec.id,
        ec.name,
        ROUND(AVG(o.total_amount), 2) AS avg_spending
    FROM electronics_customers ec
    JOIN orders o ON ec.id = o.customer_id
    WHERE o.order_date >= DATE('now', '-3 months')
    GROUP BY ec.id, ec.name
),
popular_products AS (
    -- 找出这些客户最常购买的产品
    SELECT
        ec.id AS customer_id,
        p.id AS product_id,
        p.name AS product_name,
        COUNT(*) AS purchase_count,
        RANK() OVER (PARTITION BY ec.id ORDER BY COUNT(*) DESC) AS rank
    FROM electronics_customers ec
    JOIN orders o ON ec.id = o.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    WHERE o.order_date >= DATE('now', '-3 months')
    GROUP BY ec.id, p.id, p.name
)
-- 最终结果
SELECT
    cs.id AS customer_id,
    cs.name AS customer_name,
    cs.avg_spending,
    pp.product_name AS favorite_product
FROM customer_spending cs
JOIN popular_products pp ON cs.id = pp.customer_id
WHERE pp.rank = 1
ORDER BY cs.avg_spending DESC;
```

让我执行这个查询并为您分析结果。

查询结果显示：

客户ID | 客户名称  | 平均消费金额 | 最喜爱产品
-------|----------|------------|------------
1045   | 张明      | ¥3,245.67  | 智能手表 Pro
1078   | 李华      | ¥2,876.50  | 无线耳机 X3
1023   | 王芳      | ¥2,567.89  | 超薄笔记本电脑
...    | ...      | ...        | ...

分析结果：
1. 过去 3 个月内，共有 37 位客户购买了电子产品
2. 这些客户的平均消费金额为 ¥2,156.78
3. 最受欢迎的电子产品是"智能手表 Pro"，有 12 位客户将其作为最常购买的产品
4. 消费金额最高的客户主要购买高端电子产品，如笔记本电脑和智能手表
5. 有 8 位客户在过去 3 个月内进行了多次电子产品购买，平均每人购买 3.5 次

建议：
1. 针对这 37 位客户开展电子产品促销活动
2. 特别关注"智能手表 Pro"和"无线耳机 X3"的库存管理
3. 考虑为高消费客户提供会员优惠
```

## 最佳实践

### 提高 LLM 交互效果的技巧

1. **提供清晰的上下文**：向 LLM 提供数据库结构、数据类型和关系的详细信息
2. **分步骤提问**：复杂分析任务分解为多个步骤，逐步引导 LLM
3. **指定输出格式**：明确要求 LLM 以特定格式（如 HTML、Markdown、JSON）输出结果
4. **验证和迭代**：检查 LLM 生成的查询和分析，必要时提供反馈并要求修改
5. **利用模型优势**：根据不同 LLM 的优势选择适合的任务（如 DeepSeek 生成代码，Claude 创建可视化）

### 安全注意事项

1. **数据隐私**：避免向 LLM 提供敏感或个人身份信息
2. **查询验证**：在执行 LLM 生成的查询前，检查其安全性和正确性
3. **结果审核**：审核 LLM 生成的分析结果，确保其准确性和合理性
4. **访问控制**：限制 LLM 对数据库的访问权限，仅允许只读操作
5. **记录交互**：记录与 LLM 的交互，以便审计和改进
