import json

import requests
# r=requests.get('https://www.baidu.com/')
# print(r.text)


# R = requests.request('GET','https://www.baidu.com/')
# print(R.text)
#get大小写一样，request方法的第一个参数是请求方法，可以是'get'、'post'等，大小写不敏感。第二个参数是URL，返回一个Response对象。可以通过Response对象的text属性获取响应内容。

url ='https://www.baidu.com/'
method ='get'
r = requests.request(method, url)
print(r.status_code)  # 打印响应状态码 200表示成功,400表示请求错误，500表示服务器错误等
# print(r.text)  # 打印响应内容
print(json.loads(r.text, encoding='utf-8'))  # 如果响应内容是JSON格式，可以使用json()方法解析成Python对象



# print(r.text)
# print(r.headers)
# 打印请求的URL


# with open('baidu.md', 'w', encoding='utf-8') as f:
    # json.dump(r.status_code,f, ensure_ascii=False, indent=2)


