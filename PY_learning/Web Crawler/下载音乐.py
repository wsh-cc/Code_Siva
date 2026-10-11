import requests

from package.SAVEPATH import save_path_inDownload

url= "https://lv-sycdn.kuwo.cn/0ab4ea9088b28cda6fcfa5caeab135ce/69e1c225/resource/30106/trackmedia/M500003AEHYl2DdwGy.mp3"
headers={'User-Agent': "Siva", 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}

response = requests.get(url, headers=headers)

# print(response.request.headers)
with open(save_path_inDownload('M500003AEHYl2DdwGy.mp3'), 'wb') as f:
    f.write(response.content)