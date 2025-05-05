"""
重试处理器实现

这个模块实现了重试处理器，用于处理临时性错误。
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from .exceptions import ConnectionError, DatabaseError


class RetryHandler:
    """
    重试处理器类
    
    这个类负责处理临时性错误，使用指数退避算法进行重试。
    """
    
    def __init__(self, max_retries: int = 3, initial_delay: float = 0.1, 
                 max_delay: float = 5.0, backoff_factor: float = 2.0):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            backoff_factor: 退避因子
        """
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retryable_errors = {ConnectionError}
        
    def register_retryable_error(self, error_type: Type[DatabaseError]) -> None:
        """
        注册可重试的错误类型
        
        Args:
            error_type: 错误类型
        """
        self.retryable_errors.add(error_type)
        
    def unregister_retryable_error(self, error_type: Type[DatabaseError]) -> None:
        """
        取消注册可重试的错误类型
        
        Args:
            error_type: 错误类型
        """
        if error_type in self.retryable_errors:
            self.retryable_errors.remove(error_type)
            
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: 异常
            attempt: 当前尝试次数
            
        Returns:
            bool: 如果应该重试，则返回True，否则返回False
        """
        # 检查是否超过最大重试次数
        if attempt >= self.max_retries:
            return False
            
        # 检查是否是可重试的错误类型
        for error_type in self.retryable_errors:
            if isinstance(error, error_type):
                return True
                
        return False
        
    def get_retry_delay(self, attempt: int) -> float:
        """
        获取重试延迟时间
        
        使用指数退避算法计算重试延迟时间。
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            float: 延迟时间（秒）
        """
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)
        
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        使用重试机制执行函数
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Any: 函数返回值
            
        Raises:
            Exception: 如果所有重试都失败，则抛出最后一个异常
        """
        attempt = 0
        last_error = None
        
        while attempt <= self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if self.should_retry(e, attempt):
                    delay = self.get_retry_delay(attempt)
                    self.logger.warning(
                        f"Retry {attempt + 1}/{self.max_retries} after {delay:.2f}s due to: {str(e)}"
                    )
                    time.sleep(delay)
                    attempt += 1
                else:
                    break
                    
        # 所有重试都失败，抛出最后一个异常
        if last_error:
            self.logger.error(f"All retries failed: {str(last_error)}")
            raise last_error
            
        # 这种情况不应该发生
        raise RuntimeError("Unexpected error in retry handler")
        
    def retry(self, max_retries: Optional[int] = None, 
              initial_delay: Optional[float] = None,
              max_delay: Optional[float] = None,
              backoff_factor: Optional[float] = None):
        """
        重试装饰器
        
        用于装饰需要重试的函数。
        
        Args:
            max_retries: 最大重试次数，如果为None，则使用默认值
            initial_delay: 初始延迟时间（秒），如果为None，则使用默认值
            max_delay: 最大延迟时间（秒），如果为None，则使用默认值
            backoff_factor: 退避因子，如果为None，则使用默认值
            
        Returns:
            Callable: 装饰器
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 创建一个临时的重试处理器，使用指定的参数
                handler = RetryHandler(
                    max_retries=max_retries or self.max_retries,
                    initial_delay=initial_delay or self.initial_delay,
                    max_delay=max_delay or self.max_delay,
                    backoff_factor=backoff_factor or self.backoff_factor
                )
                
                # 复制可重试的错误类型
                handler.retryable_errors = self.retryable_errors.copy()
                
                # 使用重试处理器执行函数
                return handler.execute_with_retry(func, *args, **kwargs)
            return wrapper
        return decorator
