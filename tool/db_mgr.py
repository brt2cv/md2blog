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
        self.path_db = os.path.join(repo_dir, self.default_conf)

        # if os.path.exists(path_db):
        self.load_data()

    @classmethod
    def template_data(cls, repo_dir):
        conf_data = {
            "repo_dir" : repo_dir,
            "dir_随笔": repo_dir + "essay",
            "dir_文章": repo_dir + "artiles",

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
        with open(path_data, "w", encoding="utf8") as fp:
            json.dump(conf_data, fp)

    def __del__(self):
        self.save_data()

    def load_data(self, path_conf):
        if path_conf:
            self.path_data = path_conf

        with open(self.path_data, "r") as fp:
            self.data = json.load(fp)

    def save_data(self, path_save=None):
        if path_save:
            self.path_data = path_save

        with open(self.path_data, "w") as fp:
            json.dump(self.data, path_save)

    def rebuild_tags(self):
        """ 通过structure重新计算tags """

    def rebuild_titeles(self):
        """ 通过structure重新计算titles """

    def add_doc(self, md_parser, postid):
        path_rel = os.path.relpath(os.path.abspath(path_doc), self.data["repo_dir"])
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
        for tag in doc_info["tags"]:
            self.data["tags"][tag].append(path_rel)
        self.data["postids"][doc_info["postid"]] = path_rel
        self.data["dates"][doc_info["date"]].append(path_rel)

        self.data["structure"][path_rel] = doc_info

    def remove_doc(self, path_rel):
        doc_info = self.data["structure"][path_rel]
        del self.data["titles"][doc_info["title"]]
        for tag in doc_info["tags"]:
            self.data["tags"][tag].remove(path_rel)
        self.data["dates"][doc_info["date"]].remove(path_rel)
        del self.data["postids"][doc_info["postid"]]
        del self.data["structure"][path_rel]

    def modify_doc(self, md_parser):
        path_rel = os.path.relpath(os.path.abspath(path_doc), self.data["repo_dir"])
        old_info = self.data["structure"][path_rel]

        new_info = {
            "title" : md_parser.metadata["title"],
            "weight": md_parser.metadata["weight"],
            "postid": postid,
            "tags"  : md_parser.metadata["tags"],
            "date"  : md_parser.metadata["date"],
        }

        if old_info["title"] != new_info["title"]:
            del self.data["titles"][old_info["title"]]
            self.data["titles"][new_info["title"]] = path_rel

        if set(old_info["tags"]) != set(new_info["tags"]):
            for tag in set(old_info["tags"]) - set(new_info["tags"]):
                self.data["tags"].remove(path_rel)
            for tag in set(new_info["tags"]) - set(old_info["tags"]):
                self.data["tags"][tag].append(path_rel)

        self.data["dates"][old_info["date"]].remove(path_rel)
        self.data["dates"][new_info["date"]].append(path_rel)

        self.data["structure"][path_rel] = new_info

    def move_doc(self, path_src, path_dst):
        raise Exception("尚未开发，敬请期待")

    def get_postid(self, doc_title):
        """ return str(postid) or None if not exist """
        path_rel = self.data["titles"].get(doc_title)
        if path_rel:
            return self.data["structure"][path_rel].get(postid)

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

if __name__ == "__main__":
    def getopt():
        import argparse

        parser = argparse.ArgumentParser("db_mgr", description="仅用于生成db初始化文件")
        parser.add_argument("repo_dir", action="store", help="文档Git项目的所在目录")
        return parser.parse_args()

    args = getopt()
    DocumentsMgr.template_data(os.path.realpath(args.repo_dir))
