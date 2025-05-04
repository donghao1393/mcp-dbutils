"""审计日志系统

记录所有数据库写操作，提供审计和追踪功能。
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

# 设置审计日志记录器
audit_logger = logging.getLogger("mcp_dbutils.audit")
audit_logger.setLevel(logging.INFO)

# 内存缓冲区，保存最近的日志记录
_memory_buffer: List[Dict[str, Any]] = []
_memory_buffer_size = 1000  # 默认缓冲区大小

# 审计日志配置
_audit_config = {
    "enabled": True,
    "file_storage": {
        "enabled": True,
        "path": "logs/audit",
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 10
    },
    "content": {
        "sanitize_sql": True,
        "include_user_context": True
    }
}


def configure_audit_logging(config: Dict[str, Any]) -> None:
    """配置审计日志系统
    
    Args:
        config: 审计日志配置
    """
    global _audit_config, _memory_buffer_size
    
    if config:
        _audit_config.update(config)
        
        # 更新内存缓冲区大小
        if "memory_buffer" in config and "size" in config["memory_buffer"]:
            _memory_buffer_size = config["memory_buffer"]["size"]
            
        # 配置文件处理器
        if _audit_config["enabled"] and _audit_config["file_storage"]["enabled"]:
            _setup_file_handler()


def _setup_file_handler() -> None:
    """设置文件日志处理器"""
    log_dir = _audit_config["file_storage"]["path"]
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(
        f"{log_dir}/dbutils-audit.log",
        mode="a",
        encoding="utf-8"
    )
    
    # 设置格式
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    file_handler.setFormatter(formatter)
    
    # 添加到记录器
    audit_logger.addHandler(file_handler)


def _sanitize_sql(sql: str) -> str:
    """对SQL语句进行脱敏处理
    
    Args:
        sql: SQL语句
        
    Returns:
        脱敏后的SQL语句
    """
    if not _audit_config["content"]["sanitize_sql"]:
        return sql
        
    # 简单的脱敏处理，替换VALUES子句中的值
    import re
    
    # 替换INSERT语句中的VALUES
    sanitized = re.sub(
        r"VALUES\s*\((.*?)\)", 
        "VALUES (?)", 
        sql, 
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 替换WHERE子句中的值
    sanitized = re.sub(
        r"(WHERE\s+\w+\s*=\s*)('[^']*'|\d+)", 
        r"\1?", 
        sanitized, 
        flags=re.IGNORECASE
    )
    
    return sanitized


def _get_user_context() -> Optional[str]:
    """获取用户上下文
    
    Returns:
        用户上下文信息
    """
    if not _audit_config["content"]["include_user_context"]:
        return None
        
    # 这里可以添加获取用户上下文的逻辑
    # 例如从环境变量、请求头等获取
    return None


def log_write_operation(
    connection_name: str,
    table_name: str,
    operation_type: str,
    sql: str,
    affected_rows: int,
    execution_time: float,
    status: str = "SUCCESS",
    error_message: Optional[str] = None
) -> None:
    """记录写操作到审计日志
    
    Args:
        connection_name: 数据库连接名称
        table_name: 表名
        operation_type: 操作类型（INSERT、UPDATE、DELETE）
        sql: SQL语句
        affected_rows: 影响的行数
        execution_time: 执行时间（毫秒）
        status: 操作结果（SUCCESS、FAILED）
        error_message: 错误信息（如果失败）
    """
    if not _audit_config["enabled"]:
        return
        
    # 创建日志记录
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "connection_name": connection_name,
        "table_name": table_name,
        "operation_type": operation_type,
        "sql_statement": _sanitize_sql(sql),
        "affected_rows": affected_rows,
        "status": status,
        "execution_time": execution_time,
        "user_context": _get_user_context()
    }
    
    if error_message:
        log_entry["error_message"] = error_message
    
    # 添加到内存缓冲区
    _memory_buffer.append(log_entry)
    if len(_memory_buffer) > _memory_buffer_size:
        _memory_buffer.pop(0)  # 移除最旧的记录
    
    # 写入日志文件
    if _audit_config["file_storage"]["enabled"]:
        audit_logger.info(json.dumps(log_entry))


def get_logs(
    connection_name: Optional[str] = None,
    table_name: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    operation_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """获取审计日志
    
    Args:
        connection_name: 数据库连接名称
        table_name: 表名
        start_time: 开始时间（ISO 8601格式）
        end_time: 结束时间（ISO 8601格式）
        operation_type: 操作类型（INSERT、UPDATE、DELETE）
        status: 操作状态（SUCCESS、FAILED）
        limit: 返回记录数量限制
        
    Returns:
        审计日志记录列表
    """
    # 从内存缓冲区获取日志
    logs = _memory_buffer.copy()
    
    # 应用过滤条件
    filtered_logs = []
    for log in logs:
        # 连接名称过滤
        if connection_name and log["connection_name"] != connection_name:
            continue
            
        # 表名过滤
        if table_name and log["table_name"] != table_name:
            continue
            
        # 时间范围过滤
        if start_time and log["timestamp"] < start_time:
            continue
        if end_time and log["timestamp"] > end_time:
            continue
            
        # 操作类型过滤
        if operation_type and log["operation_type"] != operation_type:
            continue
            
        # 状态过滤
        if status and log["status"] != status:
            continue
            
        filtered_logs.append(log)
        
        # 应用限制
        if len(filtered_logs) >= limit:
            break
    
    return filtered_logs


def format_logs(logs: List[Dict[str, Any]]) -> str:
    """格式化审计日志
    
    Args:
        logs: 审计日志记录列表
        
    Returns:
        格式化后的审计日志
    """
    if not logs:
        return "No audit logs found."
        
    formatted = ["Audit Logs:", "==========="]
    
    for log in logs:
        formatted.extend([
            f"\nTimestamp: {log['timestamp']}",
            f"Connection: {log['connection_name']}",
            f"Table: {log['table_name']}",
            f"Operation: {log['operation_type']}",
            f"Status: {log['status']}",
            f"Affected Rows: {log['affected_rows']}",
            f"Execution Time: {log['execution_time']:.2f}ms",
            f"SQL: {log['sql_statement']}"
        ])
        
        if "error_message" in log:
            formatted.append(f"Error: {log['error_message']}")
            
        if log.get("user_context"):
            formatted.append(f"User Context: {log['user_context']}")
    
    return "\n".join(formatted)
