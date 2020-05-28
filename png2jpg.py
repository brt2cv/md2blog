#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.0.1

import os
from PIL import Image


def _callBash():
    """
    # 安装
    sudo apt-get install imagemagick

    # ${0%.png}.jpg: 设置新转换的图像文件的名字，% 符号用来删除源文件的扩展名
    ls -1 *.png | xargs -n 1 bash -c 'convert "$0" "${0%.png}.jpg"'  # 从PNG转换到JPG
    ls -1 *.jpg | xargs -n 1 bash -c 'convert "$0" "${0%.jpg}.png"'  # 从JPG转换到PNG

    # 或者
    mogrify -format jpg *.png
    """

def png2jpg(path_png, quality):
    """ 转换png文件，并返回生成的jpg文件路径 """
    path_new = path_png[:-3] + "jpg"

    im = Image.open(path_png)  # rgba
    im_rgb = im.convert(mode="RGB")
    im_rgb.save(path_new, quality=quality)
    return path_new

def png2smaller(path_png, quality, least_ratio=0.75, new_file_prefix="keepng_"):
    """ png2jpg()未考虑转换结果，_ex()则对比转换结果，
        如果转换后文件变大了，则保留原png.
        为了避免下次重复转换png，文件名增加前缀 keepng_
    """
    if os.path.basename(path_png).startswith(new_file_prefix):
        return

    path_new = png2jpg(path_png, quality)
    # 比较size: 除非显著压缩，否则保留原图像
    if os.path.getsize(path_new) < os.path.getsize(path_png) * least_ratio:
        os.remove(path_png)
    else:
        os.remove(path_new)
        path_new = os.path.join(os.path.dirname(path_png),
                   new_file_prefix + os.path.basename(path_png))
        os.rename(path_png, path_new)
    return path_new

def png_to_jpg_mask(pngPath, quality):
    im = Image.open(pngPath)
    r, g, b, a = im.convert(mode="RGBA").split()

    name, ext = os.path.splitext(pngPath)
    jpgPath = name + ".jpg"
    maskPath = name + ".mask.jpg"

    a.convert(mode="L")
    a.save(maskPath)

    im.save(im.convert(mode="RGB"), quality=quality)

def jpg_mask_to_png(jpgPath, maskPath):
    """ 将分开的两张图片合成原图 """
    im_jpg = Image.open(jpgPath)
    im_mask = Image.open(maskPath)

    im_jpg.putalpha(im_mask)
    im_jpg.save(jpgPath + ".png")

def resize(path_src, ratio=0.5, output_shape=None, min_size=0, antialias=True):
    if os.path.getsize(path_src) < min_size:
        return

    im = Image.open(path_src)
    # 开启抗锯齿，耗时增加8倍左右
    resample = Image.ANTIALIAS if antialias else Image.NEAREST
    # 注意：pillow.size 与 ndarray.size 顺序不同
    if output_shape:
        w, h = output_shape
    else:
        list_ = [int(i*ratio) for i in im.size]
        w, h = list_
    im_new = im.resize((w, h), resample)
    im_new.save(path_src, "JPEG")


#####################################################################

def getopt():
    import argparse

    parser = argparse.ArgumentParser("png2jpg", description="图像格式转换工具")
    parser.add_argument("-p", "--path", action="store", help="解析文件路径，可以是文件或目录")
    parser.add_argument("-q", "--quality", action="store", type=int, default=85, help="图像质量")
    return parser.parse_args()


if __name__ == "__main__":
    args = getopt()

    if args.path:
        png2jpg(args.path, args.quality)
    else:
        path = input("\n请输入待处理文件path(支持直接拖拽): ")
        while True:
            path = path.strip()
            if os.path.exists(path):
                png2jpg(path, args.quality)
            else:
                print(f"Error: File [{path}] NOT found.")

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
