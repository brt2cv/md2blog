#!/usr/bin/env python3
# @Date    : 2020-05-25
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.0.1

import os
import json

from doc_parser import MarkdownParser


class DocumentsMgr:
    default_conf = ".database.json"

    def __init__(self, repo_dir):
        self.path_data = os.path.join(repo_dir, self.default_conf)
        assert os.path.exists(self.path_data), f"请手动创建配置文件:【{self.path_data}】"
        self.load_data()
        # 每次运行程序前，备份之前的database文件
        self.backup_data()

    @classmethod
    def template_data(cls, repo_dir):
        conf_data = {
            "dir_repo" : repo_dir,
            "dir_essay": os.path.join(repo_dir, "programming"),
            "dir_article": os.path.join(repo_dir, "articles"),

            "structure": {
            #     "path_doc": {
            #         "title" : ""
            #         "weight": 0,
            #         "postid": 1234xxx,
            #         "tags"  : [],
            #         "date"  : "2020-05-25"
            #     },
            #     ...
            },
            # 以下为冗余数据，空间换时间
            "titles": {
            #     "artile": "path_doc",
            #     ...
            },
            "tags": {
            #     "tag_1": ["path_doc"],
            #     ...
            },
            "dates": {
            #     "date": ["path_doc", ...],
            #     ...
            },
            "postids": {
            #     post_id: "path_doc",
            #     ...
            }
        }
        path_data = os.path.join(repo_dir, cls.default_conf)
        with open(path_data, "x") as fp:
            json.dump(conf_data, fp)

    # def __del__(self):
    #     self.save_interface()

    def save_interface(self):
        if not hasattr(self, "data"):
            return

        status = input("""是否保存配置文件：
1. 不保存
2. 保存
3. 另存为
4. 查看当前数据库内容
>> """)
        if status == "1":
            return
        elif status == "2":
            self.save_data()
        elif status == "3":
            def input_path():
                path_save = input("输入存储路径，按[back]返回: ")
                if path_save == "back":
                    return "back"
                dir_ = os.path.dirname(path_save)
                if not os.path.exists(dir_):
                    # 无法判断是否是正常路径字符串
                    print("路径不存在，请手动创建...")
                    return
                return path_save

            while True:
                path_save = input_path()
                if path_save:
                    break
            if path_save == "back":
                self.save_interface()
            else:
                self.save_data(path_save)

        elif status == "4":
            self.save_interface()
        else:
            print("未知的输入选项，请重新输入[1-4]: ")
            self.save_interface()

    def load_data(self, path_conf=None):
        if path_conf:
            self.path_data = path_conf

        with open(self.path_data, "r", encoding="utf8") as fp:
            self.data = json.load(fp)

    def save_data(self, path_save=None):
        if path_save:
            self.path_data = path_save

        with open(self.path_data, "w+", encoding="utf8") as fp:
            json.dump(self.data, fp)

    def backup_data(self):
        """ 备份之前的database文件 """

    def rebuild_tags(self):
        """ 通过structure重新计算tags """

    def rebuild_titeles(self):
        """ 通过structure重新计算titles """

    def add_doc(self, md_parser, postid):
        path_rel = os.path.relpath(os.path.abspath(md_parser.file_path),
                                   self.data["dir_repo"])
        assert path_rel not in self.data["structure"], "文件已存在，勿重复添加"
        doc_info = {
            "title" : md_parser.metadata["title"],
            "weight": md_parser.metadata["weight"],
            "postid": postid,
            "tags"  : md_parser.metadata["tags"],
            "date"  : md_parser.metadata["date"],
        }

        # update related
        existed = self.data["titles"].get(doc_info["title"])
        assert doc_info["title"] not in self.data["titles"], f"Title重复，冲突文件：{existed}"
        assert doc_info["postid"] not in self.data["postids"], f"PostID重复: {doc_info['postid']}"

        self.data["titles"][doc_info["title"]] = path_rel
        self.data["postids"][doc_info["postid"]] = path_rel

        for tag in doc_info["tags"]:
            if tag not in self.data["tags"]:
                self.data["tags"][tag] = []
            self.data["tags"][tag].append(path_rel)

        if doc_info["date"] not in self.data["dates"]:
            self.data["dates"][doc_info["date"]] = []
        self.data["dates"][doc_info["date"]].append(path_rel)

        self.data["structure"][path_rel] = doc_info
        self.save_data()

    def remove_doc(self, path_rel):
        doc_info = self.data["structure"][path_rel]
        del self.data["titles"][doc_info["title"]]
        for tag in doc_info["tags"]:
            self.data["tags"][tag].remove(path_rel)
        self.data["dates"][doc_info["date"]].remove(path_rel)
        del self.data["postids"][doc_info["postid"]]
        del self.data["structure"][path_rel]
        self.save_data()

    def modify_doc(self, md_parser):
        path_rel = os.path.relpath(os.path.abspath(md_parser.file_path),
                                   self.data["dir_repo"])
        old_info = self.data["structure"][path_rel]

        new_info = {
            "title" : md_parser.metadata["title"],
            "weight": md_parser.metadata["weight"],
            "postid": old_info["postid"],
            "tags"  : md_parser.metadata["tags"],
            "date"  : md_parser.metadata["date"],
        }

        if old_info["title"] != new_info["title"]:
            del self.data["titles"][old_info["title"]]
            self.data["titles"][new_info["title"]] = path_rel

        if set(old_info["tags"]) != set(new_info["tags"]):
            for tag in set(old_info["tags"]) - set(new_info["tags"]):
                self.data["tags"][tag].remove(path_rel)
                if not self.data["tags"][tag]:
                    del self.data["tags"][tag]
            for tag in set(new_info["tags"]) - set(old_info["tags"]):
                if tag not in self.data["tags"]:
                    self.data["tags"][tag] = []
                self.data["tags"][tag].append(path_rel)

        self.data["dates"][old_info["date"]].remove(path_rel)
        if new_info["date"] not in self.data["dates"]:
            self.data["dates"][new_info["date"]] = []
        self.data["dates"][new_info["date"]].append(path_rel)

        self.data["structure"][path_rel] = new_info
        self.save_data()

    def move_doc(self, path_src, path_dst):
        raise Exception("尚未开发，敬请期待")
        self.save_data()

    def get_postid(self, doc_title):
        """ return str(postid) or None if not exist """
        path_rel = self.data["titles"].get(doc_title)
        if path_rel:
            return self.data["structure"][path_rel]["postid"]

    def exist_doc(self, doc_title):
        return self.get_postid(doc_title)

    def sort_dir(self, path_dir, method="weight"):
        """ 排序目录下文件 """

    def list_tags(self):
        return self.data["tags"]

    def get_docs_of_tag(self, tag_name):
        return self.data["tags"][tag_name]

    def get_docs_of_category(self, category_name):
        pass

    def sync_database(self):
        """ 从cnblog下拉最新的元数据，并更新本地数据库：
            由于可能从cnblog上增加了label等数据，导致本地数据过时。
        """
        pass

# if __name__ == "__main__":
#     def getopt():
#         import argparse

#         parser = argparse.ArgumentParser("db_mgr", description="仅用于生成db初始化文件")
#         parser.add_argument("repo_dir", action="store", help="文档Git项目的所在目录")
#         return parser.parse_args()

#     args = getopt()
#     DocumentsMgr.template_data(os.path.realpath(args.repo_dir))
