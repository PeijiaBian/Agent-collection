#!/bin/bash

# 设置日志文件路径
LOG_FILE="app.log"

# 启动应用并将输出重定向到日志文件
nohup python webapp.py > ${LOG_FILE} 2>&1 &

# 输出进程ID
echo $! > webapp.pid
echo "应用已在后台启动，进程ID: $(cat webapp.pid)"
echo "日志文件: ${LOG_FILE}" 