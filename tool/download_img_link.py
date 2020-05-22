#!/usr/bin/env python

###############################################################################
# Name:         Markdown - 图片下载
# Purpose:
# Author:       Bright Li
# Modified by:
# Created:      2020-02-21
# Version:      [0.0.2]
# RCS-ID:       $$
# Copyright:    (c)
# Licence:
###############################################################################

import os
import re
from utils import wreq

from utils.log import getLogger
logger = getLogger(1)

class MarkPicDownlder:
    re_pattern = re.compile(r"!\[\]\((http.*?)\)")

    def parse_markdown(self, path_markdown, output_file):
        self.lines_copy = []
        file_dir = os.path.dirname(output_file)
        basename = os.path.basename(output_file)
        pic_dir = os.path.join(file_dir, os.path.splitext(basename)[0])  # 同名文件夹
        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)

        index = 0
        with open(path_markdown, encoding="utf8") as fp:
            for line_text in fp:
                url_src = self.parse_link_pic(line_text)
                if not url_src:
                    self.lines_copy.append(line_text)
                    continue

                file_name = str(index) + os.path.splitext(url_src)[1]
                path_pic = os.path.join(pic_dir, file_name)
                if self.download_picture(url_src, path_pic):
                    path_pic_rel = os.path.relpath(path_pic, file_dir)
                    line_update = line_text.replace(url_src, path_pic_rel)
                    self.lines_copy.append(line_update)
                    index += 1
                else:
                    self.lines_copy.append(line_text)

        with open(output_file, "w", encoding="utf8") as fp:
            fp.writelines(self.lines_copy)

        logger.info(f"完成文档更新，保存至【{output_file}】")

    def parse_link_pic(self, text):
        re_match = re.search(self.re_pattern, text)
        if re_match:
            return re_match.group(1)
        else:
            return False

    def download_picture(self, url_src, path_save):
        if os.path.exists(path_save):
            logger.debug(f"已存在文件【{path_save}】")
            return True

        try:
            r = wreq.make_request(url_src)
        except wreq.RequestException:
            logger.warning(f"无法连接到【{url_src}】")
            return False
        else:
            with open(path_save, "wb") as fp:
                fp.write(r.content)
            return True


if __name__ == "__main__":
    def getopt():
        import argparse

        parser = argparse.ArgumentParser("Markdown - 图片下载", description="")
        parser.add_argument("path", action="store", help="Markdown文档路径")
        parser.add_argument("-d", "--save_dir", action="store", help="保存目录")
        parser.add_argument("-o", "--output_file", action="store", help="保存路径")
        return parser.parse_args()

    args = getopt()
    s = MarkPicDownlder()

    if args.output_file:
        path_save = args.output_file
    elif args.save_dir:
        file_name = os.path.basename(args.path)
        path_save = os.path.join(args.save_dir, file_name)
    else:
        path_save = args.path

    s.parse_markdown(args.path, path_save)
