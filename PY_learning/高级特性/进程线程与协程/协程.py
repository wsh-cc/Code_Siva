
"""
# 协程（Coroutine）是一种轻量级的线程，允许在单线程内实现并发执行。
# 协程通过 `async` 和 `await` 关键字来定义和使用，可以在等待某些操作完成时暂停执行，
# 并在操作完成后继续执行。
# 是和I/O密集型，切换成本低
#就像你可以边写作业边听音乐，等咖啡
"""

from gevent import monkey
monkey.patch_all()#打补丁兼容系统函数
#放在导入其他模块之前

import time

#协程需要第三方库greenlet
from greenlet import greenlet
"""
greenlet需要手动切换携程，使用 `switch()` 方法来切换到另一个协程。
"""
import gevent


def sing():
   while True:
    print("正在唱歌...")
    yield
    time.sleep(1)

def dance():
    while True:
        print("正在跳舞...")
        yield
        time.sleep(1)


def eatfood():
    print("eating food...")
    time.sleep(1)

    print("eating all food")

def drinking():
    print("drinking water...")
    time.sleep(1)

    print("drinking all water")

def func(name):
    for _ in range(1,10):
        print(f"task:{name} de di {_} ci yun xing")
        time.sleep(3)
        # gevent.sleep(1)
        #正常来说应该很慢，会一个一个按顺序执行
        #所以需要在文件顶部加上一个东西就会将time.sleep()识别成gevent.sleep()

def test1():
    """
    协程可以使用 `yield` 关键字来暂停和恢复执行。
    每次调用 `next()` 时，协程会从上次暂停的地方继续执行，直到遇到下一个 `yield` 或者函数结束。
    """
    s = sing()
    d = dance()
    for _ in range(5):
        next(s)
        next(d)
        print('-'*20)


def test2():
    """
    greenlet是一个第三方库，可以更方便地实现协程。它提供了一个 `greenlet` 类，
    允许你创建和切换协程。
    """
    g1 = greenlet(eatfood)
    g2 = greenlet(drinking)
    g1.switch()#切换到g1协程，执行eatfood函数
    g2.switch()

def test3():
    gevent.joinall(
       [ gevent.spawn(func,'A'),
        gevent.spawn(func,'B'),
        gevent.spawn(func,'C'),]
    )
    # gevent.join(func,('c',))
    print("all is over!!")
#spawn()创建
#join()等待单个
#joinall([])等待所有线程完成
if __name__ == "__main__":
 
#   test1()
#   test2() 
#   test3()
