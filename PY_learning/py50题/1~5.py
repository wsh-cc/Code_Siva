def add(a,b):
    return a+b

def bijiao():
    a,b=map(int,input().split(' '))
    if a>b:
        print(f"{a}大于{b}")
    elif a<b:
        print(f"{a}小于{b}")
    else:
        print(f"{a}等于{b}")

# bijiao()
def func3():
    count = 0
    for i in range(1, 101):
        count += i
    print(count)

def func4():
    cnt=0
    for i in range(1,5):
        for j in range(1,5):
            for k in range(1,5):
                if i!=j and j!=k and i!=k:
                    print(i,j,k)
                    cnt+=1
    print(cnt)
# func4()
def func5():
    for i in range(1,10):
        for j in range(1,i+1):
            print(f"{j}*{i}={i*j}\t",end=' ')
        print()

# func5()