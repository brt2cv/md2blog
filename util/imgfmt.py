#!/usr/bin/env python3
# @Date    : 2020-08-07
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.3

import os
import subprocess
from glob import glob

from PIL import Image
import pngquant
from . import jhead

from logging import getLogger
logger = getLogger()


def isLarge(path_img, thresh=0.4):
    """ return true if ratio > thresh """
    w, h = jhead.get_resolution(path_img)
    size = jhead.get_size(path_img, unit="B")
    ratio = size / (w*h)
    return ratio > thresh

def resize(path_src, ratio=0.5, output_shape=None, min_size=0, max_shape=None,
           antialias=True, save_as_jpg=True):
    """ output_shape: list(w, h)
        min_size: 忽略存储空间小于此数值的小图片
        max_shape: 若为None，则直接缩放一次
                   否则递归压缩尺寸高于此数值的大图片, type: list(w, h)
    """
    if os.path.getsize(path_src) < min_size:
        return

    # 开启抗锯齿，耗时增加8倍左右
    resample = Image.ANTIALIAS if antialias else Image.NEAREST

    im = Image.open(path_src)
    if im.mode == "RGBA" and save_as_jpg:
        im = im.convert("RGB")

    if output_shape:
        w, h = output_shape
        im_new = im.resize((w, h), resample)
    elif max_shape is None:  # 执行一次缩放
        # 注意：pillow.size 与 ndarray.size 顺序不同
        list_ = [int(i*ratio) for i in im.size]
        im_new = im.resize(list_, resample)
    else:  # 递归缩减
        while True:
            w, h = im.size
            if w < max_shape[0] and h < max_shape[1]:
                break
            w, h = [int(i*ratio) for i in im.size]
            im = im.resize((w, h), resample)

        im_new = im

    if save_as_jpg:
        im_new.save(path_src, "JPEG")
    else:
        im_new.save(path_src)

#####################################################################

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

def _png2jpg_base(path_png, quality):
    """ 转换png文件，并返回生成的jpg文件路径 """
    path_new = path_png[:-3] + "jpg"

    im = Image.open(path_png)  # rgba
    im_rgb = im.convert(mode="RGB")
    im_rgb.save(path_new, quality=quality)
    return path_new

def _png2jpg_byMogrify(path_png):
    subprocess.run("mogrify -format jpg {}".format(path_png), shell=True)
    path_base, _ = os.path.splitext(path_png)
    return path_base + ".jpg"

def png2jpg(path_png, quality, least_ratio=0.75, removePng=True):
    """ png2jpg_base()未考虑转换结果。
        png2jpg_ex()则对比转换结果，如果转换后文件变大了，则保留原png.
        为了避免下次重复转换png，文件名增加前缀 keepng_
    """
    path_jpg = _png2jpg_base(path_png, quality)
    if least_ratio is None:
        ret = path_jpg
    # 比较size: 除非显著压缩，否则保留原图像
    elif os.path.getsize(path_jpg) < os.path.getsize(path_png) * least_ratio:
        ret = path_jpg
    else:
        os.remove(path_jpg)
        removePng = False
        ret = path_png

    if removePng:
        os.remove(path_png)
    return ret

# def png_to_jpg_mask(pngPath, quality):
#     im = Image.open(pngPath)
#     r, g, b, a = im.convert(mode="RGBA").split()

#     name, _ = os.path.splitext(pngPath)
#     # jpgPath = name + ".jpg"
#     maskPath = name + ".mask.jpg"

#     a.convert(mode="L")
#     a.save(maskPath)

#     im.save(im.convert(mode="RGB"), quality=quality)

# def jpg_mask_to_png(jpgPath, maskPath):
#     """ 将分开的两张图片合成原图 """
#     im_jpg = Image.open(jpgPath)
#     im_mask = Image.open(maskPath)

#     im_jpg.putalpha(im_mask)
#     im_jpg.save(jpgPath + ".png")

#####################################################################

COMPRESS_ALLOWED_EXT = ["png", "jpg", "jpeg"]
COMPRESS_ALLOWED_EXT.extend([ext.upper() for ext in COMPRESS_ALLOWED_EXT])

def compress_by_pngquant(path_img):
    """ png32转png8，直接替换原文件 """
    pngquant.config(min_quality=85, max_quality=95)  # "/usr/bin/pngquant", min_quality=60, max_quality=90

    if os.path.isdir(path_img):
        # pngquant.quant_dir(dir=path_img, override=True, delete=0)
        for ext in COMPRESS_ALLOWED_EXT:
            for path_ in glob(r"{}/**/*.{}".format(path_img, ext), recursive=True):
                pngquant.quant_image(path_, override=True, delete=True)
    else:
        _, ext = os.path.splitext(path_img)
        if ext and ext[1:] in COMPRESS_ALLOWED_EXT:
            pngquant.quant_image(path_img, override=True, delete=True)

#####################################################################

wreq_import_error = None
try:
    from utils import wreq
except ImportError:
    wreq_import_error = ">>> 无法载入utils.wreq模块，请参考 https://gitee.com/brt2/utils/blob/dev/wreq.py"


def format_ext(file_name):
    """ return a formated file_name """
    basename = os.path.basename(file_name)
    base, suffix = os.path.splitext(basename)

    if not suffix:
        try_suffix = ["jpg", "jpeg", "png", "gif"]  # 并未考虑大小写
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
