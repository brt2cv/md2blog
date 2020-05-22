#!/usr/bin/env python3
# @Date    : 2020-05-12
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.0.2

import re
from utils.log import make_logger
logger = make_logger()

class FormatHasBeenHugo(Exception):
    """ 格式已经符合Hugo要求，无需转换 """

class ErrorMkdocsLabel(Exception):
    """ 非法的label定义 """

class NullMarkdownFile(Exception):
    """ 空文件 """


class MarkdownFormatter:
    pattern_h1 = re.compile(r"# (.*)\n")

    # def __init__(self):
    #     self._clear_hugo()

    def _clear_hugo(self):
        self.curr_doc = {
            "path": "",
            "markdown_lines": [],
            "check_items": {},
            "hugo_info": {
                "title": "",
                "description": "",
                "date": None,
                "weight": 0,
                "tags": [],
                "categories": [],
                "keywords": []
            }
        }

    def parse_mkdocs(self, path_file):
        self._clear_hugo()
        self.curr_doc["path"] = path_file

        with open(path_file, "r", encoding="utf8") as fp:
            list_lines = fp.readlines()
            self.curr_doc["markdown_lines"] = list_lines

        if not list_lines:
            raise NullMarkdownFile()

        # check items in each line
        check_items = {"title", "tags"}
        self.curr_doc["check_items"] = check_items

        # 查找tags
        self.get_labels(list_lines)
        # remove the line
        self.curr_doc["markdown_lines"].pop(0)
        # 删除检查标记
        self.curr_doc["check_items"].remove("tags")

        hugo_mark = "title       = \""
        hugo_mark_len = len(hugo_mark)
        for line in list_lines:
            # 如果已经符合hugo_format，则无需转换格式（该检测仅限于H1标志前）
            if "title" in check_items:
                if line[:hugo_mark_len] == hugo_mark:
                    raise FormatHasBeenHugo()

            # 查找title
            if not self.curr_doc["hugo_info"]["title"]:
                self.title_mkdocs2hugo(line)

            if not check_items:
                logger.info("完成所有查询项的检测")
                break

        logger.debug(f"已完成mkdocs的元素遍历【{self.curr_doc['hugo_info']}】")

    def get_labels(self, lines):
        """ &label -> tags = ['label'] """
        first_line = lines[0]
        if first_line[0] == "&":
            list_labels = first_line.split()
            # self.curr_doc["hugo_info"]["tags"] = [label[1:] for label in list_labels]  # 去除&符号
            for label in list_labels:
                if label[0] != "&":
                    raise ErrorMkdocsLabel(f"{self.curr_doc['path']}: 非法的label定义【{label}】")
                self.curr_doc["hugo_info"]["tags"].append(label[1:])
        else:
            for line in lines:
                hugo_tag_prefix = "tags        = "
                if line.startswith("# "):
                    logger.debug("未发现tag标签")
                    break
                elif line.startswith(hugo_tag_prefix):
                    str_tags = line[len(hugo_tag_prefix):]
                    self.curr_doc["hugo_info"]["tags"] = eval(str_tags)
                    break

    def title_mkdocs2hugo(self, line):
        """ # Title -> title = "TitleName" """
        re_matches = re.match(self.pattern_h1, line)
        # print(re_matches)
        if re_matches:
            str_title = re_matches.group(1)
            # logger.debug(str_title)
            self.curr_doc["hugo_info"]["title"] = str_title
            self.curr_doc["check_items"].remove("title")

    def create_hugo_format(self):
        str_tags = "\"" + "\",\"".join(self.curr_doc["hugo_info"]["tags"]) + "\"" if self.curr_doc["hugo_info"]["tags"] else ""
        str_hugo_info = f"""<!--
+++
title       = "{self.curr_doc["hugo_info"]["title"]}"
description = ""
date        = ""
weight      = 3
tags        = [{str_tags}]
categories  = []
keywords    = []
+++ -->
"""
        self.curr_doc["markdown_lines"].insert(0, str_hugo_info)

        with open(self.curr_doc["path"], "w", encoding="utf8") as fp:
            fp.writelines(self.curr_doc["markdown_lines"])

    def img_compression(self, line):
        """ 压缩图像文件 """

    def img_png2jpg(self, line):
        """ 将png图像转jpg格式，更新line和图像命名 """


def test(path_file):
    fmt = MarkdownFormatter()
    fmt.parse_mkdocs(path_file)
    fmt.create_hugo_format()

def parse_dir(path_dir):
    import glob
    from collections import defaultdict

    list_files = glob.glob(f"{path_dir}/**/*.md", recursive=True)

    fmt = MarkdownFormatter()
    err_files = defaultdict(list)
    for path_file in list_files:
        try:
            fmt.parse_mkdocs(path_file)
            fmt.create_hugo_format()
        except FormatHasBeenHugo:
            pass
        except ErrorMkdocsLabel:
            # path_file = str(e).partition(":")[0]
            err_files["ErrorMkdocsLabel"].append(path_file)
        except NullMarkdownFile:
            err_files["NullMarkdownFile"].append(path_file)

    if err_files:
        for key, list_files in err_files.items():
            print(f">> 错误文件类型【{key}】")
            print(f"   文件列表： {list_files}")


if __name__ == "__main__":
    # test("Title.md")
    parse_dir("../documents")
