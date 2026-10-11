#函数是什么，函数也是对象
import time
def timer(operation):
    def decorator(f):
        def wrapper(*arg,**args):
            start_time=time.time()
            for i in range(operation):
                result=f(*arg,**args)
            end_time=time.time()
            print(f.__name__,'运行时间：',end_time-start_time)
            return result
        return wrapper
    return decorator




@timer(100000)#z这里对应的就是最外侧的timer以及它的参数
def add(a,b):
    return a+b

# @decorator()
# def fun1(a,b):
#      return a*b

@timer(10)
def qinatao(a,b):
    add(a,b)

qinatao(1,3)