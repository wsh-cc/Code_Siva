import http
import requests


"""
模拟登录：访问需要在登陆之后才能访问的页面，必须先模拟登录，获取到登录成功后的cookie，然后在后续的请求中携带这个cookie，才能访问这些页面。
"""
# 1 以字典的形式传递cookie
# cookies = {"..."}
# requests.get(cookies = cookies)

#2 以字符串的形式传递cookie
# headers = {
#    "User-Agent": "..."
#    "Accept": "..."
#    "Cookie": "..."#大写,直接从登陆成功后的cookies中复制过来
# }
# 

# 3 使用requests.session()方法创建一个会话对象，这个对象会自动保存和发送cookie，适合需要多次请求的场景。
# requests.session()
# http = requests.session()# 创建一个请求对象
# response = http.post(url= ,data = , headers=)# 发送请求
url = "https://passport.lanqiao.cn/login/?action=login&dialog=0&usertype=0&auth_type=login&from=dasai&backurl=https%3A%2F%2Fdasai.lanqiao.cn%2F"
data ={

    "login_str": '1',
    "password": "1"
}

http = requests.session()
response = http.get(url=url, data=data,headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"})
print(response.text)

# url = "https://fanyi.baidu.com/mtpe-individual/transText?ext_channel=Aldtype"
# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"}
# params = {
#     "kw": "a"
# }
# response = requests.get(url=url, headers=headers, params=params)
# print(response.content.decode())


# post请求传递参数



