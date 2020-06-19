#!/bin/bash

shopt -s expand_aliases  # 使支持alias
source ~/.profile
source ~/.bash_aliases

log_mkdocs="./env/mkdocs.log"
log_pull="./env/gitpull.log"

if [ -d ./env ]; then
    enpy ./env
else
    # python3 -m venv --without-pip --system-site-packages env
    pyvenv env
    enpy ./env
    # pip3 install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
    pypi -r requirements.txt
fi

auto_pull=`cat service_conf.yml | shyaml get-value auto_pull`
if [ ${auto_pull}_ = "True_" ]; then
    killall auto_pull.sh > /dev/null 2>&1  # 屏蔽win10警告
    nohup bash gitool/auto_pull.sh >> $log_pull 2>&1 &
fi

nohup mkdocs serve > $log_mkdocs 2>&1 &

# 启动ngrok.cc网络穿透
run_ngrok=`cat service_conf.yml | shyaml get-value ngrok.run`
if [ ${run_ngrok}_ = "True_" ]; then
    serial_id=`cat service_conf.yml | shyaml get-value ngrok.serial_id`
    nohup py ./ngrok.py --client=${serial_id} >> $log_mkdocs 2>&1 &
    echo "已启动ngrok.cc网络穿透，访问地址： http://mkdocs.free.idcfengye.com"
fi
