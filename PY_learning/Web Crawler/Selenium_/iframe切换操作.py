from selenium import webdriver
import time
from package import SAVEPATH

driver = webdriver.Edge()
driver.get('https://mail.qq.com/')
# driver.implicitly_wait(10) #隐式等待，加载页面时会等待，直到页面加载完成或者达到指定的时间（10秒）为止

driver.switch_to.frame(1)
driver.switch_to.frame('ptlogin_iframe')#切换到iframe，参数可以是id、name、index等qq邮箱的id和name都是ptlogin_iframe，index是1

#点击密码登录
driver.find_element(by='xpath', value='//*[@id="switcher_plogin"]').click()
time.sleep(1)





driver.quit()