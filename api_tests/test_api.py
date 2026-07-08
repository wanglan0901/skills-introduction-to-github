"""API 测试示例 - 使用 Playwright"""
import pytest
from playwright.sync_api import APIRequestContext


class TestAPIBasics:
    """基础 API 测试"""

    def test_get请求(self, api_request: APIRequestContext):
        """测试 GET 请求"""
        response = api_request.get("https://jsonplaceholder.typicode.com/posts/1")
        assert response.status == 200
        data = response.json()
        assert "title" in data
        assert data["userId"] == 1

    def test_get列表(self, api_request: APIRequestContext):
        """测试获取列表"""
        response = api_request.get("https://jsonplaceholder.typicode.com/posts")
        assert response.status == 200
        data = response.json()
        assert len(data) > 0

    def test_post请求(self, api_request: APIRequestContext):
        """测试 POST 请求"""
        payload = {
            "title": "Test Title",
            "body": "Test Body",
            "userId": 1
        }
        response = api_request.post("https://jsonplaceholder.typicode.com/posts", data=payload)
        assert response.status == 201
        data = response.json()
        assert data["title"] == "Test Title"

    def test_put请求(self, api_request: APIRequestContext):
        """测试 PUT 请求（更新）"""
        payload = {
            "id": 1,
            "title": "Updated Title",
            "body": "Updated Body",
            "userId": 1
        }
        response = api_request.put("https://jsonplaceholder.typicode.com/posts/1", data=payload)
        assert response.status == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_delete请求(self, api_request: APIRequestContext):
        """测试 DELETE 请求"""
        response = api_request.delete("https://jsonplaceholder.typicode.com/posts/1")
        assert response.status == 200


class TestAPIHeaders:
    """API 请求头测试"""

    def test自定义请求头(self, api_request: APIRequestContext):
        """测试自定义请求头"""
        response = api_request.get(
            "https://jsonplaceholder.typicode.com/posts/1",
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status == 200

    def test验证响应头(self, api_request: APIRequestContext):
        """测试验证响应头"""
        response = api_request.get("https://jsonplaceholder.typicode.com/posts/1")
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
