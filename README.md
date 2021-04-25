# message_plus_server
本项目为 [message_plus](https://github.com/KangSpace/message_plus) 小程序项目的后台服务,简单Python WebServer.

# 启动步骤
1. 安装flask依赖
> pip3 install flask requests
> 或 
> chmod +x msg_plus/bin/init.sh
> sh msg_plus/bin/init.sh

2. 启动
nohup3 python simple_server.py > msgplus.log 1>&2
> 或 
> chmod +x msg_plus/bin/startup.sh
> sh msg_plus/bin/startup.sh
> tail msgplus.log 打印以下日志即表示启动成功  
> &#42; Debugger is active!  
> &#42; Debugger PIN: 152-958-509