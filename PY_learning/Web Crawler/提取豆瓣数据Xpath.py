import requests
from lxml import etree

import threading # 使用线程优化

from package.SAVEPATH import save_path_inDownload
class Douban:
    urls=[]
    # info=[]
    headers={'User-Agent': 'Siva', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
    
    def __init__(self):
         self.url="https://movie.douban.com/top250?start={}&filter="
         for i in range(10):
            self.urls.append(self.url.format(i*25))
      
    def get_data(self,url):
            

            response = requests.get(url,headers=self.headers)
            # page = response.content.decode()# 将二进制的内容转换成字符串
            # html =etree.HTML(page)# 将字符串转换成HTML对象
            html = etree.HTML(response.content.decode())
            # data_list = html.xpath('*//ol//li')# 使用XPath表达式提取电影数据，返回一个包含所有电影数据的列表
            
            data_list =html.xpath('*//ol//li')
            for data in data_list:
                title = data.xpath('.//span[@class="title"][1]/text()')
                rating = data.xpath('.//span[@class="rating_num"]/text()')
                nunmber = data.xpath('.//div[@class="bd"]/div/span[4]/text()')
                judge = data.xpath('.//div[@class="bd"]/p/span/text()')

                print('电影名称',*title,'\n电影评分:',*rating,'\n评价人数:',*nunmber)
                print(f"电影评价:",*judge)
                print()
               
                with open(save_path_inDownload("doubantop250.txt"), 'a', encoding='utf-8') as f:
                    f.write(f"电影名称: {''.join(title)}\n电影评分: {''.join(rating)}\n评价人数: {''.join(nunmber)}\n电影评价: {''.join(judge)}\n\n")

    def run(self):
        Threads = []#这样会无序
        for url in self.urls:
            t=threading.Thread(target=self.get_data, args=(url,))
            t.start()
            Threads.append(t)
        for t in Threads:
            t.join()
if __name__ == "__main__":
    # response = requests.get("https://movie.douban.com/top250?start=0&filter=")
    # print(response.request.headers)
    bd = Douban()
    bd.run()
    