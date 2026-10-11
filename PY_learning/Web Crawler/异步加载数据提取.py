"""
一些网页的数据是通过异步加载的，直接使用requests库获取网页源代码是无法获取到这些数据的。
这时我们可以通过分析网页的请求，找到数据的接口地址，直接访问接口地址来获取数据。
"""

from urllib import response
import requests
url = "https://push2.eastmoney.com/api/qt/pkyd/get?cb=jQuery37109006881820001265_1776512717106&ut=fa5fd1943c7b386f172d6893dbfba10b&fields=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6%2Cf7&lmt=50&_=1776512717164"
response = requests.get(url)
print(response.text)