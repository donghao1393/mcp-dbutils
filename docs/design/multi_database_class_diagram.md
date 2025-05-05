# 多数据库支持架构类图

## 1. 概述

本文档提供了多数据库支持架构的详细类图，展示了各个组件之间的关系和依赖。

## 2. 连接层类图

```mermaid
classDiagram
    class ConnectionFactory {
        +create_connection(config) ConnectionBase
    }
    
    class ConnectionBase {
        <<abstract>>
        +connect() None
        +disconnect() None
        +is_connected() bool
        +execute(query, params) Result
        +begin_transaction() None
        +commit() None
        +rollback() None
    }
    
    class SQLConnection {
        -dbapi_connection
        -connection_pool
        +connect() None
        +disconnect() None
        +is_connected() bool
        +execute(query, params) Result
        +begin_transaction() None
        +commit() None
        +rollback() None
    }
    
    class MongoConnection {
        -mongo_client
        -database
        +connect() None
        +disconnect() None
        +is_connected() bool
        +execute(query, params) Result
        +begin_transaction() None
        +commit() None
        +rollback() None
    }
    
    class RedisConnection {
        -redis_client
        +connect() None
        +disconnect() None
        +is_connected() bool
        +execute(command, params) Result
        +begin_transaction() None
        +commit() None
        +rollback() None
    }
    
    class ConnectionPool {
        -connections
        +get_connection(name) ConnectionBase
        +release_connection(connection) None
        +close_all() None
    }
    
    ConnectionFactory ..> ConnectionBase : creates
    ConnectionBase <|-- SQLConnection
    ConnectionBase <|-- MongoConnection
    ConnectionBase <|-- RedisConnection
    ConnectionPool o-- ConnectionBase : manages
```

## 3. 适配器层类图

```mermaid
classDiagram
    class AdapterFactory {
        +create_adapter(connection) AdapterBase
    }
    
    class AdapterBase {
        <<abstract>>
        -connection
        +execute_query(query, params) Result
        +execute_write(query, params) Result
        +list_resources() List
        +describe_resource(resource_name) Dict
        +get_resource_stats(resource_name) Dict
        +extract_resource_name(query) str
    }
    
    class SQLAdapter {
        -connection
        +execute_query(query, params) Result
        +execute_write(query, params) Result
        +list_resources() List
        +describe_resource(resource_name) Dict
        +get_resource_stats(resource_name) Dict
        +extract_resource_name(query) str
    }
    
    class MongoAdapter {
        -connection
        +execute_query(query, params) Result
        +execute_write(query, params) Result
        +list_resources() List
        +describe_resource(resource_name) Dict
        +get_resource_stats(resource_name) Dict
        +extract_resource_name(query) str
    }
    
    class RedisAdapter {
        -connection
        +execute_query(query, params) Result
        +execute_write(query, params) Result
        +list_resources() List
        +describe_resource(resource_name) Dict
        +get_resource_stats(resource_name) Dict
        +extract_resource_name(query) str
    }
    
    AdapterFactory ..> AdapterBase : creates
    AdapterBase <|-- SQLAdapter
    AdapterBase <|-- MongoAdapter
    AdapterBase <|-- RedisAdapter
    AdapterBase o-- ConnectionBase : uses
```

## 4. 查询层类图

```mermaid
classDiagram
    class QueryBuilderFactory {
        +create_query_builder(adapter_type) QueryBuilder
    }
    
    class QueryBuilder {
        <<abstract>>
        +select(resource_name, fields) QueryBuilder
        +insert(resource_name, data) QueryBuilder
        +update(resource_name, data, condition) QueryBuilder
        +delete(resource_name, condition) QueryBuilder
        +where(condition) QueryBuilder
        +order_by(fields) QueryBuilder
        +limit(count) QueryBuilder
        +offset(count) QueryBuilder
        +build() Query
    }
    
    class SQLQueryBuilder {
        +select(resource_name, fields) SQLQueryBuilder
        +insert(resource_name, data) SQLQueryBuilder
        +update(resource_name, data, condition) SQLQueryBuilder
        +delete(resource_name, condition) SQLQueryBuilder
        +where(condition) SQLQueryBuilder
        +order_by(fields) SQLQueryBuilder
        +limit(count) SQLQueryBuilder
        +offset(count) SQLQueryBuilder
        +build() SQLQuery
    }
    
    class MongoQueryBuilder {
        +select(resource_name, fields) MongoQueryBuilder
        +insert(resource_name, data) MongoQueryBuilder
        +update(resource_name, data, condition) MongoQueryBuilder
        +delete(resource_name, condition) MongoQueryBuilder
        +where(condition) MongoQueryBuilder
        +order_by(fields) MongoQueryBuilder
        +limit(count) MongoQueryBuilder
        +offset(count) MongoQueryBuilder
        +build() MongoQuery
    }
    
    class RedisCommandBuilder {
        +select(resource_name, fields) RedisCommandBuilder
        +insert(resource_name, data) RedisCommandBuilder
        +update(resource_name, data, condition) RedisCommandBuilder
        +delete(resource_name, condition) RedisCommandBuilder
        +build() RedisCommand
    }
    
    class Query {
        <<abstract>>
        -query_string
        -params
        +get_query_string() str
        +get_params() Dict
    }
    
    class SQLQuery {
        -sql
        -params
        +get_query_string() str
        +get_params() Dict
    }
    
    class MongoQuery {
        -collection
        -operation
        -filter
        -projection
        -sort
        -limit
        -skip
        +get_query_string() str
        +get_params() Dict
    }
    
    class RedisCommand {
        -command
        -key
        -args
        +get_query_string() str
        +get_params() Dict
    }
    
    QueryBuilderFactory ..> QueryBuilder : creates
    QueryBuilder <|-- SQLQueryBuilder
    QueryBuilder <|-- MongoQueryBuilder
    QueryBuilder <|-- RedisCommandBuilder
    QueryBuilder ..> Query : builds
    Query <|-- SQLQuery
    Query <|-- MongoQuery
    Query <|-- RedisCommand
```

## 5. 权限层类图

```mermaid
classDiagram
    class PermissionChecker {
        -config
        +check_permission(connection_name, resource_name, operation_type) bool
        +get_allowed_operations(connection_name, resource_name) List
    }
    
    class OperationValidator {
        +validate_operation(operation_type, resource_name, query) bool
    }
    
    class AuditLogger {
        +log_operation(connection_name, resource_name, operation_type, user, result) None
    }
    
    class PermissionConfig {
        -connections
        +get_connection_config(connection_name) Dict
        +get_resource_permissions(connection_name, resource_name) Dict
        +is_writable(connection_name) bool
    }
    
    PermissionChecker o-- PermissionConfig : uses
    PermissionChecker ..> OperationValidator : uses
    PermissionChecker ..> AuditLogger : uses
```

## 6. API层类图

```mermaid
classDiagram
    class DatabaseClient {
        -connection_manager
        -transaction_manager
        +execute_query(connection_name, query, params) Result
        +execute_write(connection_name, query, params) Result
        +list_tables(connection_name) List
        +describe_table(connection_name, table_name) Dict
        +get_table_stats(connection_name, table_name) Dict
        +begin_transaction(connection_name) Transaction
    }
    
    class ConnectionManager {
        -connection_pool
        -adapter_factory
        +get_connection(connection_name) ConnectionBase
        +get_adapter(connection_name) AdapterBase
        +release_connection(connection) None
        +close_all() None
    }
    
    class TransactionManager {
        -active_transactions
        +begin_transaction(connection) Transaction
        +commit_transaction(transaction) None
        +rollback_transaction(transaction) None
    }
    
    class Transaction {
        -connection
        -is_active
        +commit() None
        +rollback() None
    }
    
    class Result {
        -data
        -affected_rows
        -last_insert_id
        +get_data() List
        +get_affected_rows() int
        +get_last_insert_id() int
    }
    
    DatabaseClient o-- ConnectionManager : uses
    DatabaseClient o-- TransactionManager : uses
    TransactionManager o-- Transaction : manages
    DatabaseClient ..> Result : returns
```

## 7. 错误处理类图

```mermaid
classDiagram
    class DatabaseError {
        <<abstract>>
        -message
        -cause
        +get_message() str
        +get_cause() Exception
    }
    
    class ConnectionError {
        -connection_name
        +get_connection_name() str
    }
    
    class AuthenticationError {
        -connection_name
        +get_connection_name() str
    }
    
    class ResourceNotFoundError {
        -resource_name
        +get_resource_name() str
    }
    
    class DuplicateKeyError {
        -resource_name
        -key
        +get_resource_name() str
        +get_key() str
    }
    
    class PermissionError {
        -connection_name
        -resource_name
        -operation_type
        +get_connection_name() str
        +get_resource_name() str
        +get_operation_type() str
    }
    
    class QueryError {
        -query
        +get_query() str
    }
    
    class TransactionError {
        -transaction_id
        +get_transaction_id() str
    }
    
    class RetryHandler {
        -max_retries
        -retry_interval
        -retry_strategy
        +should_retry(error, attempt) bool
        +get_retry_interval(attempt) int
        +execute_with_retry(func, *args, **kwargs) Result
    }
    
    DatabaseError <|-- ConnectionError
    DatabaseError <|-- AuthenticationError
    DatabaseError <|-- ResourceNotFoundError
    DatabaseError <|-- DuplicateKeyError
    DatabaseError <|-- PermissionError
    DatabaseError <|-- QueryError
    DatabaseError <|-- TransactionError
    RetryHandler ..> DatabaseError : handles
```

## 8. 配置管理类图

```mermaid
classDiagram
    class ConfigManager {
        -config_path
        -config
        +load_config() None
        +get_connection_config(connection_name) Dict
        +get_all_connections() List
        +validate_config() bool
    }
    
    class ConnectionConfig {
        -name
        -type
        -params
        -writable
        -write_permissions
        +get_name() str
        +get_type() str
        +get_params() Dict
        +is_writable() bool
        +get_write_permissions() Dict
    }
    
    class WritePermission {
        -default_policy
        -resources
        +get_default_policy() str
        +get_resource_permissions(resource_name) Dict
        +is_operation_allowed(resource_name, operation_type) bool
    }
    
    ConfigManager o-- ConnectionConfig : manages
    ConnectionConfig o-- WritePermission : contains
```

## 9. 组件间关系

```mermaid
classDiagram
    DatabaseClient ..> ConnectionManager : uses
    ConnectionManager ..> ConnectionPool : uses
    ConnectionManager ..> AdapterFactory : uses
    ConnectionPool ..> ConnectionFactory : uses
    AdapterFactory ..> ConnectionBase : uses
    DatabaseClient ..> QueryBuilderFactory : uses
    DatabaseClient ..> PermissionChecker : uses
    PermissionChecker ..> ConfigManager : uses
    DatabaseClient ..> RetryHandler : uses
    RetryHandler ..> DatabaseError : handles
```

## 10. 总结

以上类图展示了多数据库支持架构的主要组件和它们之间的关系。这种设计提供了良好的分层和抽象，使得系统可以灵活地支持不同类型的数据库，同时保持统一的接口和一致的用户体验。
