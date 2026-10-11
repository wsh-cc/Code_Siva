def fun1():
    for i in range(100,1000):
        a=i//100
        b=i//10%10
        c=i%10
        if a**3+b**3+c**3==i:
            print(i)

# fun1()

def fun2():
    num=1
    for i in range(9):
        num=2*(num+1)
    print(num)
# fun2()

def fun3():
    str = input()
    cnta=0
    cnt =0
    cnt1=0
    Cnt=0
    for i in range(len(str)):
        if 'a'<=str[i]<='z' or 'A'<=str[i]<='Z':# isalpha()
            cnta+=1
        elif '0'<=str[i]<='9':# isdigit()
            cnt+=1
        elif str[i]==' ':#  isspace()
            cnt1+=1
        else:
            Cnt+=1
    print(f"字母个数: {cnta}, 数字个数: {cnt}, 空格个数: {cnt1}, 其他字符个数: {Cnt}")

# fun3()

def fun4():
    #同一类型
    l=[1,2,3,4,5,2,3,4,5,52,5,2,3,4,5,2,3,4,5]
    l.sort(reverse=True)
    #sort(iterable, key=None, reverse=False)
    #iterable：要排序的可迭代对象。
    #key：一个函数，用来从每个元素中提取一个用于排序比较
    #reverse：一个布尔值。如果为True，列表元素将被按降序排序。默认为False，即升序排序。
    print(l)

# fun4()

def fun5():
    tuple1 = [
    {"sname": "张三","sno": 101,"sgrade":89},
    {"sname": "李四","sno": 108,"sgrade":90},
    {"sname": "王五","sno": 102,"sgrade":86},
    {"sname": "赵六","sno": 103,"sgrade":76},
    {"sname": "钱七","sno": 105,"sgrade":99},
    ]
    tuple1.sort(key=lambda x: x['sgrade'], reverse=True)#使用匿名函数
    print(tuple1)
fun5()