"""
https://blog.csdn.net/weixin_65289420/article/details/146369209?ops_request_misc=elastic_search_misc&request_id=5ef6fdc5532026fcfa0f790d286a0d7c&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-2-146369209-null-null.142^v102^control&utm_term=python%E7%94%9F%E6%88%90%E5%99%A8&spm=1018.2226.3001.4187


s
"""
def echo_generator():
    value = yield "准备接收"#第一次调用next(gen)时，生成器会执行到yield "准备接收"这一行，并暂停在这里，等待外部发送值。
    print(f"收到: {value}")#当外部通过gen.send("你好")发送值时，生成器会从暂停的地方继续执行，将"你好"赋值给value，并打印收到的值。
    while True:
        value = yield f"你发送了: {value}"
        print(f"收到: {value}")
# gen = echo_generator()
# print(next(gen))      # 初始化生成器，输出: 准备接收
# print(gen.send("你好"))  # 发送值并获取下一个值，输出: 你发送了: 你好
# print(gen.send("不好"))  # 发送值并获取下一个值，输出: 你发送了: 你好


def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 获取斐波那契数列的前10个数



"""我写一个装饰器"""

def num(number):#这是装饰器的参数
    def decorator(f):#接受原函数
        def function(*args,**kwargs):#接受原函数的参数
            fun=f(*args,**kwargs)
            for _ in range(0,number):
                result=next(fun) 

            return result
        return function
    return decorator


def Fib(number):
    @num(number)#加一个这个装饰器
    def fib():#这是原函数，且是一个生成器，调用时需要先定义一个生成器对象
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a+b
    return fib()#返回生成器对象  

# print(Fib(5))


if __name__ == "__main__":
    fib_gen = fibonacci()
    fibs = [next(fib_gen) for _ in range(20)]#表示next(fib_gen)调用20次，获取前20个斐波那契数
    print(fibs)  # 输出: 