import requests
import pytest
import json

# 测试环境的URL
BASE_URL = "https://api-gateway-dev.shuishoukefu.com/shake/"

# 测试接口的路径
API_PATH = "pigeon/v1/merchant/6639"

# 请求头
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiJqd3QiLCJpc3MiOiJtZWNoYXQiLCJpYXQiOjE3Mzg4MTE2OTAsImF1ZCI6IlBDIiwiZXhwIjoxNzM5MDcwODkwLCJzdWIiOiIzMHU3amtkeGVzeGpyOXFjZXMzbDZnMm9zdDA3dnU3NiJ9.Vndpruf9qIV8VoJE2LAup0c90GRB266Dk1wnTdiWKi1PVH2Hq80MER_OU0XkomAlTxA05G2L8LLyc8jM5IdwXw",
    "Content-Type": "application/json;charset=UTF-8"
}

# 测试用例：验证接口是否能够正常查询到商家信息
def test_get_merchant_info():
    # 构造完整的请求URL
    global response_json
    url = BASE_URL + API_PATH

    # 发送GET请求
    response = requests.get(url, headers=HEADERS)

    data=response.json()
    data_dumps=json.dumps(data)

    # 验证状态码是否为200
    assert response.status_code == 200

    # 验证响应体是否为JSON格式
    try:
        response_json = response.json()
        assert isinstance(response_json, dict), "Response is not a valid JSON object"
    except json.JSONDecodeError:
        pytest.fail("Response is not a valid JSON format")

    # 验证响应体中是否包含商家信息
    assert 'merchantName' in data_dumps