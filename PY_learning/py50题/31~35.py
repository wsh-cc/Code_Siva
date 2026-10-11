


from re import I


def fun1(Dict:dict)->int:
    # return sum(Dict.values())
    res=0
    for i in Dict.values():
        res+=i
    return res
def fun(n:int)->float:
    if n<=0:
        return None
    else:
        res=0
        for i in range(1,n+1):
            res+=1/i
        return res
    
def fun3(Y:int,M:int,D:int)->int:
    mon=[31,28,31,30,31,30,31,31,30,31,30,31]
    if (Y%4==0 and Y%100!=0) or Y%400==0:
        mon[1]+=1
    return sum(mon[:M-1])+D

# day=fun3(2024,1,1)
# print(day)

def fun4(n:int)->int:
    if n<=0:
        return None
    else:
        a,b=0,1
        for i in range(1,n):
            a,b=b,a+b
        return a 
# for I  in range(10):
#  print(fun4(I))

def fun5(n:int):
    if n<=0:
        return
    elif n==1:
        print(1)
        return
    else:
        # def is_prime(num):
        #     if num<=1:
        #         return False
        #     for i in range(2,int(pow(num,0.5))+1):
        #         if num%i==0:
        #             return False
        #     return True
        i=2
        while i*i<=n:
            if  n%i==0:
                n//=i
                if n==1: 
                    print(i)
                else:
                    print(i,end='*')
            else:
                i+=1
        if n>1:
            print(n)

# fun5(64)
                
