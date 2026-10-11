import re
from idna import decode
import requests

url ="https://www.baidu.com/"
headers={"User-Agent":"Siva"}
response = requests.get(url,headers=headers)
# print(response.text)
# print(response.content)# 以二进制的形式返回响应内容
"""
bytes 和str的的转换
bytes 转 str 用 decode()方法
str 转 bytes 用 encode()方法 
"""
# print(response.content.decode("utf-8"))# 将二进制的内容转换成字符串


# print(response.status_code) # 响应状态码
# print(response.headers) # 响应头
# print(response.cookies) # 响应的cookie

# print(response.request.headers) # 请求头

