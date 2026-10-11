def fun1(n,num):
    res=n
    tmp=n
    for i in range(1,num):
        tmp=tmp*10+n
        res+=tmp
    print(res)
# fun1(2,3)
def fun2(n):
    if n<=1:
        return 1
    for i in range(1,n+1):
        n=n*i
    return n

import math
from operator import is_
def fun3(r:float)->float:
    return round(math.pi*pow(r,2),2)

def fun4(l:int,r:int):
    def is_prime(n):
        if n<=1:
            return False
        for i in range(2,int(pow(n,0.5))+1):
            if n%i==0:
                return False
        return True
    for _ in range(l,r+1):
        if is_prime(_):
            print(_)


# fun4(50,100)
def fun5(n):
   res=0
   for i in range(1,n+1):
       res+=i**2
   return res