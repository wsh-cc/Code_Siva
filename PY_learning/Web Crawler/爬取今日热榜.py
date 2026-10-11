"""
爬取今日热榜
爬取网址：https://rebang.today/home
爬取内容：每日热点新闻标题、信息来源网址、信息来源、热度
"""
from lxml import etree
from selenium import webdriver
import time
from package import SAVEPATH


url = "https://rebang.today/home"
driver = webdriver.Edge()
driver.get(url)

"""
这种方法可以一直滚动直至底部
"""
last_height = 0
stable_count = 0
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #execute_script()方法可以执行JavaScript代码，这里是将页面滚动到底部
    #window.scrollTo()方法可以将页面滚动到指定的位置，这里是将页面滚动到底部，
    #document.body.scrollHeight是页面的总高度
    time.sleep(0.3)
    #driver.implicitly_wait(10)不行因为他只会在用find_element()时才生效

    new_height = driver.execute_script("return document.body.scrollHeight")
    # return document.body.scrollHeight是获取页面的总高度
   
    if new_height == last_height:
        stable_count += 1
        if stable_count >= 3:#最多允许3次，高度还不变
            break
    else:
        stable_count = 0
        last_height = new_height
"""
简单方法
CNT=0
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    CNT+=1
    time.sleep(0.5)
    if CNT>=10:#最多滚动10次
       break
"""
driver.implicitly_wait(10)
html = etree.HTML(driver.page_source)
with open(SAVEPATH.save_path_inDownload("今日热榜.txt"),'w',encoding = 'utf-8') as f:
    f.write(f"{time.strftime('%Y-%m-%d')}今日热榜\n")
    data_list = html.xpath('//*[contains(@class, "bg-primary-200")]//div//li')
    cnt = 0
    for data in data_list:
        news = data.xpath('.//*[@class="text-base multirow-ellipsis-2"]/text()')
        Website = data.xpath('.//@href')
        From = data.xpath('.//*[@class="arco-tag-content"]/text()')
        hottype = data.xpath('.//*[@class="shrink-0 text-text-300 dark:text-textDark-300"]/text()')
        cnt += 1
        f.write("——"*50+'\n')
        f.write(f"|  热点{cnt}:{news[0].strip()} \n|  信息来源网址:{Website[0].strip()}\n|  信息来源:{From[0].strip()}\t热度:{hottype[0].strip()}\n")
    f.write("——"*50+'\n')

# time.sleep(1)
driver.close()
driver.quit()


