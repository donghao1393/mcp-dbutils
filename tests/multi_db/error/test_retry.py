"""
测试重试处理器

这个模块测试多数据库支持架构中的重试处理器。
"""

from unittest.mock import Mock, patch

import pytest

from mcp_dbutils.multi_db.error.exceptions import ConnectionError, QueryError
from mcp_dbutils.multi_db.error.retry import RetryHandler


class TestRetryHandler:
    """测试RetryHandler类"""

    def test_init(self):
        """测试初始化"""
        handler = RetryHandler()
        assert handler.max_retries == 3
        assert handler.initial_delay == 0.1
        assert handler.max_delay == 5.0
        assert handler.backoff_factor == 2.0
        assert ConnectionError in handler.retryable_errors

    def test_init_with_custom_params(self):
        """测试自定义参数的初始化"""
        handler = RetryHandler(
            max_retries=5,
            initial_delay=0.2,
            max_delay=10.0,
            backoff_factor=3.0
        )
        assert handler.max_retries == 5
        assert handler.initial_delay == 0.2
        assert handler.max_delay == 10.0
        assert handler.backoff_factor == 3.0

    def test_register_retryable_error(self):
        """测试注册可重试的错误类型"""
        handler = RetryHandler()
        assert QueryError not in handler.retryable_errors
        handler.register_retryable_error(QueryError)
        assert QueryError in handler.retryable_errors

    def test_unregister_retryable_error(self):
        """测试取消注册可重试的错误类型"""
        handler = RetryHandler()
        assert ConnectionError in handler.retryable_errors
        handler.unregister_retryable_error(ConnectionError)
        assert ConnectionError not in handler.retryable_errors

    def test_should_retry_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        handler = RetryHandler(max_retries=3)
        error = ConnectionError("Connection error")
        assert handler.should_retry(error, 0)  # 第一次尝试
        assert handler.should_retry(error, 1)  # 第二次尝试
        assert handler.should_retry(error, 2)  # 第三次尝试
        assert not handler.should_retry(error, 3)  # 超过最大重试次数

    def test_should_retry_non_retryable_error(self):
        """测试不可重试的错误类型"""
        handler = RetryHandler()
        error = QueryError("Query error")
        assert not handler.should_retry(error, 0)

    def test_get_retry_delay(self):
        """测试获取重试延迟时间"""
        handler = RetryHandler(initial_delay=0.1, backoff_factor=2.0, max_delay=5.0)
        assert handler.get_retry_delay(0) == 0.1  # 第一次重试
        assert handler.get_retry_delay(1) == 0.2  # 第二次重试
        assert handler.get_retry_delay(2) == 0.4  # 第三次重试
        assert handler.get_retry_delay(3) == 0.8  # 第四次重试
        assert handler.get_retry_delay(10) == 5.0  # 超过最大延迟

    @patch('time.sleep')
    def test_execute_with_retry_success(self, mock_sleep):
        """测试成功执行函数"""
        handler = RetryHandler()
        func = Mock(return_value="success")
        result = handler.execute_with_retry(func, "arg1", arg2="arg2")
        assert result == "success"
        func.assert_called_once_with("arg1", arg2="arg2")
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    def test_execute_with_retry_success_after_retry(self, mock_sleep):
        """测试重试后成功执行函数"""
        handler = RetryHandler()
        func = Mock(side_effect=[ConnectionError("Connection error"), "success"])
        result = handler.execute_with_retry(func)
        assert result == "success"
        assert func.call_count == 2
        mock_sleep.assert_called_once()

    @patch('time.sleep')
    def test_execute_with_retry_all_failed(self, mock_sleep):
        """测试所有重试都失败"""
        handler = RetryHandler(max_retries=2)
        error = ConnectionError("Connection error")
        # 由于循环条件是 attempt < max_retries，所以只会尝试初始调用 + max_retries 次
        # 即总共 1 + 2 = 3 次，但由于第二次重试失败后就会抛出异常，所以实际只会调用 1 + 1 = 2 次
        func = Mock(side_effect=[error, error])
        with pytest.raises(ConnectionError) as excinfo:
            handler.execute_with_retry(func)
        assert str(excinfo.value) == "Connection error"
        assert func.call_count == 2
        # 由于循环条件是 attempt < max_retries，所以会调用两次sleep
        # 第一次是初始调用失败后，第二次是第一次重试失败后
        assert mock_sleep.call_count == 2

    @patch('time.sleep')
    def test_execute_with_retry_non_retryable_error(self, mock_sleep):
        """测试不可重试的错误"""
        handler = RetryHandler()
        error = QueryError("Query error")
        func = Mock(side_effect=error)
        with pytest.raises(QueryError) as excinfo:
            handler.execute_with_retry(func)
        assert str(excinfo.value) == "Query error"
        func.assert_called_once()
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    def test_retry_decorator(self, mock_sleep):
        """测试重试装饰器"""
        handler = RetryHandler()
        func = Mock(side_effect=[ConnectionError("Connection error"), "success"])

        # 使用装饰器
        decorated_func = handler.retry()(func)
        result = decorated_func("arg1", arg2="arg2")

        assert result == "success"
        assert func.call_count == 2
        # 检查调用参数，而不是比较Mock对象
        assert func.call_args_list == [
            ((("arg1",), {"arg2": "arg2"})),
            ((("arg1",), {"arg2": "arg2"}))
        ]
        mock_sleep.assert_called_once()

    @patch('time.sleep')
    def test_retry_decorator_with_custom_params(self, mock_sleep):
        """测试带自定义参数的重试装饰器"""
        handler = RetryHandler()
        func = Mock(side_effect=[ConnectionError("Connection error"), ConnectionError("Connection error"), "success"])

        # 使用带自定义参数的装饰器
        decorated_func = handler.retry(max_retries=5, initial_delay=0.2)(func)
        result = decorated_func()

        assert result == "success"
        assert func.call_count == 3
        assert mock_sleep.call_count == 2
