import requests
from os import path

from package.SAVEPATH import  save_path_inDownload

url = "https://emoji.cdn.bcebos.com/yige-aigc/index_aigc/final/toolspics/0.png"

headers={'User-Agent': 'Siva', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}

response = requests.get(url, headers=headers)


# print(response.request.headers)

with open(save_path_inDownload('0.png'), 'wb') as f:
    f.write(response.content)#content属性以二进制的形式返回响应内容，适合保存图片等二进制文件
