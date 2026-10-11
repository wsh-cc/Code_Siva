# list的方法
"""
s=[1,2,3,4,5,6,7,8,'string']
append 是追加的意思
s.append('abc')//在列表末尾添加一个元素
s.insert(1,2)//在指定位置添加一个元素，原来位置的元素向后移动
s.remove('string')//删除列表中第一个出现的指定元素，如果没有这个元素会报错
s.pop()//删除列表最后一个元素
s.pop(0)//删除指定位置的元素
s.sort()//对列表进行排序
s.reverse()//对列表进行反转
"""
# sum()//求和
#len()//求长度
def delchongfu(ar1,ar2):
    res=ar1+ar2
    #res=[*ar1,*ar2]解包组包操作
    res.sort()
    res1=[]
    for i in res:
        if i not in res1:
            res1.append(i)
    return res1  
        
#arr1=[12,23,34,45,56,6757,78,89,23,54,67,78,89,90]
# arr2=[1,1,2,2,23,45,243,56,234,45,67,78,89,90]
# print(delchongfu(arr1,arr2))

"""
list1=[]
list2=[]
for i in range(1,21):
    list1.append(i**2)
    if i**2%2==0:
       list2.append(i**4)     
print(*list1)
print(*list2)

"""
# ____________________________________________________________________
# STIRNG 类型也有切片，与list同理
# 正向索引和反向索引也一样
# str1="hello world" 
""""字符串不可变！！！真的"""
#string 方法
"""
find()//在字符串中查找指定字符或字符串，返回第一次出现的位置索引，如果没有找到返回-1
count()//统计字符串中指定字符出现的次数
upper()//大小写转换
lower()//大小写转换
strip()//去除字符串两端的空格
strip('a')//去除字符串两端的'a'
replace('a','b')//将字符串中的'a'替换成'b
startwith('a')//判断字符串是否以'a'开头
———————— 注意：因为字符串是不可变的，所以字符串的方法都是返回一个新的字符串，而不是修改原来的字符串—————— 
"""
# a=input()
# b=a[::-1]
# if a==b:
#     print('是回文字符串')
#     print(a[::-1])
# else:
#     print('不是回文字符串')
# ____________________________________________________________________

"""元组 tuple"""
"""
count()//统计元组中指定元素出现的次数
index()//在元组中查找指定元素，返回第一次出现的位置索引，如果
*扩展解包(可以动态解包，例如收集剩余所有的元素)//收集后为列表
a=10
b=20
a,b=b,a
为什么交换成功
因为1.  t=b,a 相当于组包
    2.  a,b=t 相当于解包

tuple1=1,2,3,4,5
s
"""
#————————————————————————————————————————————————————————————————————
# set集合
"""
无序，不可重复，可修改，不支持索引和切片


st={1,2,3,4,5,6,7,8,9,10,1,2,3,4,5,6,7,8,9,10}
print(st)
# 定义一个空集合
# st1=set()初始化
# 而不是st1={}
# 集合的方法
st.add(11)//添加元素
st.remove(1)//删除元素，如果没有这个元素会报错
st.pop()//随机删除一个元素并返回被删除的元素
st.clear()//清空集合

st.difference(st1)//返回集合st与st1的差集,即返回st中有而st1中没有的元素
也可以用-运算符
也可以用集合推导式st2={i for i in st if i not in st1}

st.union(st1)//返回集合st与st1的并集,即返回st和st1中所有的元素
也可以用|运算符

st.intersection(st1)//返回集合st与st1的交集,即返回st
也可以用&运算符

集合推导式的写法
# a={i for i in listset }
# a={i for i in listset if 条件}
"""


#字典dict
# dictionary
dict1={1:'a',2:'b',3:'c',4:'d',5:'e'}
# print(dict1)
# 键值对类型(key,value)value可以变化，key不行，value可以是任意类型
# key不可以重复，如果重复了会覆盖之前的值
# dict1={}#空字典
# 方法
""""
字典名称[key]=value//添加一个键值对
字典名称.pop(key)//弹出指定键值对
del 字典名称[key]//删除指定键值对
字典名称[key]=value//修改指定键对应的值

根据key获取value
dict1[key]
dict.get(key)

 ems()//返回字典中所有的键值对，返回一个可迭代对象，每个元素都是一个元组，元组中包含一个键值对
"""

print(dict1.keys())
for i in dict1.items():
    print(i)
