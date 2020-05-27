#!/usr/bin/env python3
# @Date    : 2020-05-25
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2

from collections import defaultdict
from git import Repo


def git_status(repo_or_dir, type_) -> list:
    """ type_:
        ("untracked", "modified", "added", "deleted", "renamed")
    """
    repo_obj = Repo(repo_or_dir) if isinstance(repo_or_dir, str) else repo_or_dir
    dict_status = defaultdict(list)

    str_status = repo_obj.git.execute(["git", "status", "-s"])
    for line in str_status.splitlines():
        status, path_file = line.split()
        path_file = path_file.strip('"')  # 去除对路径的双引号
        dict_status[status].append(path_file)

    map_type2files = {
        "untracked" : "??",
        "modified"  : "M",
        "added"     : "A",
        "deleted"   : "D",
        "renamed"   : "R",
    }
    return dict_status[map_type2files[type_]]


if __name__ == "__main__":
    if not repo.is_dirty():
        print("无文件要提交，干净的工作区")
        exit()

    list_untracked = repo.untracked_files  # 新建项
    list_modified = get_status("modified")  # 修改项
