from tkinter import *

def fun1():
    canvas=Canvas(width=300,height=300,bg="white")#创建一个画布，设置宽度为300像素，高度为300像素，背景颜色为白色
    canvas.pack(expand=True,fill=BOTH)
    x1=163
    y1=163
    y2=172
    for i in range(19):
        canvas.create_line(x1,y1,x1,y2,width=1,fill='red')#在画布上创建一条线段，起点坐标为(x1, y1)，终点坐标为(x1, y2)，线宽为1像素，颜色为红色
        x1-=5
        y1-=5
        y2+=5

    x1=163
    y1=163
    y2=172
    for i in range(19):
        canvas.create_line(x1,y1,x1,y2,width=1,fill='red')
        x1+=5
        y1+=5
        y2+=5
        

# fun1()


def fun2():
    canvas=Canvas(width=500,height=500,bg="white")
    canvas.pack(expand=True,fill=BOTH)
    x1=100
    y1=100
    x2=200
    y2=200
    for i in range(20):
        canvas.create_rectangle(x1,y1,x2,y2)#左上角到右下角的矩形
        x1+=5
        y1+=5
        x2-=5
        y2-=5

# fun2()

import random
def fun3():
    randomnum=random.randint(1,100)#生成一个1到100之间的随机整数
    cho=random.choice([1,2,3,4,5])#从列表[1, 2, 3, 4, 5]中随机选择一个元素
    random.shuffle([1,2,3,4,5])#将列表[1, 2, 3, 4, 5]中的元素随机打乱顺序

import string
"""
生成一个长度为n的随机字符串，字符串由大小写字母和数字组成。
"""
def fun4(n:int):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


# print(fun4(10))

def fun5(start:int, end:int,num:int):
    return random.sample(range(start, end + 1), num)  # 从[start, end]范围内随机选择num个不重复的整数

print(fun5(1, 100, 10))















# mainloop()
