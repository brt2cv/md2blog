import os
import glob
from collections import defaultdict

from doc_parser import MarkdownParser, NullMarkdownFile


class MarkdownFormatter(MarkdownParser):

    def format(self):
        if not self.check_list["find_TOC"]:
            self.insert_text(self.check_list["index_H2"], "[TOC]\n\n")

        if self.check_list["index_H1"]:
            self.pop_text(self.check_list["index_H1"])

        if not self.check_list["has_metadata"]:
            self._insert_meta()
        self._update_serial_num()

        # 图像处理
        self.img_processing()

    def overwrite(self):
        with open(self.file_path, "w", encoding="utf8") as fp:
            fp.writelines(self.get_text())

    def _insert_meta(self):
        def list_as_str(data: list):
            # str(data) -> 单引号，不符合markdown标准
            return "[\"" + "\",\"".join(data) + "\"]" if data else "[]"

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
        self.text_lines.insert(0, str_md_info)

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

        def update_line(line):
            serial_num = get_serial()
            if self.check_list["has_serial_num"]:
                prefix, _, text = line.split(maxsplit=2)
            else:
                prefix, text = line.split(maxsplit=1)

            return f"{prefix} {serial_num} {text}"

        for index, line in enumerate(self.text_lines):
            if line.startswith("## "):
                x += 1
                y,z = 0,0
                self.text_lines[index] = update_line(line)
                self.set_
            elif line.startswith("### "):
                y += 1
                z = 0
                self.text_lines[index] = update_line(line)
            elif line.startswith("#### "):
                z += 1
                self.text_lines[index] = update_line(line)


#####################################################################

def getopt():
    import argparse

    parser = argparse.ArgumentParser("格式化mkdocs文档", description="")
    parser.add_argument("-p", "--path", action="store", help="解析文件路径，可以是文件或目录")
    return parser.parse_args()

def format_one_doc(fmt, path_file):
    fmt.load_file(path_file)
    fmt.format()
    fmt.overwrite()

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
            path = path.strip()
            if os.path.exists(path):
                format_anything(fmt, path)
            else:
                print(f"Error: File [{path}] NOT found.")

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
