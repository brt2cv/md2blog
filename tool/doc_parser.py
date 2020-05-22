#!/usr/bin/env python3
# @Date    : 2020-05-22
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.2

import re


class NullMarkdownFile(Exception):
    """ 空文件 """

# class MetaDataMissing(Exception):
#     """ 缺失元数据 """

# class TOC_Missing(Exception):
#     """ 缺失[TOC]标识 """


class MarkdownParser:
    """ 支持以下两种格式：
        1. 含H1格式的原生md文件（mkdocs）
        2. title = "xxx"... 定义元数据的hugo格式
    """
    pattern_h1 = re.compile(r"# (.*)\n")
    pattern_img_link = re.compile(r"!\[\]\((http.*?)\)")
    pattern_img_png = re.compile(r"!\[\]\((.*\.png)\)")

    def _clear_metadata(self):
        self.file_path = ""
        self.text_lines = []
        self.metadata = {
            "title": "",
            "description": "",
            "date": None,
            "weight": 3,
            "tags": [],
            "categories": [],
            "keywords": []
        }
        self.check_list = {
            "index_H1": None,
            "find_TOC": False,
            "index_H2": None,
            "has_metadata": False,
            "has_serial_num": None
        }

    def load_file(self, path_file):
        self._clear_metadata()
        self.file_path = path_file
        with open(self.file_path, "r", encoding="utf8") as fp:
            self.text_lines = fp.readlines()

        if not self.text_lines:
            raise NullMarkdownFile()

        self._parse_metadata()

    def _parse_metadata(self):
        edit_meta = False
        for index, line in enumerate(self.text_lines):
            if edit_meta:
                if line.startswith("+++ -->"):
                    edit_meta = False
                else:
                    key, value = line.split("=")
                    self.metadata[key.strip()] = eval(value)
                continue

            if line.startswith("+++"):
                edit_meta = True
                self.check_list["has_metadata"] = True
            elif line.startswith("## "):  # 检测H2之前的文块
                self.check_list["index_H2"] = index
                # 检测‘has_serial_num’
                H2_text = line[2:].lstrip()
                self.check_list["has_serial_num"] = H2_text.startswith("1. ")
                break
            # 检测title
            elif line.startswith("# "):  # H1
                if not self.metadata["title"]:
                    self.metadata["title"] = line[2:].strip()
                self.check_list["index_H1"] = index
            elif line.startswith("[TOC]"):
                self.check_list["find_TOC"] = True

        # print("MetaData:", self.metadata)
