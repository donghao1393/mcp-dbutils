# Redis Examples

*English | [中文](../../zh/examples/redis-examples.md) | [Français](../../fr/examples/redis-examples.md) | [Español](../../es/examples/redis-examples.md) | [العربية](../../ar/examples/redis-examples.md) | [Русский](../../ru/examples/redis-examples.md)*

This document provides practical examples for interacting with Redis databases using MCP Database Utilities. These examples demonstrate how to leverage Redis features for caching, session management, real-time analytics, and more.

## Basic Command Examples

### Key-Value Operations

```
# Set a simple key-value pair
SET user:1001 "John Doe"

# Get a value by key
GET user:1001

# Set a key with expiration (10 seconds)
SETEX session:5001 10 "active_session_data"

# Check if a key exists
EXISTS user:1001

# Delete a key
DEL user:1001

# Set multiple values at once
MSET user:1001:name "John Doe" user:1001:email "john@example.com" user:1001:age 30

# Get multiple values at once
MGET user:1001:name user:1001:email user:1001:age
```

### Working with Hashes

Hashes are maps between string fields and string values, perfect for representing objects:

```
# Set hash fields
HSET user:1001 name "John Doe" email "john@example.com" age 30

# Get a specific hash field
HGET user:1001 name

# Get all fields and values in a hash
HGETALL user:1001

# Check if a field exists in a hash
HEXISTS user:1001 email

# Increment a numeric field
HINCRBY user:1001 age 1

# Delete a field from a hash
HDEL user:1001 age

# Get all field names in a hash
HKEYS user:1001

# Get all field values in a hash
HVALS user:1001
```

### Lists Operations

Lists are collections of ordered string elements:

```
# Add elements to the beginning of a list
LPUSH recent_users user:1001 user:1002 user:1003

# Add elements to the end of a list
RPUSH notifications:1001 "New message" "Friend request" "System update"

# Get a range of elements from a list
LRANGE recent_users 0 -1  # Get all elements
LRANGE notifications:1001 0 2  # Get first 3 elements

# Remove and get the first element
LPOP recent_users

# Remove and get the last element
RPOP notifications:1001

# Get list length
LLEN recent_users

# Remove elements by value
LREM recent_users 1 user:1002  # Remove 1 occurrence of user:1002
```

### Sets Operations

Sets are unordered collections of unique strings:

```
# Add members to a set
SADD active_users user:1001 user:1002 user:1003

# Check if a member exists in a set
SISMEMBER active_users user:1001

# Get all members in a set
SMEMBERS active_users

# Remove members from a set
SREM active_users user:1003

# Get the number of members in a set
SCARD active_users

# Get the difference between sets
SDIFF active_users inactive_users

# Get the intersection between sets
SINTER active_users premium_users

# Get the union of sets
SUNION active_users inactive_users
```

### Sorted Sets Operations

Sorted sets are sets where each member has an associated score for ordering:

```
# Add members with scores to a sorted set
ZADD leaderboard 100 user:1001 85 user:1002 95 user:1003

# Get a range of members by rank (ordered by score)
ZRANGE leaderboard 0 2  # Get top 3 users

# Get a range of members by score
ZRANGEBYSCORE leaderboard 90 100  # Get users with scores between 90 and 100

# Get a member's rank
ZRANK leaderboard user:1001

# Get a member's score
ZSCORE leaderboard user:1001

# Increment a member's score
ZINCRBY leaderboard 10 user:1002

# Count members with scores in a range
ZCOUNT leaderboard 90 100

# Remove members from a sorted set
ZREM leaderboard user:1003
```

## Redis-Specific Features

### Pub/Sub Messaging

Redis provides a Publish/Subscribe messaging paradigm:

```
# Subscribe to a channel
SUBSCRIBE notifications

# Publish a message to a channel
PUBLISH notifications "Hello, subscribers!"

# Subscribe to channels matching a pattern
PSUBSCRIBE user:*:notifications

# Unsubscribe from a channel
UNSUBSCRIBE notifications

# Unsubscribe from all channels
UNSUBSCRIBE
```

### Transactions

Redis supports transactions for executing multiple commands atomically:

```
# Start a transaction
MULTI

# Queue commands
SET user:1001:status "active"
EXPIRE user:1001:status 3600
HINCRBY user:1001:stats logins 1

# Execute the transaction
EXEC

# Discard a transaction
MULTI
SET user:1001:status "active"
DISCARD
```

### Lua Scripting

Redis allows executing Lua scripts for complex operations:

```
# Execute a simple Lua script
EVAL "return redis.call('GET', KEYS[1])" 1 user:1001

# Increment a counter only if it exists
EVAL "
local current = redis.call('GET', KEYS[1])
if current then
  return redis.call('INCR', KEYS[1])
else
  return nil
end
" 1 counter:visits

# Atomic increment with expiry
EVAL "
local key = KEYS[1]
local increment = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local current = redis.call('INCRBY', key, increment)
redis.call('EXPIRE', key, ttl)
return current
" 1 counter:visits 1 3600
```

## Advanced Usage Patterns

### Caching Strategies

```
# Set cache with expiration
SET cache:user:1001 "{\"name\":\"John\",\"email\":\"john@example.com\"}" EX 3600

# Check and set pattern (using Lua)
EVAL "
local key = KEYS[1]
local value = ARGV[1]
local ttl = tonumber(ARGV[2])
if redis.call('EXISTS', key) == 0 then
  redis.call('SET', key, value, 'EX', ttl)
  return 1
else
  return 0
end
" 1 cache:product:1001 "{\"name\":\"Smartphone\",\"price\":699.99}" 3600

# Cache invalidation by prefix
EVAL "
local pattern = ARGV[1]
local keys = redis.call('KEYS', pattern)
local count = 0
for i, key in ipairs(keys) do
  redis.call('DEL', key)
  count = count + 1
end
return count
" 0 "cache:product:*"
```

### Rate Limiting

```
# Simple rate limiter (allow 5 requests per minute)
EVAL "
local key = KEYS[1]
local max_requests = tonumber(ARGV[1])
local window_seconds = tonumber(ARGV[2])
local count = redis.call('INCR', key)
if count == 1 then
  redis.call('EXPIRE', key, window_seconds)
end
return count <= max_requests
" 1 "ratelimit:user:1001:api" 5 60

# Sliding window rate limiter
EVAL "
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local max_requests = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)
if count < max_requests then
  redis.call('ZADD', key, now, now .. '-' .. math.random())
  redis.call('EXPIRE', key, window)
  return 1
else
  return 0
end
" 1 "ratelimit:user:1001:api" $(date +%s) 60 10
```

### Session Management

```
# Create a new session
HMSET session:abc123 user_id 1001 created_at "2023-05-01T10:00:00Z" ip "192.168.1.1" data "{\"cart\":[\"item1\",\"item2\"]}"
EXPIRE session:abc123 1800  # 30 minutes

# Update session expiry on activity
EXPIRE session:abc123 1800

# Update session data
HSET session:abc123 data "{\"cart\":[\"item1\",\"item2\",\"item3\"]}"
EXPIRE session:abc123 1800

# Get session data
HGETALL session:abc123

# Delete session
DEL session:abc123
```

## AI Interaction Examples

Here are some example conversations with AI using Redis data:

**You**: Can you analyze our website's traffic patterns based on the Redis analytics data?

**AI**: Based on the Redis analytics data, here's an analysis of your website's traffic patterns:

```
Time Period    | Visitors | Page Views | Avg. Session Duration | Bounce Rate
---------------|----------|-----------|----------------------|------------
Morning (6-12) | 3,245    | 12,567    | 3m 42s               | 32.4%
Afternoon (12-6)| 5,678   | 24,321    | 4m 15s               | 28.7%
Evening (6-12) | 7,890    | 35,678    | 5m 23s               | 24.2%
Night (12-6)   | 2,345    | 8,765     | 6m 12s               | 22.5%
```

Your website experiences peak traffic during evening hours (6 PM - 12 AM), with the highest number of visitors (7,890) and page views (35,678). Interestingly, night-time visitors (12 AM - 6 AM) have the longest average session duration (6m 12s) and lowest bounce rate (22.5%), suggesting highly engaged users during these hours.

**You**: What are our most active user segments based on the Redis user activity data?

**AI**: Based on the Redis user activity data, here are your most active user segments:

```
User Segment        | Active Users | Avg. Sessions/Week | Avg. Actions/Session | Conversion Rate
--------------------|--------------|-------------------|---------------------|---------------
Mobile App Users    | 12,567       | 8.3               | 14.2                | 7.8%
Desktop Web Users   | 8,765        | 4.2               | 9.7                 | 5.2%
New Users (<30 days)| 5,432        | 3.5               | 6.8                 | 3.1%
Premium Subscribers | 3,456        | 12.7              | 18.5                | 15.3%
Returning Customers | 7,890        | 5.6               | 11.3                | 9.4%
```

Premium subscribers are your most engaged segment with the highest average sessions per week (12.7), actions per session (18.5), and conversion rate (15.3%). Mobile app users form your largest active user base (12,567 users) with strong engagement metrics. New users show the lowest engagement, suggesting an opportunity to improve onboarding and early user experience.
