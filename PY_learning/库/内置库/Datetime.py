import time

v1=time.time()#这是1970年1月1日到现在的秒数，返回一个浮点数
print(v1)
t=time.localtime(v1)#将秒数转换为时间元组，包含年、月、日、时、分、秒等信息
print(t)
time.sleep(2)#让程序暂停2秒钟


from datetime import datetime
now = datetime.now()#获取当前日期和时间
print("当前日期和时间:", now)

# zonetime =datetime.utcnow()#获取当前UTC日期和时间
# print("当前UTC日期和时间:", zonetime)   