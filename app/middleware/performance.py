"""
性能监控中间件
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# 配置性能日志
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)

# 如果没有处理器，添加一个控制台处理器
if not perf_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    perf_logger.addHandler(handler)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件，记录请求处理时间"""
    
    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求开始
        method = request.method
        url = str(request.url)
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 添加性能头部
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录性能日志
        status_code = response.status_code
        
        if process_time > self.slow_request_threshold:
            perf_logger.warning(
                f"慢请求 - {method} {url} - {status_code} - {process_time:.3f}s"
            )
        else:
            perf_logger.info(
                f"{method} {url} - {status_code} - {process_time:.3f}s"
            )
        
        return response

class RequestLimitMiddleware(BaseHTTPMiddleware):
    """简单的请求限制中间件"""
    
    def __init__(self, app, max_requests_per_minute: int = 60):
        super().__init__(app)
        self.max_requests = max_requests_per_minute
        self.requests = {}  # 存储IP和时间戳
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_time = time.time()
        
        # 清理过期记录
        if client_ip in self.requests:
            self.requests[client_ip] = [
                timestamp for timestamp in self.requests[client_ip]
                if current_time - timestamp < 60  # 保留1分钟内的记录
            ]
        else:
            self.requests[client_ip] = []
        
        # 检查请求频率
        if len(self.requests[client_ip]) >= self.max_requests:
            return Response(
                content="请求过于频繁，请稍后再试",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # 记录当前请求
        self.requests[client_ip].append(current_time)
        
        # 处理请求
        response = await call_next(request)
        return response
