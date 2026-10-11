def fun1(n:int):
    if n%2==0:
        return 
    else :
        for i in range((n-1)//2):
            print(f"{' '*((n-1)//2-i)}{'*'*(i*2+1)}")
        print(f"{'*'*n}")
        for j in range((n-1)//2):
            print(f"{' '*(j+1)}{'*'*(n-2-2*j)}")
# fun1(7)

def fun2(List:list)->list:
    if len(List)<=1:
        return List
    return [List[-1],*List[1:len(List)-1],List[0]]

# a=[1,2,3,4,5]
# res=fun2(a)
# print(res)

def fun3(List:list,index1:int,index2:int)->list:
    List[index1],List[index2]=List[index2],List[index1]
    return List

# a=[1,2,3,4,5]
# res=fun3(a,1,3)
# print(res)

def fun4(List:list,target:int)->int:
    cnt=List.count(target)
    return cnt 

def fun5(List:list)->int:
    res=1
    for i in List:
        res*=i
    return res