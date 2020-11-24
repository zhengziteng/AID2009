"""
基于 epoll 的 IO并发模型
重点代码 ！！
"""

from socket import *
from select import *

# 创建全局变量
HOST = "0.0.0.0"
PORT = 8800
ADDR = (HOST, PORT)

# 创建套接字
sockfd = socket()
sockfd.bind(ADDR)
sockfd.listen(5)

# IO多路复用往往与非阻塞IO一起使用，防止传输过程的卡顿
sockfd.setblocking(False)

# 创建epoll对象
ep = epoll()
# 关注的IO
ep.register(sockfd, EPOLLIN)

# 建立文件描述符查找对象的字典
map = {sockfd.fileno(): sockfd}

# 循环监控关注的IO
while True:
    events = ep.poll() # events--> [(fileno,event),()]
    print("你有新的IO需要处理哦",events)
    # 对监控的套接字就绪情况分情况讨论
    for fd,event in events:
        if fd == sockfd.fileno():
            # 处理客户端连接
            connfd, addr = map[fd].accept()
            print("Connect from", addr)
            # 连接一个客户端就多监控一个
            connfd.setblocking(False)
            # 设置边缘触发：只通知一次，如果未处理则下次再通知
            ep.register(connfd, EPOLLIN|EPOLLET)
            map[connfd.fileno()] = connfd # 维护字典
        # elif event==EPOLLIN:
        #     # 某个客户端连接套接字就绪
        #     data = map[fd].recv(1024).decode()
        #     # 客户端退出
        #     if not data:
        #         ep.unregister(fd)  # 删除监控
        #         map[fd].close()
        #         del map[fd] # 维护字典删除一项
        #         continue
        #     print(data)
        #     # map[fd].send(b'OK')
        #     ep.unregister(fd)
        #     ep.register(fd, EPOLLOUT)  # 关注写
        # elif event == EPOLLOUT:
        #     # 写处理
        #     map[fd].send(b"OK")
        #     ep.unregister(fd) # 先清理之前的
        #     ep.register(fd, EPOLLIN)  # 重新关注读
