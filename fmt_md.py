#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.0.2

import os
import re
import datetime
import glob
from collections import defaultdict

from doc_parser import MarkdownParser, NullMarkdownFile
from png2jpg import png2smaller, resize


class MarkdownFormatter(MarkdownParser):

    def format(self):
        # self._update_categories()

        if not self.check_list["find_TOC"]:
            self.insert_text(self.check_list["index_H2"], "[TOC]\n\n")

        if self.check_list["index_H1"]:
            self.pop_text(self.check_list["index_H1"])

        self.update_meta()

        self._update_serial_num()

        # 图像处理
        if self.get_images("http") and input("是否尝试下载超链接图片？[Y/n]: ").lower() != "n":
            # self.unlock_text()
            self.download_img()

        # 默认启用 png -> jpg
        self.convert_png2jpg()

        # 对于高分辨率图像进行压缩
        self.resize_high_resolution()

        # 判断下载图像的size，执行resize或压缩
        self.compress_bigimg()

    def overwrite(self):
        with open(self.file_path, "w", encoding="utf8") as fp:
            fp.writelines(self.get_text())
        print(f"Markdown文件已保存【{self.file_path}】")

    def _make_meta_line(self):
        def list_as_str(data: list):
            # str(data) -> 单引号，不符合markdown标准
            return "[\"" + "\",\"".join(data) + "\"]" if data else "[]"

        self.metadata["date"] = str(datetime.date.today())

        # date数据由于使用eval()反序列化，故必须使用""作为字符串
        str_md_info = f"""<!--
+++
title       = "{self.metadata['title']}"
description = "{self.metadata['description']}"
date        = "{self.metadata['date']}"
weight      = {self.metadata['weight']}
tags        = {list_as_str(self.metadata.get('tags'))}
categories  = {list_as_str(self.metadata.get('categories'))}
keywords    = {list_as_str(self.metadata.get('keywords'))}
+++ -->
"""
        return str_md_info

    def update_meta(self):
        meta_line = self._make_meta_line()
        if self.meta_range[0] is not None:
        # def _remove_old_meta(self):
            __text_lines = self.get_text()
            meta_start, meta_end = self.meta_range
            if meta_start is not None:
                self.set_text(__text_lines[:meta_start] + __text_lines[meta_end +1:])

        # def _insert_meta(self):
            self.insert_text(0, meta_line)
            self.meta_range = [None, None]
        else:
            self.modify_text(0, meta_line)

    def _update_serial_num(self):
        """ 使用3级序号：1.2.4. xxx """
        x, y, z = 0, 0, 0
        def get_serial():
            serial_num = ""
            for i in [x, y, z]:
                if i:
                    serial_num += f"{i}."
                else:
                    break
            return serial_num

        pattern_headline = re.compile(r"(#+) +(\d+\.\S*)? *(.*)")

        def update_line(line):
            serial_num = get_serial()
            # if self.check_list["has_serial_num"]:
            #     prefix, _, text = line.split(maxsplit=2)
            # else:
            #     prefix, text = line.split(maxsplit=1)
            prefix, _, text = re.match(pattern_headline, line).groups()
            return f"{prefix} {serial_num} {text}"

        for index, line in enumerate(self.get_text()):
            if line.startswith("## "):
                x += 1
                y,z = 0,0
                self.modify_text(index, update_line(line))
            elif line.startswith("### "):
                y += 1
                z = 0
                self.modify_text(index, update_line(line))
            elif line.startswith("#### "):
                z += 1
                self.modify_text(index, update_line(line))

    def download_img(self):
        from download_img_link import download_src

        dict_images = self.get_images("http")
        # 生成图像目录
        dir_img, _ = os.path.splitext(self.file_path)
        if not os.path.exists(dir_img):
            os.makedirs(dir_img)
        self.process_images(dict_images, lambda url: download_src(url, dir_img))

    def convert_png2jpg(self):
        path_rel_start = os.path.dirname(self.file_path)
        def png2jpg_and_return_relpath(path_png):
            path_jpg = png2smaller(path_png, 85)
            return os.path.relpath(path_jpg, path_rel_start)

        dict_images = self.get_images("png")
        self.process_images(dict_images, png2jpg_and_return_relpath)
        # 删除原png文件
        # for path_img in dict_images.values():
        #     os.remove(path_img)

    def compress_jpg(self):
        pass

    def compress_bigimg(self):
        pass

    def resize_high_resolution(self, save_as_jpg=True):
        dict_images_png = self.get_images("png")
        dict_images_jpg = self.get_images("jpg")
        callback = lambda url: resize(url, ratio=0.6, min_size=10240,
                                      max_shape=[680,680], save_as_jpg=save_as_jpg)
        self.process_images({**dict_images_png, **dict_images_jpg}, callback)

#####################################################################

def getopt():
    import argparse

    parser = argparse.ArgumentParser("格式化mkdocs文档", description="")
    parser.add_argument("-p", "--path", action="store", help="解析文件路径，可以是文件或目录")
    return parser.parse_args()

def format_one_doc(fmt, path_file):
    fmt.load_file(path_file)
    fmt.format()

def format_dir(fmt, path_dir):
    list_files = glob.glob(f"{path_dir}/**/*.md", recursive=True)

    err_files = defaultdict(list)
    for path_file in list_files:
        try:
            format_one_doc(fmt, path_file)
        except NullMarkdownFile:
            err_files["NullMarkdownFile"].append(path_file)

    if err_files:
        for key, list_files in err_files.items():
            print(f">> 错误文件类型【{key}】")
            print(f"   文件列表： {list_files}")

def format_anything(fmt, path):
    if os.path.isdir(path):
        format_dir(fmt, path)
    else:
        format_one_doc(fmt, path)


if __name__ == "__main__":
    args = getopt()
    fmt = MarkdownFormatter()

    if args.path:
        format_anything(fmt, args.path)
    else:
        path = input("\n请输入待处理文件path(支持直接拖拽): ")
        while True:
            path = path.strip().strip('"')
            if os.path.exists(path):
                format_anything(fmt, path)
                fmt.overwrite()
            else:
                print(f"Error: File [{path}] NOT found.")

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
