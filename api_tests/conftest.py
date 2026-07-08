"""API 测试 fixture 配置"""
import pytest
import os
import sys

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def base_url():
    """被测系统基础 URL"""
    return os.environ.get("BASE_URL", "https://buffalo-dev.shuishoukefu.com")


@pytest.fixture(scope="session")
def auth_token(base_url):
    """登录获取认证 token（如需 token 认证的话）"""
    import requests
    login_url = f"{base_url}/api/login"
    payload = {
        "email": "wanglan1@shuishoukefu.com",
        "password": "123"
    }
    resp = requests.post(login_url, json=payload, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        token = data.get("token") or data.get("data", {}).get("token") or ""
        print(f"✓ 登录成功，token={token[:20]}...")
        return token
    else:
        print(f"⚠️ 登录失败 ({resp.status_code}): {resp.text[:200]}")
        return ""


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """带认证信息的请求头"""
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers
