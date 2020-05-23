#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.0.1

import os.path
import pngquant

def compress_by_pngquant(path_img):
    """ png32转png8，直接替换原文件 """
    pngquant.config()  # "/usr/bin/pngquant", min_quality=60, max_quality=90

    if os.path.isdir(path_img):
        quant_dir(dir=path_img, override=True, delete=0)
    else:
        pngquant.quant_image(path_img, override=True, delete=True)

#####################################################################

def getopt():
    import argparse

    parser = argparse.ArgumentParser("png2jpg", description="图像格式转换工具")
    parser.add_argument("-p", "--path", action="store", help="解析文件路径，可以是文件或目录")
    return parser.parse_args()


if __name__ == "__main__":
    args = getopt()

    if args.path:
        compress_by_pngquant(args.path)
    else:
        path = input("\n请输入待处理文件path(支持直接拖拽): ")
        while True:
            path = path.strip()
            if os.path.exists(path):
                compress_by_pngquant(path)
            else:
                print(f"Error: File [{path}] NOT found.")

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
