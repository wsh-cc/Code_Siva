#打开一个进程就像打开一个微信，互不影响，
#如微信崩溃，浏览器却不会崩溃，而线程却不一样
"""
进程的五种状态
新建态：正在创建进程
就绪态：进程已经准备好，可以运行了，但还没有被分配到CPU上运行(如切到了后台)
运行态：进程正在CPU上运行
阻塞态：进程正在等待某个事件发生，如等待输入/输出完成，等待锁释放等，此时进程无法继续执行
终止态：进程已经完成了它的任务，或者被强制终止了，此时进程已经结束了它的生命周期
"""
import re
import os,sys


import time
import multiprocessing

sys.path.append(r'D:\Python_code\高级特性')
from  Generator生成器 import Fib

def sing(name,age):
    print(f"{age}岁的{name}正在唱歌...")
    time.sleep(2)
    # os.getpid() #获取当前进程的id
    # os.getppid() #获取当前进程的父进程的id
    print(f"当前进程的id: {os.getpid()}, 父进程的id: {os.getppid()}")
    print(f"{name}唱歌结束了")
def dance(name,age):
    print(f"{age}岁的{name}正在跳舞...")
    time.sleep(3)
    # print(f"当前函数的名称：{dance.__name__}")输出函数的名称

    # print(f"当前进程的名称：{multiprocessing.current_process().name}")
    #  #输出当前进程的名称
    print(f"当前进程的id: {os.getpid()}, 父进程的id: {os.getppid()}")
    print(f"{name}跳舞结束了")
def test1():
     #和线程一样，参数用args 或 kwargs 传递,可以指定进程的名称，默认是Process-1, Process-2..
    p1 = multiprocessing.Process(target = sing,kwargs={"name":"凉","age":19})
    p2 = multiprocessing.Process(target = dance,name="跳舞进程",args=('波奇',18))
    print(f"p1的名称：{p1.name}, p2的名称：{p2.name}")
    #同时进行，  进程的创建成本更高
    p1.start()
    p2.start()
    
    # is_alive()判断进程是否还在运行，返回True或False
    print(f"p1是否还在运行: {p1.is_alive()}, p2是否还在运行: {p2.is_alive()}")
    p1.join()
    print(f"p1是否还在运行: {p1.is_alive()}, p2是否还在运行: {p2.is_alive()}")

    p2.join()
    print(f"p1是否还在运行: {p1.is_alive()}, p2是否还在运行: {p2.is_alive()}")


def add():
        global count
        for _ in range(100000):
            count += 1
        print(f"父进程的id: {os.getpid()}, count的值: {count}")
def test2():
    
    p1= multiprocessing.Process(target=add)
    # 进程是独立的内存空间，都是一个独立副本
    p2= multiprocessing.Process(target=add)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"最终count的值: {count}")


def test3():
    """
    进程间不共享资源，进程间通信需要使用队列、管道等方式，线程间共享资源，线程间通信可以直接使用全局变量等方式
    这里使用Multiprocessing模块里的Queue
    """
    q = multiprocessing.Queue(3)
     #默认参数为零，表示为无限制
    print(q.empty()) #判断队列是否为空
    q.put('hello')
    print(q.qsize())#判断数量
    q.put(999)
    q.put(True)
    # q.put('world') #当队列满了，再放入元素会阻塞，直到有空间为止
    print(q.qsize())
    for _ in range(q.qsize()):
        print(q.get(),end = ' ') 

def producer(q):
    for i in range(5):
        q.put(i)
        print(f"生产了{i},目前仓库有{q.qsize()}件商品")
        time.sleep(0.5)
def consumer(q):
    while q.empty()!= True:
        print(f"消费了{q.get()},目前仓库有{q.qsize()}件商品")
        time.sleep(1)
def test4():
    q = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=producer,args=(q,))
    p2 = multiprocessing.Process(target=consumer,kwargs={'q': q})
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()


def my_fib(n):
    res = Fib(n)
    print(f"第{n}个斐波那契数是：{res}")
    time.sleep(1)
    return res     
def test5():
    # print(multiprocessing.cpu_count())#获取CPU的核心数   我是32核
    p = multiprocessing.Pool(3)#创建一个进程池，最多同时运行3个进程，最好为cpu核数
    results = []

    for i in range(1,9):
        result=p.apply_async(my_fib,args=(i,))#apply_async()方法是异步的，表示不会阻塞主进程，主进程会继续往下走，而子进程会在后台运行，直到完成任务后才会返回结果
        """
        apply_async()   异步表示无序，主程序会继续运行走   
        apply()         同步表示有先后顺序，要先完成一个任务才能继续下一个
        """
        results.append(result)

    p.close()#关闭进程池，表示不再接受新的任务, 
    """
    一定要先调用close()方法,才能调用join()方法，否则会报错，表示进程池还在接受新的任务，无法等待所有任务完成
    """
    p.join()#等待所有进程池中的任务完成
    
    for res in results:
        # print(res)#获取结果，没有join与get 方法，会直接输出结果是一个AsyncResult对象，表示一个异步结果
        #而不会等待，因此会先结束，导致剩余子进程终止
        
        print(res.get())#获取结果，get()会阻塞，需要对应子进程结束才会返回


count = 0
if __name__ == "__main__":
  a=1  
#   test1()
#   test2()
#   test3()
#   test4()
#   test5()
