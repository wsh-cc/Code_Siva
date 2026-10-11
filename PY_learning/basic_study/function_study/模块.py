# 有五种模块导入方法
# 1. 导入整个模块
# import math

# 2. 导入模块并重命名
# import math as mt

# 3. 导入模块中的所有函数
# from math import *
"""
 __all__=["sin","cos","tan"]

 #假如这是math模块中，那么当math模块被导入时，只有sin,cos,tan这三个函数会被导入
"""
# 4. 导入模块中的指定函数
# from math import sin

# 5. 导入模块中的指定函数并重命名
# from math import cos as cs

"""
包  Package

包的本质就是一个文件夹,该文件夹中可以包含若干个py模块,文件夹下还包含了一个__init__.py文件,
作用:模块较多时,用来管理多个模块

"""
from 函数测试 import my_hello
# 函数测试.my_hello()
my_hello()

