# 多数据库支持架构数据流图

## 1. 概述

本文档提供了多数据库支持架构的详细数据流图，展示了不同操作场景下数据如何在系统各组件之间流动。

## 2. 读操作数据流

### 2.1 基本读操作

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant DBClient as DatabaseClient
    participant PermCheck as PermissionChecker
    participant ConnMgr as ConnectionManager
    participant Adapter as 适配器
    participant Conn as 连接
    participant DB as 数据库
    
    Client->>DBClient: execute_query(conn_name, query, params)
    DBClient->>PermCheck: check_permission(conn_name, resource, "READ")
    alt 权限检查通过
        PermCheck-->>DBClient: 允许操作
        DBClient->>ConnMgr: get_adapter(conn_name)
        ConnMgr-->>DBClient: 返回适配器
        DBClient->>Adapter: execute_query(query, params)
        Adapter->>Conn: execute(query, params)
        Conn->>DB: 执行数据库操作
        DB-->>Conn: 返回结果
        Conn-->>Adapter: 返回结果
        Adapter-->>DBClient: 转换并返回结果
        DBClient-->>Client: 返回最终结果
    else 权限检查失败
        PermCheck-->>DBClient: 拒绝操作
        DBClient-->>Client: 抛出PermissionError
    end
```

### 2.2 使用查询构建器的读操作

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant DBClient as DatabaseClient
    participant QueryBuilder as 查询构建器
    participant PermCheck as PermissionChecker
    participant ConnMgr as ConnectionManager
    participant Adapter as 适配器
    participant Conn as 连接
    participant DB as 数据库
    
    Client->>DBClient: 创建查询构建器
    DBClient->>QueryBuilder: create_query_builder(adapter_type)
    QueryBuilder-->>Client: 返回查询构建器
    Client->>QueryBuilder: select("users").where("age > 18").build()
    QueryBuilder-->>Client: 返回查询对象
    Client->>DBClient: execute_query(conn_name, query)
    DBClient->>PermCheck: check_permission(conn_name, "users", "READ")
    alt 权限检查通过
        PermCheck-->>DBClient: 允许操作
        DBClient->>ConnMgr: get_adapter(conn_name)
        ConnMgr-->>DBClient: 返回适配器
        DBClient->>Adapter: execute_query(query)
        Adapter->>Conn: execute(query)
        Conn->>DB: 执行数据库操作
        DB-->>Conn: 返回结果
        Conn-->>Adapter: 返回结果
        Adapter-->>DBClient: 转换并返回结果
        DBClient-->>Client: 返回最终结果
    else 权限检查失败
        PermCheck-->>DBClient: 拒绝操作
        DBClient-->>Client: 抛出PermissionError
    end
```

## 3. 写操作数据流

### 3.1 基本写操作

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant DBClient as DatabaseClient
    participant PermCheck as PermissionChecker
    participant ConnMgr as ConnectionManager
    participant Adapter as 适配器
    participant Conn as 连接
    participant DB as 数据库
    participant Audit as AuditLogger
    
    Client->>DBClient: execute_write(conn_name, query, params)
    DBClient->>Adapter: extract_resource_name(query)
    Adapter-->>DBClient: 返回资源名称
    DBClient->>PermCheck: check_permission(conn_name, resource, operation_type)
    alt 权限检查通过
        PermCheck-->>DBClient: 允许操作
        DBClient->>ConnMgr: get_adapter(conn_name)
        ConnMgr-->>DBClient: 返回适配器
        DBClient->>Adapter: execute_write(query, params)
        Adapter->>Conn: execute(query, params)
        Conn->>DB: 执行数据库操作
        DB-->>Conn: 返回结果
        Conn-->>Adapter: 返回结果
        Adapter-->>DBClient: 转换并返回结果
        DBClient->>Audit: log_operation(conn_name, resource, operation, result)
        DBClient-->>Client: 返回最终结果
    else 权限检查失败
        PermCheck-->>DBClient: 拒绝操作
        DBClient-->>Client: 抛出PermissionError
    end
```

### 3.2 使用查询构建器的写操作

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant DBClient as DatabaseClient
    participant QueryBuilder as 查询构建器
    participant PermCheck as PermissionChecker
    participant ConnMgr as ConnectionManager
    participant Adapter as 适配器
    participant Conn as 连接
    participant DB as 数据库
    participant Audit as AuditLogger
    
    Client->>DBClient: 创建查询构建器
    DBClient->>QueryBuilder: create_query_builder(adapter_type)
    QueryBuilder-->>Client: 返回查询构建器
    Client->>QueryBuilder: insert("users", {"name": "John", "age": 30}).build()
    QueryBuilder-->>Client: 返回查询对象
    Client->>DBClient: execute_write(conn_name, query)
    DBClient->>PermCheck: check_permission(conn_name, "users", "INSERT")
    alt 权限检查通过
        PermCheck-->>DBClient: 允许操作
        DBClient->>ConnMgr: get_adapter(conn_name)
        ConnMgr-->>DBClient: 返回适配器
        DBClient->>Adapter: execute_write(query)
        Adapter->>Conn: execute(query)
        Conn->>DB: 执行数据库操作
        DB-->>Conn: 返回结果
        Conn-->>Adapter: 返回结果
        Adapter-->>DBClient: 转换并返回结果
        DBClient->>Audit: log_operation(conn_name, "users", "INSERT", result)
        DBClient-->>Client: 返回最终结果
    else 权限检查失败
        PermCheck-->>DBClient: 拒绝操作
        DBClient-->>Client: 抛出PermissionError
    end
```

## 4. 事务数据流

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant DBClient as DatabaseClient
    participant TransMgr as TransactionManager
    participant ConnMgr as ConnectionManager
    participant Adapter as 适配器
    participant Conn as 连接
    participant DB as 数据库
    
    Client->>DBClient: begin_transaction(conn_name)
    DBClient->>ConnMgr: get_connection(conn_name)
    ConnMgr-->>DBClient: 返回连接
    DBClient->>TransMgr: begin_transaction(connection)
    TransMgr->>Conn: begin_transaction()
    Conn->>DB: 开始事务
    DB-->>Conn: 返回结果
    Conn-->>TransMgr: 返回结果
    TransMgr-->>DBClient: 返回事务对象
    DBClient-->>Client: 返回事务对象
    
    loop 执行多个操作
        Client->>DBClient: execute_write(conn_name, query, params, transaction)
        DBClient->>Adapter: execute_write(query, params)
        Adapter->>Conn: execute(query, params)
        Conn->>DB: 执行数据库操作
        DB-->>Conn: 返回结果
        Conn-->>Adapter: 返回结果
        Adapter-->>DBClient: 转换并返回结果
        DBClient-->>Client: 返回结果
    end
    
    alt 提交事务
        Client->>DBClient: commit_transaction(transaction)
        DBClient->>TransMgr: commit_transaction(transaction)
        TransMgr->>Conn: commit()
        Conn->>DB: 提交事务
        DB-->>Conn: 返回结果
        Conn-->>TransMgr: 返回结果
        TransMgr-->>DBClient: 返回结果
        DBClient-->>Client: 返回结果
    else 回滚事务
        Client->>DBClient: rollback_transaction(transaction)
        DBClient->>TransMgr: rollback_transaction(transaction)
        TransMgr->>Conn: rollback()
        Conn->>DB: 回滚事务
        DB-->>Conn: 返回结果
        Conn-->>TransMgr: 返回结果
        TransMgr-->>DBClient: 返回结果
        DBClient-->>Client: 返回结果
    end
```

## 5. 错误处理和重试数据流

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant DBClient as DatabaseClient
    participant RetryHandler as 重试处理器
    participant ConnMgr as ConnectionManager
    participant Adapter as 适配器
    participant Conn as 连接
    participant DB as 数据库
    
    Client->>DBClient: execute_query(conn_name, query, params)
    DBClient->>RetryHandler: execute_with_retry(execute_query_func, conn_name, query, params)
    RetryHandler->>ConnMgr: get_adapter(conn_name)
    ConnMgr-->>RetryHandler: 返回适配器
    RetryHandler->>Adapter: execute_query(query, params)
    Adapter->>Conn: execute(query, params)
    Conn->>DB: 执行数据库操作
    
    alt 操作成功
        DB-->>Conn: 返回结果
        Conn-->>Adapter: 返回结果
        Adapter-->>RetryHandler: 返回结果
        RetryHandler-->>DBClient: 返回结果
        DBClient-->>Client: 返回最终结果
    else 操作失败（临时错误）
        DB-->>Conn: 抛出错误
        Conn-->>Adapter: 抛出错误
        Adapter-->>RetryHandler: 抛出ConnectionError
        RetryHandler->>RetryHandler: should_retry(error, attempt)
        alt 应该重试
            RetryHandler->>RetryHandler: 等待重试间隔
            RetryHandler->>Adapter: 重试操作
            Adapter->>Conn: execute(query, params)
            Conn->>DB: 执行数据库操作
            DB-->>Conn: 返回结果
            Conn-->>Adapter: 返回结果
            Adapter-->>RetryHandler: 返回结果
            RetryHandler-->>DBClient: 返回结果
            DBClient-->>Client: 返回最终结果
        else 不应该重试
            RetryHandler-->>DBClient: 抛出原始错误
            DBClient-->>Client: 抛出错误
        end
    else 操作失败（永久错误）
        DB-->>Conn: 抛出错误
        Conn-->>Adapter: 抛出错误
        Adapter-->>RetryHandler: 抛出QueryError
        RetryHandler->>RetryHandler: should_retry(error, attempt)
        RetryHandler-->>DBClient: 抛出原始错误
        DBClient-->>Client: 抛出错误
    end
```

## 6. 连接池管理数据流

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant DBClient as DatabaseClient
    participant ConnMgr as ConnectionManager
    participant ConnPool as ConnectionPool
    participant ConnFactory as ConnectionFactory
    participant Conn as 连接
    participant DB as 数据库
    
    Client->>DBClient: execute_query(conn_name, query, params)
    DBClient->>ConnMgr: get_connection(conn_name)
    ConnMgr->>ConnPool: get_connection(conn_name)
    
    alt 连接池中有可用连接
        ConnPool-->>ConnMgr: 返回现有连接
    else 连接池中没有可用连接
        ConnPool->>ConnFactory: create_connection(config)
        ConnFactory->>Conn: 创建新连接
        Conn->>DB: 建立连接
        DB-->>Conn: 连接成功
        Conn-->>ConnFactory: 返回新连接
        ConnFactory-->>ConnPool: 返回新连接
        ConnPool-->>ConnMgr: 返回新连接
    end
    
    ConnMgr-->>DBClient: 返回连接
    DBClient->>Conn: 使用连接执行操作
    Conn->>DB: 执行数据库操作
    DB-->>Conn: 返回结果
    Conn-->>DBClient: 返回结果
    DBClient->>ConnMgr: release_connection(connection)
    ConnMgr->>ConnPool: release_connection(connection)
    DBClient-->>Client: 返回最终结果
```

## 7. 配置加载数据流

```mermaid
sequenceDiagram
    participant App as 应用程序
    participant ConfigMgr as ConfigManager
    participant FileSystem as 文件系统
    participant ConnConfig as ConnectionConfig
    participant WritePermission as WritePermission
    
    App->>ConfigMgr: load_config()
    ConfigMgr->>FileSystem: 读取配置文件
    FileSystem-->>ConfigMgr: 返回配置数据
    
    loop 对每个连接配置
        ConfigMgr->>ConnConfig: 创建连接配置
        
        alt 连接配置包含写权限
            ConnConfig->>WritePermission: 创建写权限配置
            WritePermission-->>ConnConfig: 返回写权限配置
        end
        
        ConnConfig-->>ConfigMgr: 返回连接配置
    end
    
    ConfigMgr->>ConfigMgr: validate_config()
    ConfigMgr-->>App: 配置加载完成
```

## 8. 资源列表和描述数据流

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant DBClient as DatabaseClient
    participant PermCheck as PermissionChecker
    participant ConnMgr as ConnectionManager
    participant Adapter as 适配器
    participant Conn as 连接
    participant DB as 数据库
    
    Client->>DBClient: list_resources(conn_name)
    DBClient->>ConnMgr: get_adapter(conn_name)
    ConnMgr-->>DBClient: 返回适配器
    DBClient->>Adapter: list_resources()
    Adapter->>Conn: 获取资源列表
    Conn->>DB: 查询资源列表
    DB-->>Conn: 返回资源列表
    Conn-->>Adapter: 返回资源列表
    Adapter-->>DBClient: 转换并返回资源列表
    
    loop 对每个资源
        DBClient->>PermCheck: check_permission(conn_name, resource, "READ")
        alt 有权限
            PermCheck-->>DBClient: 允许访问
        else 无权限
            PermCheck-->>DBClient: 拒绝访问
            DBClient->>DBClient: 从列表中移除资源
        end
    end
    
    DBClient-->>Client: 返回过滤后的资源列表
    
    Client->>DBClient: describe_resource(conn_name, resource_name)
    DBClient->>PermCheck: check_permission(conn_name, resource_name, "READ")
    
    alt 权限检查通过
        PermCheck-->>DBClient: 允许操作
        DBClient->>ConnMgr: get_adapter(conn_name)
        ConnMgr-->>DBClient: 返回适配器
        DBClient->>Adapter: describe_resource(resource_name)
        Adapter->>Conn: 获取资源描述
        Conn->>DB: 查询资源结构
        DB-->>Conn: 返回资源结构
        Conn-->>Adapter: 返回资源结构
        Adapter-->>DBClient: 转换并返回资源描述
        DBClient-->>Client: 返回资源描述
    else 权限检查失败
        PermCheck-->>DBClient: 拒绝操作
        DBClient-->>Client: 抛出PermissionError
    end
```

## 9. 总结

以上数据流图展示了多数据库支持架构中不同操作场景下数据如何在系统各组件之间流动。这些数据流图有助于理解系统的运行机制，为实现提供指导。
