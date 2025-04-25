# Advanced LLM Interaction Examples

*English | [中文](../../zh/examples/advanced-llm-interactions.md) | [Français](../../fr/examples/advanced-llm-interactions.md) | [Español](../../es/examples/advanced-llm-interactions.md) | [العربية](../../ar/examples/advanced-llm-interactions.md) | [Русский](../../ru/examples/advanced-llm-interactions.md)*

This document showcases advanced interaction examples between MCP Database Utilities and various Large Language Models (LLMs), helping you fully leverage their potential for data analysis.

## Table of Contents

- [Generating Data Analysis Reports with DeepSeek](#generating-data-analysis-reports-with-deepseek)
- [Creating BI Dashboards in Claude Desktop](#creating-bi-dashboards-in-claude-desktop)
- [Detecting Data Anomalies with GPT-4](#detecting-data-anomalies-with-gpt-4)
- [Predictive Analytics with Gemini](#predictive-analytics-with-gemini)
- [Natural Language Data Queries with Llama 3](#natural-language-data-queries-with-llama-3)

## Generating Data Analysis Reports with DeepSeek

DeepSeek models excel at data analysis and code generation. The following example demonstrates how to use DeepSeek to generate a complete HTML data analysis report.

### Step 1: Prepare Data Query

First, use MCP Database Utilities to query the required data:

```
You: Can you help me query sales data for the past 12 months, grouped by month and product category?

AI: I'll help you query this data. I'll use the dbutils-run-query tool to execute the query.

Here are the query results:

Month    | Product Category | Sales Amount | Order Count | Avg Order Amount
---------|-----------------|--------------|------------|----------------
2023-01  | Electronics     | $245,670     | 432        | $568.68
2023-01  | Home Goods      | $156,890     | 689        | $227.71
...
2023-12  | Food & Beverage | $98,320      | 1,290      | $76.22
```

### Step 2: Request DeepSeek to Generate Analysis Report

Provide the query results to DeepSeek and request an analysis report:

```
You: Please generate a detailed HTML analysis report based on this sales data, including trend analysis, seasonality analysis, and product category comparisons. The report should include interactive charts and key findings.

DeepSeek: I'll generate a detailed HTML analysis report for you. Here's the complete HTML code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Data Analysis Report - 2023</title>
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

        /* More styles... */
    </style>
</head>
<body>
    <header>
        <h1>Sales Data Analysis Report</h1>
        <p class="subtitle">January 2023 - December 2023</p>
    </header>

    <section id="executive-summary">
        <h2>Executive Summary</h2>
        <div class="summary-cards">
            <div class="card">
                <h3>Total Sales</h3>
                <p class="highlight">$2,845,670</p>
                <p class="trend positive">↑ 15.3% YoY</p>
            </div>
            <!-- More cards... -->
        </div>
        <div class="key-findings">
            <h3>Key Findings</h3>
            <ul>
                <li>Electronics category contributed the highest sales, accounting for 42% of total sales</li>
                <li>Q4 sales increased by 28.5% compared to Q1</li>
                <li>Home Goods category performed best during the holiday season (Oct-Dec)</li>
            </ul>
        </div>
    </section>

    <!-- More report content... -->

    <script>
        // Monthly sales trend chart
        const monthlySalesCtx = document.getElementById('monthly-sales-chart').getContext('2d');
        const monthlySalesChart = new Chart(monthlySalesCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Electronics',
                        data: [245670, 234560, 256780, 267890, 278900, 289760, 301230, 312450, 325670, 345670, 367890, 389760],
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    // More datasets...
                ]
            },
            // More configuration...
        });

        // More charts...
    </script>
</body>
</html>
```

This HTML report contains a complete sales data analysis, including interactive charts, trend analysis, and key findings. You can save this code as an HTML file and open it in your browser.
```

### Step 3: Save and Use the Report

Save the generated HTML code as a file and open it in a browser:

```bash
echo '<!DOCTYPE html>...' > sales_analysis_report.html
open sales_analysis_report.html  # on macOS
# or xdg-open sales_analysis_report.html  # on Linux
# or start sales_analysis_report.html  # on Windows
```

## Creating BI Dashboards in Claude Desktop

Claude Desktop supports generating visualizations through artifact outputs. The following example demonstrates how to use Claude to create interactive BI dashboards.

### Step 1: Prepare Data

Use MCP Database Utilities to get the required data:

```
You: Please help me query customer segmentation data, including customer ID, purchase frequency, average spending, and most recent purchase date.

AI: I'll query the customer segmentation data for you.

Here are the query results:

Customer ID | Purchase Frequency | Average Spending | Last Purchase Date
------------|-------------------|-----------------|------------------
1001        | 12                | $1,245.67       | 2023-12-15
1002        | 3                 | $567.89         | 2023-10-23
...
1100        | 8                 | $876.54         | 2023-11-30
```

### Step 2: Request Claude to Generate a BI Dashboard

Provide the data to Claude and request a BI dashboard:

```
You: Please create an interactive BI dashboard for customer segmentation analysis based on this data. The dashboard should include RFM analysis, customer value distribution, and customer lifecycle stages. Please output the result as an HTML artifact.

Claude: I'll create an interactive BI dashboard for customer segmentation analysis. This dashboard will include RFM analysis, customer value distribution, and customer lifecycle stages visualizations.

Here's the BI dashboard created based on your data:

[Claude will generate an HTML artifact containing the interactive BI dashboard]
```

### Step 3: Save and Use the BI Dashboard

The HTML artifact generated by Claude can be downloaded directly and opened in a browser. The dashboard typically includes:

- RFM (Recency, Frequency, Monetary) analysis charts
- Customer value distribution heatmap
- Customer lifecycle stage funnel chart
- Interactive filters and controls

## Detecting Data Anomalies with GPT-4

GPT-4 excels at identifying patterns and anomalies in data. The following example demonstrates how to use GPT-4 for data anomaly detection.

### Step 1: Get Time Series Data

Use MCP Database Utilities to get time series data:

```
You: Please help me query system login data for the past 30 days, including date, time, user ID, and login IP.

AI: I'll query the system login data for you.

Here are the query results:

Date       | Time     | User ID | Login IP
-----------|----------|---------|---------------
2023-12-01 | 08:23:45 | user_a  | 192.168.1.101
2023-12-01 | 09:15:32 | user_b  | 192.168.1.102
...
2023-12-30 | 22:45:12 | user_a  | 45.67.89.123
```

### Step 2: Request GPT-4 to Detect Anomalies

Provide the data to GPT-4 and request anomaly detection:

```
You: Please analyze this login data and identify any potential security anomalies, such as unusual login times, abnormal IP address changes, or suspicious login patterns.

GPT-4: I've analyzed the login data you provided and identified the following potential security anomalies:

1. **Unusual Login Times**:
   - user_a typically logs in during business hours (8:00-18:00), but there was a login at 3:27 AM on December 15th
   - user_c logged in around midnight (00:15) for two consecutive days on December 10th and 11th

2. **Abnormal IP Address Changes**:
   - user_b typically logs in from the 192.168.1.x subnet, but logged in from 78.34.56.89 (located in Russia) on December 20th
   - user_a logged in from 45.67.89.123 on December 30th at 22:45:12, which is inconsistent with their usual IP range

3. **Suspicious Login Patterns**:
   - user_d logged in from 3 different IP addresses within a 10-minute period on December 25th
   - user_e and user_f show identical login patterns (same times, similar IPs), possibly indicating account sharing or automated scripts

4. **Geographic Anomalies**:
   - user_b logged in from a US IP at 16:30:45 on December 19th and from a Russian IP at 02:15:33 on December 20th, a physical travel time that's impossible

Recommended Actions:
1. Implement temporary locks and password resets for accounts user_a, user_b, and user_d
2. Investigate potential account sharing between user_e and user_f
3. Implement two-factor authentication, especially for administrator accounts
4. Set up time-based and geolocation-based login rules
```

## Predictive Analytics with Gemini

Gemini excels at handling structured data and predictive analytics. The following example demonstrates how to use Gemini for sales forecasting.

### Step 1: Get Historical Sales Data

Use MCP Database Utilities to get historical sales data:

```
You: Please help me query monthly sales data for the past 24 months, grouped by product category.

AI: I'll query the monthly sales data for the past 24 months for you.

Here are the query results:

Year-Month | Product Category | Sales Amount | Units Sold
-----------|-----------------|--------------|----------
2022-01    | Electronics     | $198,450     | 324
2022-01    | Home Goods      | $123,670     | 567
...
2023-12    | Food & Beverage | $98,320      | 1,290
```

### Step 2: Request Gemini to Perform Predictive Analysis

Provide the data to Gemini and request predictive analysis:

```
You: Based on this historical sales data, please forecast sales trends for the next 6 months. Consider seasonality factors, growth trends, and correlations between product categories.

Gemini: Based on the 24 months of historical sales data you provided, I've conducted time series analysis and generated sales forecasts for the next 6 months. Here are my analysis results:

## Forecast Overview

I used a SARIMA (Seasonal AutoRegressive Integrated Moving Average) model for forecasting, which accounts for seasonal patterns, overall trends, and correlations between product categories.

## 6-Month Sales Forecast

| Year-Month | Product Category | Forecasted Sales | Forecasted Units | Prediction Interval (95% CI) |
|------------|-----------------|-----------------|-----------------|----------------------------|
| 2024-01    | Electronics     | $267,830        | 437             | $245,670 - $289,990       |
| 2024-01    | Home Goods      | $168,450        | 734             | $154,320 - $182,580       |
| ...        | ...             | ...             | ...             | ...                        |
| 2024-06    | Food & Beverage | $112,780        | 1,456           | $98,540 - $127,020        |

## Key Forecast Findings

1. **Seasonal Patterns**:
   - Electronics sales are projected to increase by 35% during the holiday season (Nov-Jan)
   - Home Goods show a 22% sales increase during spring (Mar-May)
   - Food & Beverage category shows relatively stable monthly sales with minimal volatility

2. **Growth Trends**:
   - Electronics projected annual growth rate: 12.5%
   - Home Goods projected annual growth rate: 8.3%
   - Food & Beverage projected annual growth rate: 5.7%

3. **Product Category Correlations**:
   - Electronics and Home Goods sales show moderate positive correlation (r=0.65)
   - Food & Beverage has low correlation with other categories (r<0.3)

## Forecasting Methodology

I used the following steps for forecasting:
1. Performed seasonal decomposition of time series data for each product category
2. Applied SARIMA models with parameters optimized through AIC criterion
3. Conducted cross-validation to ensure model robustness
4. Generated point forecasts and prediction intervals for the next 6 months

Forecast accuracy assessment: MAPE (Mean Absolute Percentage Error) = 7.2%, indicating relatively reliable predictions.
```

## Natural Language Data Queries with Llama 3

Llama 3 excels at natural language understanding and SQL generation. The following example demonstrates how to use Llama 3 for natural language data queries.

### Step 1: Understand Database Structure

First, use MCP Database Utilities to understand the database structure:

```
You: Please list all tables in the database and their structure.

AI: I'll list all tables in the database and their structure for you.

The database contains the following tables:

1. customers
   - id: INTEGER (primary key)
   - name: TEXT
   - email: TEXT
   - registration_date: DATE
   - city: TEXT
   - status: TEXT

2. products
   - id: INTEGER (primary key)
   - name: TEXT
   - category: TEXT
   - price: DECIMAL
   - stock: INTEGER
   - description: TEXT

3. orders
   - id: INTEGER (primary key)
   - customer_id: INTEGER (foreign key -> customers.id)
   - order_date: DATETIME
   - total_amount: DECIMAL
   - status: TEXT

4. order_items
   - id: INTEGER (primary key)
   - order_id: INTEGER (foreign key -> orders.id)
   - product_id: INTEGER (foreign key -> products.id)
   - quantity: INTEGER
   - price: DECIMAL
```

### Step 2: Ask Questions in Natural Language

Ask Llama 3 questions in natural language:

```
You: I want to know which customers purchased electronics products in the past 3 months, what their average spending was, and what products they purchased most frequently.

Llama 3: I'll help you analyze customer data for electronics purchases over the past 3 months. To answer your question, I need to write a SQL query.

First, let me analyze your question:
1. Find customers who purchased electronics products in the past 3 months
2. Calculate their average spending
3. Determine which products they purchased most frequently

Here's the SQL query I've constructed:

```sql
WITH electronics_customers AS (
    -- Find customers who purchased electronics in the past 3 months
    SELECT DISTINCT c.id, c.name, c.email
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN order_items oi ON o.id = oi.order_id
    JOIN products p ON oi.product_id = p.id
    WHERE p.category = 'Electronics'
    AND o.order_date >= DATE('now', '-3 months')
    AND o.status = 'completed'
),
customer_spending AS (
    -- Calculate average spending for these customers
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
    -- Find most frequently purchased products for these customers
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
-- Final results
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

Let me execute this query and analyze the results for you.

The query results show:

Customer ID | Customer Name | Avg Spending | Favorite Product
------------|--------------|--------------|----------------
1045        | John Smith    | $3,245.67   | Smart Watch Pro
1078        | Emily Johnson | $2,876.50   | Wireless Earbuds X3
1023        | Michael Brown | $2,567.89   | Ultra-Thin Laptop
...         | ...          | ...          | ...

Analysis of the results:
1. In the past 3 months, 37 customers purchased electronics products
2. The average spending across these customers was $2,156.78
3. The most popular electronics product was "Smart Watch Pro," which was the most frequently purchased product for 12 customers
4. Customers with the highest spending primarily purchased high-end electronics like laptops and smart watches
5. 8 customers made multiple electronics purchases in the past 3 months, averaging 3.5 purchases per person

Recommendations:
1. Launch an electronics promotion targeting these 37 customers
2. Pay special attention to inventory management for "Smart Watch Pro" and "Wireless Earbuds X3"
3. Consider offering membership benefits for high-spending customers
```

## Best Practices

### Tips for Improving LLM Interactions

1. **Provide Clear Context**: Give LLMs detailed information about database structure, data types, and relationships
2. **Ask Step-by-Step**: Break complex analysis tasks into multiple steps, guiding the LLM through the process
3. **Specify Output Format**: Clearly request LLMs to output results in specific formats (HTML, Markdown, JSON)
4. **Validate and Iterate**: Check queries and analyses generated by LLMs, provide feedback and request modifications when necessary
5. **Leverage Model Strengths**: Choose tasks based on different LLMs' strengths (e.g., DeepSeek for code generation, Claude for visualizations)

### Security Considerations

1. **Data Privacy**: Avoid providing sensitive or personally identifiable information to LLMs
2. **Query Validation**: Check the safety and correctness of LLM-generated queries before executing them
3. **Result Auditing**: Review analysis results generated by LLMs to ensure accuracy and reasonableness
4. **Access Control**: Limit LLMs' access to databases, allowing read-only operations only
5. **Interaction Logging**: Log interactions with LLMs for auditing and improvement purposes
