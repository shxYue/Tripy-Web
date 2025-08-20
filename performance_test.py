"""
性能测试脚本
用于测试API性能和负载能力
"""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
import json

class PerformanceTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求并记录性能指标"""
        url = f"{self.base_url}{path}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                content = await response.text()
                end_time = time.time()
                
                return {
                    "status_code": response.status,
                    "response_time": end_time - start_time,
                    "content_length": len(content),
                    "success": 200 <= response.status < 300,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            end_time = time.time()
            return {
                "status_code": 0,
                "response_time": end_time - start_time,
                "content_length": 0,
                "success": False,
                "error": str(e),
                "headers": {}
            }
    
    async def load_test(self, method: str, path: str, concurrent_users: int = 10, 
                       duration_seconds: int = 30, **kwargs) -> Dict[str, Any]:
        """负载测试"""
        print(f"开始负载测试: {method} {path}")
        print(f"并发用户: {concurrent_users}, 持续时间: {duration_seconds}s")
        
        results = []
        start_time = time.time()
        
        async def worker():
            while time.time() - start_time < duration_seconds:
                result = await self.make_request(method, path, **kwargs)
                results.append(result)
                await asyncio.sleep(0.01)  # 短暂延迟避免过度压力
        
        # 启动并发worker
        tasks = [asyncio.create_task(worker()) for _ in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        # 计算统计信息
        if not results:
            return {"error": "没有收到任何响应"}
        
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        
        stats = {
            "total_requests": len(results),
            "successful_requests": success_count,
            "failed_requests": len(results) - success_count,
            "success_rate": success_count / len(results) * 100,
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": statistics.median(response_times),
            "requests_per_second": len(results) / duration_seconds,
        }
        
        if len(response_times) > 1:
            stats["stddev_response_time"] = statistics.stdev(response_times)
        
        return stats
    
    async def test_basic_endpoints(self) -> Dict[str, Any]:
        """测试基本端点性能"""
        endpoints = [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/static/pages/index.html"),
        ]
        
        results = {}
        for method, path in endpoints:
            print(f"测试 {method} {path}")
            result = await self.make_request(method, path)
            results[f"{method} {path}"] = result
            print(f"  状态码: {result['status_code']}, 响应时间: {result['response_time']:.3f}s")
        
        return results

async def main():
    """主测试函数"""
    print("=== Tripy-Web 性能测试 ===\n")
    
    async with PerformanceTester() as tester:
        # 基本端点测试
        print("1. 基本端点测试")
        basic_results = await tester.test_basic_endpoints()
        print()
        
        # 健康检查负载测试
        print("2. 健康检查负载测试")
        health_load = await tester.load_test("GET", "/health", concurrent_users=5, duration_seconds=10)
        print(f"  总请求数: {health_load.get('total_requests', 0)}")
        print(f"  成功率: {health_load.get('success_rate', 0):.1f}%")
        print(f"  平均响应时间: {health_load.get('avg_response_time', 0):.3f}s")
        print(f"  每秒请求数: {health_load.get('requests_per_second', 0):.1f}")
        print()
        
        # 静态文件负载测试
        print("3. 静态文件负载测试")
        static_load = await tester.load_test("GET", "/static/pages/index.html", 
                                           concurrent_users=10, duration_seconds=10)
        print(f"  总请求数: {static_load.get('total_requests', 0)}")
        print(f"  成功率: {static_load.get('success_rate', 0):.1f}%")
        print(f"  平均响应时间: {static_load.get('avg_response_time', 0):.3f}s")
        print(f"  每秒请求数: {static_load.get('requests_per_second', 0):.1f}")
        print()
        
        # 保存详细结果
        all_results = {
            "basic_endpoints": basic_results,
            "health_load_test": health_load,
            "static_load_test": static_load,
            "timestamp": time.time()
        }
        
        with open("performance_test_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print("性能测试完成！详细结果已保存到 performance_test_results.json")

if __name__ == "__main__":
    print("请确保 Tripy-Web 服务正在运行在 http://127.0.0.1:8000")
    print("按 Enter 开始测试...")
    input()
    
    asyncio.run(main())
