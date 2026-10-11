from selenium import webdriver
import time
from package import SAVEPATH

driver = webdriver.Edge()
driver.get('https://www.bilibili.com/')
time.sleep(1)

driver.maximize_window()#最大化窗口
time.sleep(1)

with open(SAVEPATH.save_path_inDownload('bilibili.html'),'w',encoding='utf-8') as f:
    f.write(driver.page_source)#获取网页源代码并写入文件

print(driver.title)#获取网页标题

print(driver.current_url)#获取当前页面的URL

driver.save_screenshot(SAVEPATH.save_path_inDownload('bilibili.png'))#截图并保存

driver.refresh()#刷新页面
time.sleep(1)

driver.quit()#关闭浏览器
