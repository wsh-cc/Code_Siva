# 函数的作用域//全局变量和局部变量
# 全局变量先声明，再使用
#在局部函数里面修改全局变量，需要使用global关键字，
# for i in range(10):
    # print(i)
#     for j in range(5):
#         print(j)
#         a=1
# print(i,a)
# - 如果循环在全局作用域（不在任何函数内），循环里的赋值操作会直接定义全局变量。​
# - 如果循环在函数内部，循环里的赋值操作会定义局部变量（除非用 global 或 nonlocal 声明）。
"""
默认参数要放在最后，可以设置多个，//否则会报错
"""
# def func(a,b,c=10):
#    return a+b+c

# 不定长参数
# 类型：位置，
# def fun1(*a,**b):#*a表示位置参数,封装成元组，**b表示关键字参数，封装成字典
#     print(a)
#     print(type(a))
#     print(b)
#     print(type(b))
#     if b.get("round") is not None:#注意这里是字符串
#         print(round(sum(a)/len(a),b.get("round")))

# a=2
# fun1(1,2,3,4,a,round=2)
    

# 普通参数类型；字符布尔字符串列表元组集合字典
# 特殊参数；函数参数
"""
接下来将要演示
"""
def add(*numberss):
    return sum(numberss)

def fun2(a,b,fun):
    return fun(a,b)

# print(add(1,2,3,4,5))
print(fun2(1,2,add))