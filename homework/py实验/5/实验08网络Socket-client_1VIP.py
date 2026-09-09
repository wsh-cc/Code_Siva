#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：client.py

import socket               # 导入 socket 模块
import os
os.system('cls')  # 清屏
s = socket.socket()         # 创建 socket 对象
host = socket.gethostname() # 获取本地主机名
port = 12341                # 设置端口好

s.connect((host, port))
print('连接服务器成功。立即开始接受消息。')

print(s.recv(1024).decode(encoding='utf_8', errors='strict'))
##input( '客户端：收到第1条消息，回车键继续')

print(s.recv(1024).decode(encoding='utf_8', errors='strict'))
##input( '客户端：收到第2条消息，回车键继续')

print(s.recv(1024).decode(encoding='utf_8'))
##input( '客户端：收到第3条消息，回车键继续')



meg = input( '请输入要发送的消息：')
input( '回车键继续：立即发送消息。。。')
s.send(meg.encode(encoding='utf_8', errors='strict'))
print( '我是客户端：消息已发送，关闭连接。')
s.close()  

