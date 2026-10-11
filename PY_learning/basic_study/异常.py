#异常处理两种方案
"""
1.不做处理
2.捕获异常

异常类型有
ValueError
NameError
IndexError
KeyError
AttributeError
ImportError
ModuleNotFoundError
SyntaxError
TabError
IndentationError
MemoryError

"""
# ValueError
"""

try:
 可能出现异常的代码1
 可能出现异常的代码2
 可能出现异常的代码3
 可能出现异常的代码4

except 异常类型 as 变量名:
 出现异常时的预案
[finally:
    不管是否出现异常，都会运行的代码]

"""
# try:
#     print('-'*20)
#     print(name)
# except Exception:
#     print("联系管理员")

# # 可以用Exception捕获所有异常
# finally:
#          print("都会执行")


#异常的传递
# 异常的传递就是异常在函数中层层上报，直到被捕获为止，或者程序报错


def fun1():
    print("fun1")
    fun2()
def fun2():
    print("fun2")
    fun3()

def fun3():
    print("fun3")
    fun4()  
def fun4():
    print("fun4")
    print(masdkfm)

try:
    fun1()
except Exception:
     print("联系管理员")
