from selenium.webdriver import ActionChains
from selenium import webdriver
#click:鼠标左击
#double_click:鼠标双击
#context_click:右键点击
#move_to_element:鼠标移动
#click_and_hold:鼠标点击并保持按下鼠标
#move_by_offset:鼠标移动指定的距离
#drag_and_drop:拖动元素到目标位置

driver = webdriver.Edge()
driver.get('https://www.runoob.com/try/try')

driver.implicitly_wait(10)


ac = ActionChains(driver)#创建一个ActionChains对象，传入driver参数

ac.move_to_element(driver.find_element(by='xpath', value='//*[@href="/http/http-status-codes.html"]'))#鼠标移动到元素上

ac.click_and_hold()#鼠标点击并保持按下鼠标

ac.move_to_element(driver.find_element(by='xpath', value='//*[@id="s"]'))#鼠标移动到元素上

ac.release()#释放鼠标

# driver.find_element(by='xpath', value='').click()#执行enter
"""最重要的一步，执行动作链中的所有动作，如果不执行，前面的动作都不会生效"""
ac.perform()#执行动作链中的所有动作
