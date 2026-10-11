def fun1(List:list):
    res=0
    return sum(List)

def fun2(r:int,l:int)->list:
    
    return [i for i in range(l,r+1) if i%2==0]

def fun3(List1:list,List2:list)->list:
    return [i for i in List1 if i not in List2]


# a=[1,2,3,4,5]
# b=[4,5,6,7,8]
# res = fun3(a,b)
# print(res)

def fun4(List:list)->list:
    List.sort()
    i = 1
    for j in range(1,len(List)):
        if List[i-1]!=List[j]:
            List[i]=List[j]
            i+=1
    return List[:i]

# a=[1,1,2]
# res = fun4(a)
# print(res)

def fun5(x,y):
    return y,x

