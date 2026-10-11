def fun11(list):
    sum = 0 
    for i in list:
        if i%2==0:
            sum+=i
    return sum

def fun12(dict):
    name =''
    age =0
    for key in dict:
        if dict[key]>age:
            name=key
            age=dict[key]
    print(f"年龄最大的人是{name}，年龄是{age}")

def fun13(List,num):
    for i in range(len(List)):
        if num<=List[i]:
            List.insert(i,num)
            return 
    List.append(num)
    return 

def fun14(a:float,b:float,c:float):
    f = sorted([a,b,c])
    for i in f:
        print(i)

# fun14(3.3,3.0,10)

def fun15(num : int):
    n =9
    while n%num!=0: 
        n=n*10+9 
    print(n)
i=int(input())
fun15(i) 
    


    
    