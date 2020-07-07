#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 2.0.1

import os
from utils import wreq

from utils.log import getLogger
logger = getLogger()

def format_ext(file_name):
    """ return a formated file_name """
    basename = os.path.basename(file_name)
    base, suffix = os.path.splitext(basename)

    if not suffix:
        try_suffix = ["jpg", "png", "gif"]
        for i in try_suffix:
            if basename.find(i) >= 0:
                suffix = "." + i
                break
    if not suffix:
        logger.warning(f"图片【{file_name}】没有扩展名，需要手动判断类型")
        suffix = input(f"图片【{file_name}】没有扩展名，请手动填写，默认为'jpg': ")
        if not suffix:
            suffix = ".jpg"
        elif suffix[0] != ".":
            suffix = "." + suffix

    file_name2 = base + suffix
    return file_name2


def download_src(url_src, save_dir):
    index = 0
    list_files = os.listdir(save_dir)
    for file_name in list_files:
        x = file_name.split("_", 1)[0]
        try:
            index = max(int(x) +1, index)
        except ValueError:
            continue

    # 验证扩展名
    file_name = format_ext(url_src)

    # 下载图像
    path_save = os.path.join(save_dir,
                "{}_{}".format(index, file_name))

    try:
        r = wreq.make_request(url_src)
        with open(path_save, "wb") as fp:
            fp.write(r.content)
        return path_save

    except wreq.RequestException:
        logger.error(f"无法连接到【{url_src}】")
        return
