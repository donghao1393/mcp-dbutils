# MongoDB Examples

*English | [中文](../../zh/examples/mongodb-examples.md) | [Français](../../fr/examples/mongodb-examples.md) | [Español](../../es/examples/mongodb-examples.md) | [العربية](../../ar/examples/mongodb-examples.md) | [Русский](../../ru/examples/mongodb-examples.md)*

This document provides practical examples for interacting with MongoDB databases using MCP Database Utilities. These examples demonstrate how to leverage MongoDB features for document storage, querying, and aggregation.

## Basic Query Examples

### Listing All Collections

```javascript
db.getCollectionNames();
```

Or using the `listCollections` command:

```javascript
db.runCommand({ listCollections: 1 });
```

### Viewing Collection Structure

MongoDB is schema-less, but you can examine the structure of documents in a collection:

```javascript
// Get a sample document
db.customers.findOne();

// Get collection stats
db.customers.stats();

// Analyze document structure across the collection
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

### Basic Data Queries

```javascript
// Query the first 10 documents from the customers collection
db.customers.find().limit(10);

// Filter by conditions
db.customers.find({ city: "New York", status: "active" });

// Sorting queries
db.customers.find({}, { customer_id: 1, name: 1, registration_date: 1 })
  .sort({ registration_date: -1 })
  .limit(20);
```

## MongoDB-Specific Features

### Document Embedding

MongoDB allows embedding related data within a single document:

```javascript
// Query for orders with embedded items
db.orders.find({
  customer_id: "C1001",
  "items.product_name": "Smartphone"
});

// Insert document with embedded array
db.orders.insertOne({
  order_id: "O1001",
  customer_id: "C1001",
  order_date: new Date(),
  status: "processing",
  items: [
    { product_id: "P1", product_name: "Smartphone", quantity: 1, price: 699.99 },
    { product_id: "P2", product_name: "Phone Case", quantity: 2, price: 19.99 }
  ],
  shipping_address: {
    street: "123 Main St",
    city: "New York",
    state: "NY",
    zip: "10001"
  },
  total_amount: 739.97
});
```

### Document References

For more complex relationships, you can use document references:

```javascript
// Insert documents with references
db.customers.insertOne({
  _id: "C1001",
  name: "John Doe",
  email: "john.doe@example.com",
  address_id: "A1001"
});

db.addresses.insertOne({
  _id: "A1001",
  street: "123 Main St",
  city: "New York",
  state: "NY",
  zip: "10001"
});

// Query with lookup (similar to JOIN in SQL)
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

### Text Search

MongoDB provides powerful text search capabilities:

```javascript
// Create a text index
db.products.createIndex({ name: "text", description: "text" });

// Perform text search
db.products.find({ $text: { $search: "comfortable durable" } });

// Text search with score
db.products.find(
  { $text: { $search: "comfortable durable" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } });
```

### Geospatial Queries

MongoDB supports geospatial queries for location-based applications:

```javascript
// Create a geospatial index
db.stores.createIndex({ location: "2dsphere" });

// Insert a document with geospatial data
db.stores.insertOne({
  name: "Downtown Store",
  location: {
    type: "Point",
    coordinates: [-73.9857, 40.7484]  // [longitude, latitude]
  }
});

// Find stores near a location (within 5km)
db.stores.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.9857, 40.7484]
      },
      $maxDistance: 5000  // in meters
    }
  }
});
```

## Advanced Query Techniques

### Aggregation Framework

MongoDB's aggregation framework provides powerful data processing capabilities:

```javascript
// Calculate sales by category
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

// Customer purchase analysis
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

## Performance Optimization Tips

### Using Explain

Use `explain()` to view query plans and help optimize queries:

```javascript
// Analyze query execution plan
db.customers.find({ status: "active", city: "New York" }).explain("executionStats");

// Analyze aggregation execution plan
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: { _id: "$customer_id", total: { $sum: "$total_amount" } } }
], { explain: true });
```

### Optimizing Index Usage

Ensure queries use appropriate indexes:

```javascript
// Create a single field index
db.customers.createIndex({ email: 1 }, { unique: true });

// Create a compound index
db.orders.createIndex({ customer_id: 1, order_date: -1 });

// Create a partial index
db.orders.createIndex(
  { status: 1 },
  { partialFilterExpression: { status: "processing" } }
);

// View collection indexes
db.customers.getIndexes();
```

## AI Interaction Examples

Here are some example conversations with AI using MongoDB data:

**You**: Can you analyze our product inventory levels across different categories?

**AI**: I'll analyze your product inventory levels by category. Here's what I found:

```
Category      | Total Products | Total Inventory | Avg Inventory/Product | Low Stock Products (<20)
--------------|----------------|-----------------|------------------------|------------------------
Electronics   | 342            | 12,567          | 36.7                   | 28 (8.2%)
Clothing      | 567            | 24,890          | 43.9                   | 45 (7.9%)
Home Goods    | 289            | 8,765           | 30.3                   | 37 (12.8%)
Sports        | 178            | 5,432           | 30.5                   | 19 (10.7%)
Beauty        | 231            | 7,654           | 33.1                   | 15 (6.5%)
```

The Home Goods category has the highest percentage of low-stock products (12.8%), suggesting potential inventory management issues. Clothing has the highest average inventory per product, which might indicate overstocking in some areas.
