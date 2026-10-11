"""
https://blog.csdn.net/qq_45807032/article/details/105219674?ops_request_misc=elastic_search_misc&request_id=d69e51c5fb0ca04ecc57c01f7023b426&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-105219674-null-null.142^v102^control&utm_term=python%E8%BF%AD%E4%BB%A3%E5%99%A8&spm=1018.2226.3001.4187

可迭代对象：有__iter__()方法的对象
迭代器：有__iter__()和__next__()方法的对象，通过StopIteration异常来表示迭代结束

"""

import time
from collections.abc import Iterable,Iterator
 
class Classmate(object):
    """定义一个同学类"""
 
    def __init__(self):
        self.name = list()
        self.name_num = 0
 
    def add(self,name):
        self.name.append(name)
    
    def __iter__(self):
        return self   # 返回本身
 
    def __next__(self):
       if self.name_num < len(self.name):
           ret = self.name[self.name_num]
           self.name_num += 1
           return ret
 
        # 抛出异常，当循环后自动结束
       else:
           raise StopIteration
 
 
class1 =  Classmate()
class1.add("张三")
class1.add("李四")
class1.add("王五")
 
print("判断是否是可迭代的对象：", isinstance(class1,Iterable))
 
print("判断是否是迭代器：", isinstance(class1,Iterator))
 
for name in class1:
    print(name)
    time.sleep(1)
#这个迭代器只能用一次，仅供参考
for name in class1:
    print(name)
    time.sleep(1)
 
