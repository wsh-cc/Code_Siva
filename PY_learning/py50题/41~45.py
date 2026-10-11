def fun1(str1:str,n:int):

    str1=''.join([str1[0:n][::-1], str1[n:len(str1)-n], str1[len(str1)-n:len(str1)][::-1]])
    print(str1)

# fun1("abcdefg",2)
   
def fun2(dict1:dict)->dict:
    res={}
    for key in dict1:
        res[dict1[key]]=key
    return res

# a={"a":1,"b":2,"c":3}
# res=fun2(a)
# print(res)

def fun3()->str:
    try:
        res = int(input("请输入一个整数："))

    except ValueError:
        return "输入错误"
    return res

# res=fun3()
# print(res)

def fun4(age:int):
    if age<0 or age>135:
        raise ValueError("年龄必须在0到135之间")
       #raise + 异常类型 (错误信息)


from ast import main
from tkinter import *
def fun5():
    canvas=Canvas(width=1000,height=900)
    canvas.pack(expand=True,fill=BOTH)
    k=1
    j=1
    for i in range(90):
        canvas.create_oval(250-k,200-k,250+k,200+k,width=1)#左上角到右下角的椭圆
        k+=j
        j+=1
        

fun5()
mainloop()