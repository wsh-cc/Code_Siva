import time
import random
from selenium import webdriver

driver = webdriver.Edge()
driver.get('https://www.cqupt.edu.cn/')

driver.implicitly_wait(10) 
time.sleep(1)
for i in range(10):
    time.sleep(0.1)
    js = 'window.scrollBy(0, {})'.format(random.randint(100, 300))
    
    driver.execute_script(js)

driver.close()
driver.quit()