#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：server.py

import socket               # 导入 socket 模块

s = socket.socket()         # 创建 socket 对象
host = socket.gethostname() # 获取本地主机名
print( '服务器主机名是：'+ host + '。')

port = 12341                # 设置端口
s.bind((host, port))        # 绑定端口

s.listen(5)                 # 等待客户端连接
while True:

    print('服务器被阻塞，等待客户连接。。。')
    c, addr = s.accept()     # 建立客户端连接。
    
    input('\n\n\n连接成功。客户端地址为:' + str( addr ) + '\n回车键继续：发送消息。')

    meg = '\n1.连接成功\n'
    c.send(meg.encode(encoding='utf_8', errors='strict'))
    input( '\n已发送第1条消息：回车键继续')

    meg = '\n2.欢迎您的到来\n'
    c.send(meg.encode(encoding='utf_8', errors='strict'))
    input( '\n已发送第2条消息：回车键继续')

    meg = '\n3.我是服务器.\n'
    c.send(meg.encode(encoding='utf_8', errors='strict'))
    print( '\n已发送第3条消息。\n\n立即接收消息。。。')

    print( '\n接收到的消息是：' + c.recv(1024).decode(encoding='utf_8', errors='strict'))
    
    c.close()                # 关闭连接
    print( '\n\n等待下一个客户端...')

print( '程序已结束')
