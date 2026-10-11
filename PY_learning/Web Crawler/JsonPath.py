"""
安装pip install jsonpath

JsonPath是一个用于在JSON数据中提取特定信息的工具。它提供了一种类似于XPath的语法，可以方便地从复杂的JSON结构中获取所需的数据。
"""

import json
from jsonpath import jsonpath


"""
使用jsonpath 提取json数据
json_data = jsonpath(json_data, '$.author')[0]# $ 表示根节点，.表示子节点，[]表示数组索引
json_data = jsonpath(json_data, '$..author')# $ 表示根节点，..表示任意层级的子节点


"""