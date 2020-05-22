#!/bin/bash

test -z $1 && action="pull" || action=$1  # echo "Error: 请显式定义操作!" && exit

function clone_or_pull () {
dir_name=$1
url_repo=$2
branch=$3
others=${*:4}

    if [ -d $dir_name ]; then
        cd $dir_name
        echo "尝试更新 ${dir_name} 模块"
        # git checkout $branch
        git pull
        cd - > /dev/null
    else
        echo "克隆仓库 ${url_repo} --> ${dir_name}"
        git clone $url_repo $dir_name $others
        cd $dir_name
        if [ $? -eq 0 ]; then
            git checkout $branch
            test $? -eq 0 && echo "已切换至${branch}分支" || echo "无法切换分支${branch}"
            cd - > /dev/null
        fi
    fi
}

function sub_module_pull () {
dir_module=$1
url_repo=$2
branch=$3

    if [ -d $dir_module ]; then
        git subtree pull --prefix=$dir_module $url_repo $branch --squash
    else
        read -p "是否载入子模块 [y/N]" continue
        if [ ${continue}_ == "y_" ]; then
            git subtree add --prefix=$dir_module $url_repo $branch --squash
        fi
    fi
}

function sub_module_push () {
dir_module=$1
url_repo=$2
branch=$3

    git subtree push --prefix=$dir_module $url_repo $branch
}

#####################################################################

m_cnblog="git@gitee.com:brt2/pycnblog.git"

if [ $action == "push" ]; then
    echo "如需推送，请直接到子仓库中执行 `git push`"
    exit
elif [ $action == "pull" ]; then
    # 子模块
    # sub_module_pull include/pystr $m_pystr dev

    # 子项目
    # test -d tool || mkdir -p tool
    clone_or_pull tool/cnblog $m_cnblog dev
else
    echo "未知的指令参数: ${action}"
    exit
fi
