#!/bin/bash

usage="Usage: ./auto_pull.sh >> pull.log"
test ${1}_ == "-h_" && echo $usage && exit

function action() {
    if [ -z "`git pull | grep 'Already'`" ]; then
        # 更新label
        echo "重新生成labels链接"
        python3 ./labels.py
    fi
    cur_date=$(date '+%Y-%m-%d, %H:%m')
    echo "完成更新 (Current Time: $cur_date)"
}

function action-test() {
    # echo "Hello"
    zenity --info --text 'ahts'
}


# crontab -e  # 编辑定时指令

while true; do
    action
    # delta=`expr 60 \* 60 \* 24`
    sleep 1d
done
