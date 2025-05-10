# Redis 示例

*[English](../../en/examples/redis-examples.md) | 中文 | [Français](../../fr/examples/redis-examples.md) | [Español](../../es/examples/redis-examples.md) | [العربية](../../ar/examples/redis-examples.md) | [Русский](../../ru/examples/redis-examples.md)*

本文档提供了使用MCP数据库工具与Redis数据库交互的实用示例。这些示例展示了如何利用Redis的特性进行缓存、会话管理、实时分析等操作。

## 基本命令示例

### 键值操作

```
# 设置简单的键值对
SET user:1001 "张三"

# 通过键获取值
GET user:1001

# 设置带过期时间的键（10秒）
SETEX session:5001 10 "active_session_data"

# 检查键是否存在
EXISTS user:1001

# 删除键
DEL user:1001

# 一次设置多个值
MSET user:1001:name "张三" user:1001:email "zhangsan@example.com" user:1001:age 30

# 一次获取多个值
MGET user:1001:name user:1001:email user:1001:age
```

### 使用哈希

哈希是字符串字段和字符串值之间的映射，非常适合表示对象：

```
# 设置哈希字段
HSET user:1001 name "张三" email "zhangsan@example.com" age 30

# 获取特定哈希字段
HGET user:1001 name

# 获取哈希中的所有字段和值
HGETALL user:1001

# 检查哈希中是否存在字段
HEXISTS user:1001 email

# 增加数值字段
HINCRBY user:1001 age 1

# 从哈希中删除字段
HDEL user:1001 age

# 获取哈希中的所有字段名
HKEYS user:1001

# 获取哈希中的所有字段值
HVALS user:1001
```

### 列表操作

列表是有序字符串元素的集合：

```
# 将元素添加到列表的开头
LPUSH recent_users user:1001 user:1002 user:1003

# 将元素添加到列表的末尾
RPUSH notifications:1001 "新消息" "好友请求" "系统更新"

# 获取列表中的一系列元素
LRANGE recent_users 0 -1  # 获取所有元素
LRANGE notifications:1001 0 2  # 获取前3个元素

# 移除并获取第一个元素
LPOP recent_users

# 移除并获取最后一个元素
RPOP notifications:1001

# 获取列表长度
LLEN recent_users

# 按值移除元素
LREM recent_users 1 user:1002  # 移除1个user:1002
```

### 集合操作

集合是唯一字符串的无序集合：

```
# 向集合添加成员
SADD active_users user:1001 user:1002 user:1003

# 检查成员是否存在于集合中
SISMEMBER active_users user:1001

# 获取集合中的所有成员
SMEMBERS active_users

# 从集合中移除成员
SREM active_users user:1003

# 获取集合中的成员数量
SCARD active_users

# 获取集合之间的差异
SDIFF active_users inactive_users

# 获取集合之间的交集
SINTER active_users premium_users

# 获取集合的并集
SUNION active_users inactive_users
```

### 有序集合操作

有序集合是每个成员都有一个用于排序的分数的集合：

```
# 向有序集合添加带分数的成员
ZADD leaderboard 100 user:1001 85 user:1002 95 user:1003

# 按排名获取成员范围（按分数排序）
ZRANGE leaderboard 0 2  # 获取前3名用户

# 按分数获取成员范围
ZRANGEBYSCORE leaderboard 90 100  # 获取分数在90到100之间的用户

# 获取成员的排名
ZRANK leaderboard user:1001

# 获取成员的分数
ZSCORE leaderboard user:1001

# 增加成员的分数
ZINCRBY leaderboard 10 user:1002

# 计算分数范围内的成员数量
ZCOUNT leaderboard 90 100

# 从有序集合中移除成员
ZREM leaderboard user:1003
```

## Redis特有功能

### 发布/订阅消息

Redis提供发布/订阅消息范式：

```
# 订阅频道
SUBSCRIBE notifications

# 向频道发布消息
PUBLISH notifications "你好，订阅者！"

# 订阅匹配模式的频道
PSUBSCRIBE user:*:notifications

# 取消订阅频道
UNSUBSCRIBE notifications

# 取消订阅所有频道
UNSUBSCRIBE
```

### 事务

Redis支持事务，用于原子性地执行多个命令：

```
# 开始事务
MULTI

# 队列命令
SET user:1001:status "active"
EXPIRE user:1001:status 3600
HINCRBY user:1001:stats logins 1

# 执行事务
EXEC

# 放弃事务
MULTI
SET user:1001:status "active"
DISCARD
```

### Lua脚本

Redis允许执行Lua脚本进行复杂操作：

```
# 执行简单的Lua脚本
EVAL "return redis.call('GET', KEYS[1])" 1 user:1001

# 仅当计数器存在时才增加
EVAL "
local current = redis.call('GET', KEYS[1])
if current then
  return redis.call('INCR', KEYS[1])
else
  return nil
end
" 1 counter:visits

# 原子增加并设置过期时间
EVAL "
local key = KEYS[1]
local increment = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local current = redis.call('INCRBY', key, increment)
redis.call('EXPIRE', key, ttl)
return current
" 1 counter:visits 1 3600
```

## 高级使用模式

### 缓存策略

```
# 设置带过期时间的缓存
SET cache:user:1001 "{\"name\":\"张三\",\"email\":\"zhangsan@example.com\"}" EX 3600

# 检查并设置模式（使用Lua）
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
" 1 cache:product:1001 "{\"name\":\"智能手机\",\"price\":699.99}" 3600

# 按前缀失效缓存
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

### 会话管理

```
# 创建新会话
HMSET session:abc123 user_id 1001 created_at "2023-05-01T10:00:00Z" ip "192.168.1.1" data "{\"cart\":[\"item1\",\"item2\"]}"
EXPIRE session:abc123 1800  # 30分钟

# 在活动时更新会话过期时间
EXPIRE session:abc123 1800

# 更新会话数据
HSET session:abc123 data "{\"cart\":[\"item1\",\"item2\",\"item3\"]}"
EXPIRE session:abc123 1800

# 获取会话数据
HGETALL session:abc123

# 删除会话
DEL session:abc123
```

## AI交互示例

以下是使用Redis数据与AI交互的示例对话：

**您**：能否根据Redis分析数据分析我们网站的流量模式？

**AI**：根据Redis分析数据，以下是您网站的流量模式分析：

```
时间段        | 访问者数 | 页面浏览量 | 平均会话时长 | 跳出率
--------------|---------|-----------|------------|--------
上午 (6-12)   | 3,245   | 12,567    | 3分42秒    | 32.4%
下午 (12-6)   | 5,678   | 24,321    | 4分15秒    | 28.7%
晚上 (6-12)   | 7,890   | 35,678    | 5分23秒    | 24.2%
夜间 (12-6)   | 2,345   | 8,765     | 6分12秒    | 22.5%
```

您的网站在晚上时段（晚上6点至凌晨12点）经历流量高峰，拥有最多的访问者（7,890）和页面浏览量（35,678）。有趣的是，夜间访问者（凌晨12点至6点）拥有最长的平均会话时长（6分12秒）和最低的跳出率（22.5%），表明这些时段的用户参与度很高。

**您**：根据Redis用户活动数据，我们最活跃的用户群体是哪些？

**AI**：根据Redis用户活动数据，以下是您最活跃的用户群体：

```
用户群体          | 活跃用户数 | 平均每周会话数 | 平均每会话操作数 | 转化率
------------------|-----------|--------------|----------------|-------
移动应用用户      | 12,567    | 8.3          | 14.2           | 7.8%
桌面网页用户      | 8,765     | 4.2          | 9.7            | 5.2%
新用户（<30天）   | 5,432     | 3.5          | 6.8            | 3.1%
高级会员          | 3,456     | 12.7         | 18.5           | 15.3%
回头客            | 7,890     | 5.6          | 11.3           | 9.4%
```

高级会员是您参与度最高的群体，拥有最高的每周平均会话数（12.7）、每会话操作数（18.5）和转化率（15.3%）。移动应用用户构成了您最大的活跃用户基础（12,567用户），具有较强的参与度指标。新用户显示出最低的参与度，这表明有机会改善用户引导和早期用户体验。
