#!/usr/bin/env python3
# @Date    : 2020-05-25
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2

import os
from glob import glob
# import json
import yaml

from doc_parser import MarkdownParser

class MakePages:
    def __init__(self):
        # with open(path_conf, "r") as fp:
        #     configs = json.load(fp)
        # self.mkdocs_md_dir = configs["mkdocs_dir"]
        self.mkdocs_md_dir = 'D:\\Home\\workspace\\note\\internal'

    def rebuild(self):
        def walk_for_dirs(root_dir):
            for root, dirs, _ in os.walk(root_dir, topdown=False):
                self.update_nav(root)  # 生成根目录的 .pages 文件
                for subdir in dirs:  # 递归子目录
                    walk_for_dirs(subdir)

        walk_for_dirs(self.mkdocs_md_dir)

    def update_nav(self, path_md):
        """ 由于一个文件或目录的更新，重构 dir/.pages 配置文件 """
        if os.path.isdir(path_md):
            dir_md = path_md
        else:
            dir_md = os.path.dirname(path_md)

        # if os.path.exists(path_nav):
        #     with open(path_nav, 'r', encoding='utf-8') as fp:
        #         data = yaml.load(fp)
        # else:
        #     data = {}

        md_files = glob(os.path.join(dir_md, "*.md"))
        if not md_files:
            return

        dict_md = {}
        for file in md_files:
            md_parser = MarkdownParser()
            md_parser.load_file(file)
            title = md_parser.get_title()
            weight = int(md_parser.get_weight())

            if weight not in dict_md:
                dict_md[weight] = {}

            # path_rel = os.path.relpath(file, self.mkdocs_md_dir)
            file_name = os.path.basename(file)
            dict_md[weight][title] = file_name

        # def priority_for_title(pair):  # 排序
        #     title = pair[0]
        #     list_parts = title.split("-", 1)
        #     if len(list_parts) == 1:
        #         try:
        #             priority = int(list_parts[0])
        #             return priority
        #         except:
        #             pass

        list_priority = []
        for weight, dict_files in sorted(dict_md.items(), key=lambda d: d[0]):
            for title, file in sorted(dict_files.items(), key=lambda d: d[0]):  # priority_for_title
                list_priority.append({title: file})

        path_nav = os.path.join(dir_md, ".pages")
        with open(path_nav, 'w', encoding='utf-8') as fp:
            yaml.dump({"nav": list_priority}, fp, allow_unicode=True)


if __name__ == "__main__":
    o = MakePages()
    o.rebuild()
