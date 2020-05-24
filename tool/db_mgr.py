#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.0.1

import json
from git import Repo


REPO_ROOT_DIR = ".."
DB_FILE = REPO_ROOT_DIR + "/files.json"

repo = Repo(REPO_ROOT_DIR)
if not repo.is_dirty():
    print("无文件要提交，干净的工作区")
    exit()


def git_status(type_):
    """ type_:
        ("untracked", "modified", "added", "deleted", "renamed")
    """
    from collections import defaultdict

    dict_status = defaultdict(list)

    str_status = repo.git.execute(["git", "status", "-s"])
    for line in str_status.splitlines():
        status, path_file = line.split()
        dict_status[status].append(path_file)

    map_type2files = {
        "untracked" : "??",
        "modified"  : "M",
        "added"     : "A",
        "deleted"   : "D",
        "renamed"   : "R",
    }
    return dict_status[map_type2files[type_]]

class DocumentsMgr:
    def __init__(self):
        self.dict_conf = {
                "docs_dir": REPO_ROOT_DIR + "/documents/",
                "db_file":  REPO_ROOT_DIR + "/doc.json",
            }
        self.metadata = {
            # path_tree: {
            #     path_doc: {
            #         "weight": 0,
            #         "postid": 1234xxx,
            #         "tags"  : []
            #     }
            # }
        }

    def load_config(self, path_conf):
        with open(path_conf, "r") as fp:
            dict_conf = json.load(fp)

        for key, value in dict_conf.items():
            self.dict_conf[key] = value

    def save_config(self, path_save):
        with open(path_conf, "w") as fp:
            json.dump(self.dict_conf, path_save)

    def add_doc(self, path_doc):
        pass

    def get_postid(self, doc_title):
        """ return str(postid) or None if not exist """
        return None

    def exist_doc(self, doc_title):
        return self.get_postid(doc_title)

    def modify_doc(self, path_doc):
        pass

    def move_doc(self, path_doc):
        pass

    def list_tags(self):
        pass

    def get_docs_of_tag(self, tag_name):
        pass

    def get_docs_of_category(self, category_name):
        pass

    def sync_database(self):
        """ 从cnblog下拉最新的元数据，并更新本地数据库：
            由于可能从cnblog上增加了label等数据，导致本地数据过时。
        """
        pass


if __name__ == "__main__":
    list_untracked = repo.untracked_files  # 新建项
    list_modified = get_status("modified")  # 修改项

    mgr = DocumentsMgr()
    # mgr.load_config()
