import time
import threading
import requests 


count =0

#子线程
def worker1():
    time_start = time.time()
    res = requests.get('https://www.baidu.com')
    time_end = time.time()
    print(f"请求状态码: {res.status_code}, 耗时: {time_end - time_start:.2f}秒")

def worker2(val1,val2,val3):
    time_start = time.time()
    res = requests.get('https://www.baidu.com')
    time_end = time.time()
    print(f"val1: {val1}, val2: {val2}, val3: {val3}")
    print(f"请求状态码: {res.status_code}, 耗时: {time_end - time_start:.2f}秒")

def test1():
    # 创建子线程 ：target = 子线程函数
    #1
    #threading.Thread(target=worker1).start()
    #不写这种写法了
    """
    线程是共享内存空间的，所以主线程和子线程之间是可以共享数据的，
    线程时无序的，不会等子线程结束了才继续往下走，
    线程的调用是异步的，主线程不会等子线程结束就继续往下走了，
    所以如果主线程结束了，整个程序就结束了，子线程也就结束了，
    所以我们需要让主线程等待子线程结束后才继续往下走
    """
    #2 写这种方便start 和 join 的调用
    t1 =threading.Thread(target=worker2,kwargs={"val1":1,"val2":2,"val3":3})
    # t1 =threading.Thread(target=worker2,args=(1,2,3))
    """
    args 和 kwargs 的区别：
    args 是一个元组，传递位置参数，调用时会按照顺序将,一个元素时需要加逗号区分元组和普通括号
    kwargs 是一个字典，传递关键字参数
    """
    t1.start()
    #等待t1线程结束后，主线程才继续往下走,
    t1.join()

lock=threading.Lock() #创建一个锁对象，尽量不用锁，锁会降低性能，只有在必要的时候才使用锁
def test2():
    """
    可能会出现资源竞争，最终count的值可能不是600000
    解决方式是加lock锁
    """
    def add():
        lock.acquire() #加锁
        #lock.aquire(timeout=1) 可以设置超时时间，避免死锁，
        global count
        for _ in range(100000):
            count += 1
        lock.release() #释放锁

    t1=threading.Thread(target=add)
    t2=threading.Thread(target=add)

    t1.start()
    t2.start()

    t1.join()
    t2.join()   

    print(f"最终count的值: {count}")

#所有程序默认有一个主线程，主线程结束了，整个程序就结束了，自己创建的是子线程
# if __name__ =="__main__":
    
#     print("主线程开始")
    
#     # test1()
#     # test2() #怎么计数没有冲突,可能是是计算得太快了？

#     """
#     资源竞争？但是py不是有GIL吗？
#     可能会出现这种情况：t1读取到值的时候被中断了，然后切换t2线程，并完成了加一但是没有写回内存，t1继续执行，完成了加一并写回内存，这样就丢失了一次加一(重复了)
#     """
#     print("主线程结束")
test2()

