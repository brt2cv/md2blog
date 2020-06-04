#!/usr/bin/env python3
# @Date    : 2020-05-27
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2

import os
import subprocess


def run_cmd(str_cmd):
    """ return a list stdout-lines """
    completed_process = subprocess.run(str_cmd,
                                shell=True,
                                check=True,
                                stdout=subprocess.PIPE)
    return completed_process.stdout.decode().splitlines()

def git_status(repo_dir):
    cwd = os.path.abspath(os.path.curdir)
    os.chdir(repo_dir)
    list_lines = run_cmd("git status -s")
    os.chdir(cwd)
    return list_lines

class GitMixedStatus(Exception):
    """ Git status 状态不纯净（例如AM，即add了新文件，
        又进行了修改，但修改未添加到stage） """

def filter_status(stdout_lines, type_):
    """ git-status是用两位状态表示的 """
    list_files = []
    for line in stdout_lines:
        _state, path_file = line.split(maxsplit=1)
        state_mixed = line[:2]

        path_file = path_file.strip('"')  # 去除对路径的双引号
        checking = {
            "untracked"         : state_mixed == "??",
            "added"             : state_mixed[0] != " ",
            "unadded"           : state_mixed[1] != " ",  # AM, MM, AD
            "new_added"         : state_mixed[0] == "A",  # A_
            "new_unadded"       : state_mixed[1] == "A",  # A_
            "modified_added"    : state_mixed[0] == "M",
            "modified_unadded"  : state_mixed[1] == "M",  # MM, AM, _M
            "deleted_added"     : state_mixed[0] == "D",
            "deleted_unadded"   : state_mixed[1] == "D",
            # "renamed"   : "R" == state,
        }[type_]
        if checking:
            list_files.append(path_file)

    return list_files

def git_commit(repo_dir, message):
    if not message:
        from datetime import datetime
        message = datetime.now().strftime('%a, %b %d %H:%M')
    cwd = os.path.abspath(os.path.curdir)
    os.chdir(repo_dir)
    run_cmd(f'git commit -m "{message}"')
    os.chdir(cwd)

def git_add(list_path):
    cwd = os.path.abspath(os.path.curdir)

    repo_file = list_path[0]
    repo_sub_dir = repo_file if os.path.isdir(repo_file) else os.path.dirname(repo_file)
    os.chdir(repo_sub_dir)
    run_cmd('git add "' + '" "'.join(list_path) + '"')
    os.chdir(cwd)

class GitRepo:
    def __init__(self, repo_dir):
        self.repo_dir = repo_dir

    def status(self, type_=None):
        list_lines = git_status(self.repo_dir)
        if type_:
            list_files = filter_status(list_lines, type_)
            return list_files
        else:
            return list_lines

    def add(self, list_path):
        # return git_add(list_path)
        cwd = os.path.abspath(os.path.curdir)
        os.chdir(self.repo_dir)
        run_cmd('git add "' + '" "'.join(list_path) + '"')
        os.chdir(cwd)

    def commit(self, message):
        return git_commit(self.repo_dir, message)

    def is_status_mixed(self):
        list_lines = self.status()
        for line in list_lines:
            # _state = line.split(maxsplit=1)[0]
            _state = line[:2].strip()
            if _state != "??" and len(_state) != 1:
                return True

# if __name__ == "__main__":
#     list_modified = git_status("../note", "modified")
#     print(list_modified)
#     print(os.path.abspath(os.curdir))
