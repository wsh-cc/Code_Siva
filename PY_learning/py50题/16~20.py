from email.errors import InvalidBase64PaddingDefect
from tkinter import N


def fun1():
   for i in range(7):
    while True:
         num=int(input("请输入一个整数1~50："))
         if 1<=num<=50:
             print(f"*"*num)
             break
    
def fun2():
    num=int(input("请输入一个整数："))
    if num%2==0:
        print(f"{num}是偶数")
    else:
        print(f"{num}是奇数")

def fun3():
    #判断年份是否为闰年
    year=int(input("请输入一个年份："))
    if (year%4==0 and year%100!=0) or year%400==0:
        print(f"{year}是闰年")  
    else:
        print(f"{year}不是闰年")


def fun4(num):
    str1=''
    n1=num
    while n1>0:
        str1=str(n1%2)+str1
        n1=n1//2
    print(f"{num}的二进制表示是{str1}")#bin(num)[2:]#bin(num)[2:]去掉前缀0b
    n2 =num
    str2=''
    while n2>0:
        str2=str(n2%8)+str2
        n2=n2//8
    print(f"{num}的八进制表示是{str2}")#oct(num)[2:]# oct(num)[2:]去掉前缀0o
    str3=''
    n3=num
    while n3>0:
        str3=str(n3%16)+str3
        n3=n3//16
    print(f"{num}的十六进制表示是{str3}")#hex(num)[2:]# hex(num)[2:]去掉前缀0x

# fun4(100)

def fun5():
    while True:
        num=int(input())
        if num**2<50:
            break
    

fun5()
