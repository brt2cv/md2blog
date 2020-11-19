#!/usr/bin/env python3
# @Date    : 2020-11-19
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.3

import os
import yaml  # json
from pathlib import Path
from logging import getLogger

logger = getLogger(__file__)


class DocumentsMgr:
    default_conf = "database.yml"

    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        path_database = self.get_database()
        assert os.path.exists(path_database), f"请手动创建配置文件:【{path_database}】"
        self.load_data()
        # 每次运行程序前，备份之前的database文件
        self.backup_data()

    def get_database(self):
        return os.path.join(self.repo_dir, self.default_conf)

    @classmethod
    def template_data(cls, repo_dir):
        conf_data = {
            "dir_essay": "programming",
            # "dir_article": "articles",

            "structure": {
            # "programming": {
            #     "3-syntax": {
            #         "path_doc": {
            #             "title" : ""
            #             "weight": 0,
            #             "postid": 1234xxx,
            #             "tags"  : [],
            #             "date"  : "2020-05-25"
            #         },
            #         ...
            #     }
            # },
            # "artile": {}
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
        with open(path_data, "x", encoding="utf8") as fp:
            # json.dump(conf_data, fp, indent=2)  # ensure_ascii=False,
            yaml.dump(conf_data, fp, allow_unicode=True)

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
        if not path_conf:
            path_conf = self.get_database()

        with open(path_conf, "r", encoding="utf8") as fp:
            # self.data = json.load(fp)
            self.data = yaml.unsafe_load(fp)

    def save_data(self, path_save=None):
        if not path_save:
            path_save = self.get_database()

        with open(path_save, "w+", encoding="utf8") as fp:
            # json.dump(self.data, fp, ensure_ascii=False, indent=2)
            yaml.dump(self.data, fp, allow_unicode=True)

    def backup_data(self):
        """ 备份之前的database文件 """

    def rebuild_tags(self):
        """ 通过structure重新计算tags """

    def rebuild_titeles(self):
        """ 通过structure重新计算titles """

    def get_structure(self, path_unix):
        """ 返回dict_info，或者 None """
        assert not os.path.isabs(path_unix), "请使用相对路径查询[structrue]"
        tuple_parts = Path(path_unix).parts
        curr_level = self.data["structure"]
        for dirname in tuple_parts[:-1]:
            if dirname not in curr_level:
                return
            curr_level = curr_level[dirname]
        return curr_level.get(tuple_parts[-1])

    def _exists_structure(self, path_unix):
        return self.get_structure(path_unix) is not None

    def _set_structure(self, path_unix, dict_info):
        tuple_parts = Path(path_unix).parts
        curr_level = self.data["structure"]
        for dirname in tuple_parts[:-1]:
            if dirname not in curr_level:
                curr_level[dirname] = {}
            curr_level = curr_level[dirname]

        # assert tuple_parts[-1] not in curr_level, "文件已存在，勿重复添加"
        curr_level[tuple_parts[-1]] = dict_info

    def _del_structure(self, path_unix):
        tuple_parts = Path(path_unix).parts
        curr_level = self.data["structure"]

        list_levels = []
        for dirname in tuple_parts[:-1]:
            list_levels.append((curr_level, dirname))
            curr_level = curr_level[dirname]

        del curr_level[tuple_parts[-1]]
        list_levels.reverse()

        for dict_level, dirname in list_levels:
            if dict_level[dirname]:
                break
            else:
                del dict_level[dirname]

    def walk_repo(self, ignore_list=None):
        """ return: a set of path_file """
        if ignore_list is None:
            ignore_list = []

        set_files = set()
        for root, dirs, files in os.walk(self.repo_dir, topdown=False):
            path_rel = os.path.relpath(root, self.repo_dir)

            for name in files:
                if name[-3:] != ".md":
                    continue
                if name in ignore_list:
                    continue
                set_files.add(os.path.join(path_rel, name))
        return set_files

    def add_doc(self, md_parser, postid: str):
        path_rel = os.path.relpath(os.path.abspath(md_parser.file_path), self.repo_dir)
        assert not self._exists_structure(path_rel), "文件已存在，勿重复添加"
        doc_info = {
            "title" : md_parser.make_title(),
            "weight": md_parser.metadata["weight"],
            "postid": postid,
            "tags"  : md_parser.metadata["tags"],
            "date"  : md_parser.metadata["date"],
        }

        # update related
        assert doc_info["postid"] not in self.data["postids"], f"PostID重复: {doc_info['postid']}"
        # existed = self.data["titles"].get(doc_info["title"])
        # assert doc_info["title"] not in self.data["titles"], f"Title重复，冲突文件：{existed}"

        self.data["titles"][doc_info["title"]] = path_rel
        self.data["postids"][doc_info["postid"]] = path_rel

        for tag in doc_info["tags"]:
            if tag not in self.data["tags"]:
                self.data["tags"][tag] = []
            self.data["tags"][tag].append(path_rel)

        if doc_info["date"] not in self.data["dates"]:
            self.data["dates"][doc_info["date"]] = []
        self.data["dates"][doc_info["date"]].append(path_rel)

        self._set_structure(path_rel, doc_info)
        self.save_data()

    def remove_doc(self, path_rel):
        doc_info = self.get_structure(path_rel)
        del self.data["titles"][doc_info["title"]]
        for tag in doc_info["tags"]:
            tag_files = self.data["tags"].get(tag)
            if not tag_files:
                logger.warning(f"[-] 不存在【{tag}】标签，无法处理标签内容")
                continue
            if path_rel in tag_files:
                tag_files.remove(path_rel)
            if not tag_files:
                del self.data["tags"][tag]

        if path_rel in self.data["dates"][doc_info["date"]]:
            self.data["dates"][doc_info["date"]].remove(path_rel)
        if not self.data["dates"][doc_info["date"]]:
            del self.data["dates"][doc_info["date"]]
        del self.data["postids"][doc_info["postid"]]
        self._del_structure(path_rel)
        self.save_data()

    def modify_doc(self, md_parser):
        path_rel = os.path.relpath(os.path.abspath(md_parser.file_path), self.repo_dir)
        old_info = self.get_structure(path_rel)
        new_info = {
            "title" : md_parser.make_title(),
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
                tag_files = self.data["tags"].get(tag)
                if not tag_files:
                    logger.warning(f"[-] 不存在【{tag}】标签，无法处理标签内容")
                    continue
                if path_rel in tag_files:
                    tag_files.remove(path_rel)
                if not tag_files:
                    del self.data["tags"][tag]
            for tag in set(new_info["tags"]) - set(old_info["tags"]):
                if tag not in self.data["tags"]:
                    self.data["tags"][tag] = []
                self.data["tags"][tag].append(path_rel)

        if path_rel in self.data["dates"][old_info["date"]]:
            self.data["dates"][old_info["date"]].remove(path_rel)
        if not self.data["dates"][old_info["date"]]:
            del self.data["dates"][old_info["date"]]
        if new_info["date"] not in self.data["dates"]:
            self.data["dates"][new_info["date"]] = []
        self.data["dates"][new_info["date"]].append(path_rel)

        self._set_structure(path_rel, new_info)
        self.save_data()

    def move_doc(self, path_old, path_new):
        # path_old: 转换为相对路径
        path_old = os.path.relpath(os.path.abspath(path_old), self.repo_dir)
        path_new = os.path.relpath(os.path.abspath(path_new), self.repo_dir)
        doc_info = self.get_structure(path_old)
        self.data["titles"][doc_info["title"]] = path_new

        for tag in doc_info["tags"]:
            self.data["tags"][tag].remove(path_old)
            self.data["tags"][tag].append(path_new)

        self.data["dates"][doc_info["date"]].remove(path_old)
        self.data["dates"][doc_info["date"]].append(path_new)

        self.data["postids"][doc_info["postid"]] = path_new
        self._del_structure(path_old)
        self._set_structure(path_new, doc_info)
        self.save_data()

    def get_title_by_path(self, path):
        dict_info = self.get_structure(path)
        if dict_info:
            return dict_info["title"]

    def get_title_by_postid(self, postid):
        path_rel = self.data["postids"].get(postid)
        return self.get_title_by_path(path_rel)

    def get_postid_by_path(self, path):
        """ return str(postid) or None if not exist """
        dict_info = self.get_structure(path)
        if dict_info:
            return dict_info["postid"]

    def get_postid_by_title(self, doc_title):
        """ Not Recommand! """
        path_rel = self.data["titles"].get(doc_title)
        return self.get_postid_by_path(path_rel)

    # def exist_doc(self, doc_title):
    #     return self.get_postid_by_title(doc_title)

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

    # def rebuild_format(self):
    #     for path, md_info in self.data["structure"].items():
    #         # list_parts = list(Path(path).parts)
    #         path_unix = path.replace("\\", "/")

    #         list_parts = path_unix.split("/")
    #         file_name = list_parts.pop()
    #         if file_name == "_index.md":
    #             continue
    #         curr_level = structure_rebuild
    #         for part in list_parts:
    #             if part not in curr_level:
    #                 curr_level[part] = {}
    #             curr_level = curr_level[part]
    #         curr_level[file_name] = md_info

    #     self.data["structure"] = structure_rebuild
    #     self.save_data("db_rebuild.json")

    def check_repo_dbmap(self):
        """ 根据repo中的数据库检测数据内容书否对应 """
        from util.gitsh import GitRepo

        # 获取self.data中的全部路径
        set_db_files = set()
        def join_path_part(dict_data, path_prefix):
            for fname, next_level in dict_data.items():
                # path_join = path_prefix + "/" + fname
                new_prefix = path_prefix.copy()
                new_prefix.append(fname)
                if fname.endswith(".md"):
                    path_join = "/".join(new_prefix)
                    set_db_files.add(path_join)
                else:
                    join_path_part(next_level, new_prefix)

        join_path_part(self.data["structure"], [])

        # from pprint import pprint
        # pprint(set_db_files)

        # 通过git获取当前管理的全部文件
        git = GitRepo(self.repo_dir)
        list_files = set(git.files("\.md"))

        # from pprint import pprint
        # pprint(list_files)

        for path_md in list_files:
            if os.path.basename(path_md) == "_index.md":
                continue
            # list_parts = list(Path(path_md).parts)
            path_unix = path_md.replace("\\", "/")
            try:
                set_db_files.remove(path_unix)
            except KeyError:
                print(f"[-] 当前db中缺失文件信息【{path_unix}】")

        for path_unix in set_db_files:
            print(f"[+] 当前db中多余的文件信息【{path_unix}】")


if __name__ == "__main__":
    def getopt():
        import argparse

        parser = argparse.ArgumentParser("db_mgr", description="""
* 用于生成db初始化文件: `py db_mgr.py -i ./note/`
* 用于数据库自检：查询db中，相较于磁盘，缺失或多余的文件（不联网）: `py db_mgr.py -c`
* 用于根据 `git state -s` 中的rename项迁移文件路径（注意，请勿修改文件内容）: `py db_mgr.py -m`
""")
        parser.add_argument("-i", "--init", action="store", help="指定Git项目的所在目录，并创建数据库")
        # parser.add_argument("-c", "--selfcheck", action="store_true", help="数据库自检")
        # parser.add_argument("-b", "--rebuild", action="store_true", help="重构.cnblog.json的structure结构")
        # parser.add_argument("-r", "--repair", action="store", help="修复数据库内容")
        parser.add_argument("-d", "--remove", action="store", help="删除数据库条目【】")
        return parser.parse_args()

    args = getopt()
    if args.init:
        DocumentsMgr.template_data(os.path.realpath(args.init))
        exit()
    else:
        db_mgr = DocumentsMgr("note/")

    if args.remove:
        db_mgr.remove_doc(args.remove)
    # else:
    # 默认读取.cnblog.json获取note目录

    # path_cnblog_conf = ".cnblog.json"
    # with open(path_cnblog_conf, "r") as fp:
    #     dict_conf = json.load(fp)

    # repo_dir = dict_conf["repo_dir"]
    # mgr = DocumentsMgr(repo_dir)

    # if args.selfcheck:
    #     assert False, "请使用 'python3 main.py -c' 来比对数据库"
    #     mgr.check_repo_dbmap()
    # elif args.rebuild:
    #     assert False, "请更改代码，定义rebuild的操作后，注释当前行再执行命令"
    #     mgr.rebuild_format()
