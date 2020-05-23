#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.2

import os.path
import re


class NullMarkdownFile(Exception):
    """ 空文件 """

class TextLocked(Exception):
    """ 文本内容已加锁，当前不可修改 """

# class MetaDataMissing(Exception):
#     """ 缺失元数据 """

# class TOC_Missing(Exception):
#     """ 缺失[TOC]标识 """


class MarkdownParser:
    """ 支持以下两种格式：
        1. 含H1格式的原生md文件（mkdocs）
        2. title = "xxx"... 定义元数据的hugo格式
    """
    pattern_images = {
        "all":  re.compile(r"!\[\]\((.*)\)"),
        "png":  re.compile(r"!\[\]\((.*\.png)\)"),
        "link": re.compile(r"!\[\]\((http.*?)\)"),
    }

    def _clear_metadata(self):
        self.file_path = ""
        self.__text_lines = []
        self.__text_lock = False
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
            "has_metadata": False
        }

    def get_text(self):
        """ 并不能保证text内容不被改写 """
        return self.__text_lines

    def _set_text(self, content):
        if not content.endswith("\n"):
            content += "\n"
        return content

    def modify_text(self, index, content):
        self.check_lock()
        self.__text_lines[index] = self._set_text(content)

    def insert_text(self, index, content):
        self.check_lock()
        self.__text_lines.insert(index, self._set_text(content))

    def pop_text(self, index):
        self.check_lock()
        self.__text_lines.pop(index)

    def lock_text(self):
        self.__text_lock = True

    def unlock_text(self):
        self.__text_lock = False

    def check_lock(self):
        if self.__text_lock:
            raise TextLocked()

    def load_file(self, path_file):
        self._clear_metadata()
        self.file_path = path_file
        with open(self.file_path, "r", encoding="utf8") as fp:
            self.__text_lines = fp.readlines()

        if not self.get_text():
            raise NullMarkdownFile()

        self._parse_metadata()

    def _parse_metadata(self):
        edit_meta = False
        for index, line in enumerate(self.get_text()):
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
                # H2_text = line[2:].lstrip()
                # self.check_list["has_serial_num"] = H2_text.startswith("1. ")
                break
            # 检测title
            elif line.startswith("# "):  # H1
                if not self.metadata["title"]:
                    self.metadata["title"] = line[2:].strip()
                self.check_list["index_H1"] = index
            elif line.startswith("[TOC]"):
                self.check_list["find_TOC"] = True

        # print("MetaData:", self.metadata)

    def get_images(self, type_="all"):
        """ 临时有效，会加锁文本数据
            type_ in ("all", "png", "link")
        """
        self.lock_text()

        def match_regex(pattern, text):
            """ 适用于一个group的正则式 """
            re_match = re.search(pattern, text)
            return re_match.group(1) if re_match else None

        dict_images = {}  # line: url
        for index, line in enumerate(self.get_text()):
            url_img = match_regex(self.pattern_images[type_], line)
            if url_img:
                # 相对路径转换
                if not url_img.startswith("http") and not os.path.isabs(url_img):
                    url_img = os.path.join(os.path.dirname(self.file_path), url_img)
                dict_images[index] = url_img
        return dict_images

    def process_images(self, dict_images, callback):
        """ callback(url) -> new_url
        """
        self.unlock_text()
        for line_idx, url_img in dict_images.items():
            url_new = callback(url_img)
            if url_new:
                self.modify_text(line_idx, f"![]({url_new})")
