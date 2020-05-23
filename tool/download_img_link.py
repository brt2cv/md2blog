#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 2.0.0

import os
import re
from utils import wreq

from utils.log import getLogger
logger = getLogger()

from doc_parser import MarkdownParser

def download_src(url_src, save_dir):
    try:
        r = wreq.make_request(url_src)
        path_save = os.path.join(save_dir, os.path.basename(url_src))
        with open(path_save, "wb") as fp:
            fp.write(r.content)
        return path_save

    except wreq.RequestException:
        logger.error(f"无法连接到【{url_src}】")
        return
