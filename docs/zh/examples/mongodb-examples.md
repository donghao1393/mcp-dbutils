# MongoDB 示例

*[English](../../en/examples/mongodb-examples.md) | 中文 | [Français](../../fr/examples/mongodb-examples.md) | [Español](../../es/examples/mongodb-examples.md) | [العربية](../../ar/examples/mongodb-examples.md) | [Русский](../../ru/examples/mongodb-examples.md)*

本文档提供了使用MCP数据库工具与MongoDB数据库交互的实用示例。这些示例展示了如何利用MongoDB的特性进行文档存储、查询和聚合操作。

## 基本查询示例

### 列出所有集合

```javascript
db.getCollectionNames();
```

或者使用`listCollections`命令：

```javascript
db.runCommand({ listCollections: 1 });
```

### 查看集合结构

MongoDB是无模式的，但您可以检查集合中文档的结构：

```javascript
// 获取一个样本文档
db.customers.findOne();

// 获取集合统计信息
db.customers.stats();

// 分析集合中的文档结构
db.customers.aggregate([
  { $sample: { size: 100 } },
  { $project: { 
      fieldNames: { $objectToArray: "$$ROOT" }
    }
  },
  { $unwind: "$fieldNames" },
  { $group: { 
      _id: "$fieldNames.k", 
      count: { $sum: 1 },
      types: { $addToSet: { $type: "$fieldNames.v" } }
    }
  },
  { $sort: { count: -1 } }
]);
```

### 基本数据查询

```javascript
// 查询customers集合中的前10个文档
db.customers.find().limit(10);

// 按条件过滤
db.customers.find({ city: "New York", status: "active" });

// 排序查询
db.customers.find({}, { customer_id: 1, name: 1, registration_date: 1 })
  .sort({ registration_date: -1 })
  .limit(20);
```

## MongoDB特有功能

### 文档嵌入

MongoDB允许在单个文档中嵌入相关数据：

```javascript
// 查询带有嵌入项的订单
db.orders.find({
  customer_id: "C1001",
  "items.product_name": "智能手机"
});

// 插入带有嵌入数组的文档
db.orders.insertOne({
  order_id: "O1001",
  customer_id: "C1001",
  order_date: new Date(),
  status: "处理中",
  items: [
    { product_id: "P1", product_name: "智能手机", quantity: 1, price: 699.99 },
    { product_id: "P2", product_name: "手机壳", quantity: 2, price: 19.99 }
  ],
  shipping_address: {
    street: "123 Main St",
    city: "纽约",
    state: "NY",
    zip: "10001"
  },
  total_amount: 739.97
});
```

### 文档引用

对于更复杂的关系，您可以使用文档引用：

```javascript
// 插入带有引用的文档
db.customers.insertOne({
  _id: "C1001",
  name: "张三",
  email: "zhangsan@example.com",
  address_id: "A1001"
});

db.addresses.insertOne({
  _id: "A1001",
  street: "123 Main St",
  city: "北京",
  district: "朝阳区",
  zip: "100001"
});

// 使用lookup查询（类似于SQL中的JOIN）
db.customers.aggregate([
  { $match: { _id: "C1001" } },
  { $lookup: {
      from: "addresses",
      localField: "address_id",
      foreignField: "_id",
      as: "address"
    }
  },
  { $unwind: "$address" }
]);
```

### 文本搜索

MongoDB提供强大的文本搜索功能：

```javascript
// 创建文本索引
db.products.createIndex({ name: "text", description: "text" });

// 执行文本搜索
db.products.find({ $text: { $search: "舒适 耐用" } });

// 带分数的文本搜索
db.products.find(
  { $text: { $search: "舒适 耐用" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } });
```

### 地理空间查询

MongoDB支持地理空间查询，适用于基于位置的应用：

```javascript
// 创建地理空间索引
db.stores.createIndex({ location: "2dsphere" });

// 插入带有地理空间数据的文档
db.stores.insertOne({
  name: "市中心店",
  location: {
    type: "Point",
    coordinates: [116.4074, 39.9042]  // [经度, 纬度]
  }
});

// 查找附近的商店（5公里内）
db.stores.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [116.4074, 39.9042]
      },
      $maxDistance: 5000  // 单位：米
    }
  }
});
```

## 高级查询技术

### 聚合框架

MongoDB的聚合框架提供强大的数据处理能力：

```javascript
// 按类别计算销售额
db.orders.aggregate([
  { $unwind: "$items" },
  { $lookup: {
      from: "products",
      localField: "items.product_id",
      foreignField: "_id",
      as: "product_info"
    }
  },
  { $unwind: "$product_info" },
  { $group: {
      _id: "$product_info.category",
      total_sales: { $sum: { $multiply: ["$items.quantity", "$items.price"] } },
      count: { $sum: 1 }
    }
  },
  { $sort: { total_sales: -1 } }
]);

// 客户购买分析
db.orders.aggregate([
  { $group: {
      _id: "$customer_id",
      total_spent: { $sum: "$total_amount" },
      order_count: { $sum: 1 },
      avg_order_value: { $avg: "$total_amount" },
      first_purchase: { $min: "$order_date" },
      last_purchase: { $max: "$order_date" }
    }
  },
  { $lookup: {
      from: "customers",
      localField: "_id",
      foreignField: "_id",
      as: "customer_info"
    }
  },
  { $unwind: "$customer_info" }
]);
```

## 性能优化技巧

### 使用Explain

使用`explain()`查看查询计划并帮助优化查询：

```javascript
// 分析查询执行计划
db.customers.find({ status: "active", city: "北京" }).explain("executionStats");

// 分析聚合执行计划
db.orders.aggregate([
  { $match: { status: "已完成" } },
  { $group: { _id: "$customer_id", total: { $sum: "$total_amount" } } }
], { explain: true });
```

### 优化索引使用

确保查询使用适当的索引：

```javascript
// 创建单字段索引
db.customers.createIndex({ email: 1 }, { unique: true });

// 创建复合索引
db.orders.createIndex({ customer_id: 1, order_date: -1 });

// 创建部分索引
db.orders.createIndex(
  { status: 1 },
  { partialFilterExpression: { status: "处理中" } }
);

// 查看集合索引
db.customers.getIndexes();
```

## AI交互示例

以下是使用MongoDB数据与AI交互的示例对话：

**您**：能否分析一下我们各个产品类别的库存水平？

**AI**：我将分析您各个产品类别的库存水平。以下是我的发现：

```
类别        | 产品总数 | 总库存量 | 平均库存/产品 | 低库存产品(<20)
------------|---------|---------|--------------|---------------
电子产品    | 342     | 12,567  | 36.7         | 28 (8.2%)
服装        | 567     | 24,890  | 43.9         | 45 (7.9%)
家居用品    | 289     | 8,765   | 30.3         | 37 (12.8%)
体育用品    | 178     | 5,432   | 30.5         | 19 (10.7%)
美妆产品    | 231     | 7,654   | 33.1         | 15 (6.5%)
```

家居用品类别有最高比例的低库存产品(12.8%)，这表明可能存在库存管理问题。服装类别的每件产品平均库存最高，这可能表明某些区域存在库存过剩的情况。我建议重点关注37件低库存的家居用品，并审查该类别的库存管理策略。
