# lanbda 参数列表；函数体
# 逻辑简单,只有一行
# 通常作为高阶函数的参数
out_line =lambda : print("_______________________________")
out_line()
add =lambda a,b:a+b
print(add(1,2))

data_list=["c","python","java","c++","javascript","php"]
data_list.sort(key=lambda x:len(x))#根据字符串的长度排序
print(data_list)