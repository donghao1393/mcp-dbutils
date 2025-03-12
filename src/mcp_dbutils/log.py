"""日志处理模块"""

import sys
from datetime import datetime
from typing import Callable

def create_logger(name: str, is_debug: bool = False) -> Callable:
    """创建stderr日志函数，用于本地调试
    Args:
        name: 服务名称
        is_debug: 是否输出debug级别日志
    """
    def log(level: str, message: str):
        """输出日志到stderr
        Args:
            level: 日志级别 (debug/info/warning/error)
            message: 日志内容
        """
        if level == "debug" and not is_debug:
            return

        timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
        log_message = f"{timestamp} [{name}] [{level}] {message}"

        # 输出到stderr
        print(log_message, file=sys.stderr, flush=True)

    return log
