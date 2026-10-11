# Web Crawler

## robots协议  不用管，但不要采集用户的隐私数据
robots协议是一个网站用来告诉搜索引擎哪些页面可以被爬取，哪些页面不可以被爬取的协议。
它通过在网站根目录下放置一个名为`robots.txt`的文件来实现。
这个文件包含了一些规则，告诉搜索引擎哪些页面可以被爬取，哪些页面不可以被爬取。

# HTTP和HTTPS协议
https是HTTP的安全版本，它使用SSL/TLS协议来加密数据传输，保护用户的隐私和安全。

http://www.example.com/index.html
http与https 是协议
www.example.com 是域名
/index.html 是路径
## http请求信息 报文
HTTP报文是由请求行、请求头、空行和请求体组成的。
### 请求行：
包含了请求方法、请求URL和HTTP版本。
### 请求头：
包含了请求的元信息，如User-Agent、Accept等。
### 空行：
用于分隔请求头和请求体。
### 请求体：
包含了要发送给服务器的数据。
## http响应信息
HTTP响应报文是由状态行、响应头、空行和响应体组成的。
### 状态码：
200 OK：请求成功
302 Found：请求的资源被临时移动到另一个URL
404 Not Found：请求的资源不存在
500 Internal Server Error：服务器内部错误
503 Service Unavailable：服务器暂时无法处理请求，一般是反爬虫
### Cookie：
cookie是服务器发送给客户端的一小段数据，客户端会在后续的请求中携带这个数据，以便服务器识别用户身份和状态。
## requests
### 请求传递参数
1. URL参数：通过在URL中添加查询字符串来传递参数，例如`http://www.example.com/search?q=python`。
2. 表单参数：通过paramms参数传递，例如`requests.get('http://www.example.com/search', params={'q': 'python'})`。
3. JSON参数：通过json参数传递，例如`requests.post('http://www.example.com/api', json={'key': 'value'})`。

## XPath
XPath是一种用于在XML文档中定位节点的语言，也可以用于HTML文档中。它使用路径表达式来选择节点，可以根据节点的名称、属性、位置等进行选择。
常用的XPath表达式：
- `/tag`：选择根元素下的tag子元素
- `//tag`：选择所有tag子元素
- `@attribute`：选择具有指定属性的元素
- `text()`：选择元素的文本内容

## 模拟登录
### cookies + session 鉴权机制
 判断方法: 可以看请求参数，session一般为form data 格式，也可以看域名，，session鉴权域名相同


cookies是服务器发送给客户端的一小段数据，客户端会在后续的请求中携带这个数据，以便服务器识别用户身份和状态。
session是一种服务器端的存储机制，用于保存用户的状态和数据。它通常与cookies结合使用，服务器会在session中保存用户的状态和数据，并通过cookies将session ID发送给客户端，客户端在后续的请求中携带这个session ID，以便服务器识别用户身份和状态。 
### 基于Token的鉴权机制
 判断方法：可以看请求参数，也可以看域名，Token鉴权域名不同
基于Token的鉴权机制是一种常见的用户认证和授权方式。它通过生成一个唯一的Token来标识用户身份，并在后续的请求中携带这个Token，以便服务器识别用户身份和状态。常见的Token类型有JWT（JSON Web Token）和OAuth Token。
## jsonpath
jsonpath是一种用于在JSON数据中定位节点的语言。它使用路径表达式来选择节点，可以根据节点的名称、属性、位置等进行选择。
常用的jsonpath表达式：
- `$.key`：选择根元素下的key子元素
- `$..key`：选择所有key子元素
- `$.key[0]`：选择key数组中的第一个元素
- `$`  :选择根元素

## selenium
selenium是一个用于自动化测试和爬取动态网页的工具。它可以模拟用户在浏览器中的操作，如点击、输入等，并获取网页的内容。
来应对反爬取
安装 pip install selenium
使用selenium需要下载对应浏览器的驱动程序，例如Chrome浏览器需要下载ChromeDriver，Firefox浏览器需要下载GeckoDriver等。

## selenium+xpath
使用selenium结合xpath可以更方便地定位和操作网页元素。通过selenium的
`find_element_by_xpath`方法可以使用xpath表达式来定位元素，并进行相应的操作，如点击、输入等。
river.find_element(by='xpath', value='//span[normalize-space(text())="手机登录"]').click()#点击页面上的元素，例如登录按钮等

driver.find_element(by='xpath', value='//input[@placeholder="请输入手机号码/邮箱"]').send_keys('173')#通过xpath定位输入框并输入内容

driver.find_element(by='xpath', value='//input[@placeholder="请输入密码"]').send_keys('wana666')#通过xpath定位输入框并输入内容

driver.find_element(by='xpath', value='//button[@class="!text-18px ant-btn ant-btn-primary ant-btn-block"]').click()#点击页面上的元素，例如登录按钮等
## 等待
#time.sleep(1)
强制等待

#driver.implicitly_wait(19)
隐式等待，加载页面时会等待，直到页面加载完成或者达到指定的时间（19秒）为止

#显式等待，可以等待某个条件，较高级
"""
from selenium.webdriver.suppoert import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

WebDriverWait(driver, 10,0.2).until(
    EC.visibility_of_element_located((by='xpath', value='//span[normalize-space(text())="手机登录"]'))
    #等待页面上某个元素可见，例如登录按钮等
    EC.element_to_be_clickable((by='xpath', value='//span[normalize-space(text())="手机登录"]')
    #等待页面上某个元素可点击，例如登录按钮等
) # 创建一个WebDriverWait对象，等待时间为10秒,每0.2秒检查一次条件是否满足

"""
## iframe切换操作 （典型的有qq邮箱）