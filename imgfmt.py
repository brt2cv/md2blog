#!/usr/bin/env python3
# @Date    : 2020-09-03
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.2.1

import os.path
from util import imgfmt
from logging import getLogger

logger = getLogger()


def getopt():
    import argparse

    parser = argparse.ArgumentParser("ImgFormatter.py", description="图像格式转换工具")
    parser.add_argument("-p", "--path", action="store", help="解析文件路径，可以是文件或目录")
    parser.add_argument("-s", "--resize", action="store", type=float, help="图像缩放比例，默认0.6")
    parser.add_argument("-c", "--compress", action="store_true", help="使用pngquant压缩图像")
    parser.add_argument("-u", "--url_download", action="store_true", help="下载图片，请通过'--path'输入图像的URL")
    parser.add_argument("-j", "--png2jpg", action="store", type=int, help="设置png2jpg转换时的jpg图像质量，默认85")
    parser.add_argument("-w", "--webp2jpg", action="store_true", help="将webp图像转换为jpg")
    return parser.parse_args()


if __name__ == "__main__":
    args = getopt()

    def switch_opt(args, path_img):
        if args.png2jpg:
            imgfmt.png2jpg(path_img, args.png2jpg)
        elif args.webp2jpg:
            imgfmt.webp2jpg(path_img)
        elif args.resize:
            imgfmt.resize(path, ratio=args.resize, min_size=10240)  #  max_shape=[888,888]
        elif args.compress:
            logger.debug(">>> 压缩图像的jpg质量尚未开发，敬请期待...")
            imgfmt.compress_by_pngquant(path_img)
        elif args.url_download:
            if imgfmt.wreq_import_error:
                print(imgfmt.wreq_import_error)
                return
            path_save = input("--> 请输入存储路径: ")
            if not path_save:
                logger.error("未获取到有效存储路径")
                return
            imgfmt.download_src(args.path, path_save)
        else:
            raise Exception("未知的指令")

    def check_path(path):
        if os.path.isdir(path):
            from glob import glob

            logger.info("当前路径为目录，将遍历目录下的所有文件")
            list_files = glob(os.path.join(path, "*"))
            for path_file in list_files:
                switch_opt(args, path_file)
        elif os.path.isfile(path):
            switch_opt(args, path)
        else:
            print(f"Error: File [{path}] NOT found.")

    def path_str2list(path_str):
        path = path_str.strip()

        for q in ["\"", "\'"]:
            multi_files_gap = "{0} {0}".format(q)
            if path.find(multi_files_gap) >= 0:
                list_args = path.split(multi_files_gap)
                # break
                return [path.strip(q) for path in list_args]

        return [path.strip("\"").strip("\'")]

    if args.path:
        check_path(args, args.path)
    else:
        path = input("\n请输入待处理文件path(支持直接拖拽): ")
        while True:

            ret_list = path_str2list(path)
            for path in ret_list:
                check_path(path)

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
