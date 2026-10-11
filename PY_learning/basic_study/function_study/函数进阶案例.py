def jie(n):
    if(n==1 or n==0):
        return 1
    return n*jie(n-1)

def countmoney(*commodity:tuple,coupon=0,score=0,express=0):#可以默认为零
    goods_price=sum([good[1]*good[2] for good in commodity])
    if(goods_price>=5000):
        if(coupon<=goods_price):
            goods_price-=coupon

        if(score//100>=goods_price):
            goods_price=0
            score-=goods_price*100
        else:
            goods_price -= score//100
            score %= 100

    return goods_price+express
   
count_money=countmoney(("apple",100,20),("orange",150,30),coupon=100,score=2000,express=100.9)
print(count_money)
# 200+450+100
# 2000+4500-100-200+100=
"""
类型注解的写法:
a:int=10
b:str="hello"
c:float=10.5
d:bool=True
e:list=[1,2,3,4,5]
ss:list[str]=["a","b","c"]
dictary:dict[str,int]={"a":1,"b":2,"c":3}
goods:tuple[str,int,int]=("apple",100,20)

但是py有类型推断功能，所以不需要写类型注解，但是建议写类型注解，因为类型注解可以提高代码的可读性，

"""
# names:list[str,int,int]=['str',1,2]
# ppp=None
# names.append("hello")
# print(names)
# names.append(0.33)
# print(names)

def add(a:int,b:int)->int:
    return a+b
#定义了参数类型和返回值类型
print(add(1,2))

