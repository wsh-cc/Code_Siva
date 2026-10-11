import hashlib
str1=input("请输入需要加密的密码：")
hash_object=hashlib.md5(str1.encode('utf-8'))
result =hash_object.hexdigest()
print("加密密码为：",result)