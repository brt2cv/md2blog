#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.0.1

import json
import xmlrpc.client

class CnblogUploader:
    def __init__(self, path_conf):
        self.dict_conf = {
            "username": "",
            "password": "",
            "blog_url": ""
            "blog_id": "anything"
        }
        self.load_config(path_conf)
        self.cnblog_server = xmlrpc.client.ServerProxy(self.dict_conf["blog_url"])

    def load_config(self, path_conf):
        with open(path_conf, "r") as fp:
            dict_conf = json.load(fp)
        for key, value in dict_conf.items():
            self.dict_conf[key] = value

    def upload_md(self, md_parser):
        post = dict(description="".join(md_parser.get_text()),
                    title=md_parser.metadata["title"],
                    categories=md_parser.metadata["categories"])
        self.cnblog_server.metaWeblog.newPost(self.dict_conf["blog_id"],
                                              self.dict_conf["username"],
                                              self.dict_conf["password"],
                                              post, True)

    def upload_img(self, path_img):
        pass


if __name__ == "__main__":
    from fmt_md import MarkdownFormatter, format_anything

    args = getopt()

    fmt = MarkdownFormatter()
    uploader = CnblogUploader()
    uploader.load_config(".cnblog.json")

    def process_in_all(path_md):
        if not os.path.exists(path):
            print(f"Error: File [{path}] NOT found.")
            return

        # 格式化md
        format_anything(fmt, path_md)
        # 上传数据
        uploader.upload_md(fmt)

    path = input("请输入待处理文件path(支持直接拖拽): ")
    while True:
        path = path.strip()
        process_in_all(path)

        path = input("继续输入path，按[Q]退出: ")
        if path.lower() == "q":
            break
