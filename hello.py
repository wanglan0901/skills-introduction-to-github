#!/usr/bin/env python3
"""Hello World 示例程序"""

def greet(name: str) -> str:
    return f"你好, {name}!"

if __name__ == "__main__":
    message = greet("Trae 用户")
    print(message)
    print("Python 环境已成功配置!")
