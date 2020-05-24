#!/usr/bin/env python
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.2

import os
import json
import xmlrpc.client

from fmt_md import MarkdownFormatter, format_anything
from db_mgr import DocumentsMgr

try:
    from utils.log import getLogger
except ImportError:
    from logging import getLogger
logger = getLogger()


class PostidNotUnique(Exception):
    """ 获取到postid不唯一，可能是存在同名title的文档 """

class CnblogManager:
    def __init__(self, path_conf):
        self.dict_conf = {
            "blog_url": "",
            "blog_id" : "",
            "app_key" : "",
            "username": "",
            "password": "",
        }
        self.load_config(path_conf)
        self.cnblog_server = xmlrpc.client.ServerProxy(self.dict_conf["blog_url"])
        self.mime = None

        self.md_fmt = MarkdownFormatter()
        self.doc_mgr = DocumentsMgr()

    def load_config(self, path_conf):
        with open(path_conf, "r") as fp:
            dict_conf = json.load(fp)
        for key, value in dict_conf.items():
            self.dict_conf[key] = value

    def get_postid(self, title_or_postid):
        if title_or_postid.isdecimal():
            postid = title_or_postid
        else:
            postid = self.doc_mgr.get_postid(title_or_postid)
            if isinstance(postid, list):
                raise PostidNotUnique(f"获取到postid不唯一，请指定postid值: 【{postid}】")
        return postid

    def get_user_info(self):
        """ return a list of user-info """
        user_info = self.cnblog_server.blogger.getUsersBlogs(
                    self.dict_conf["blog_url"],
                    self.dict_conf["username"],
                    self.dict_conf["password"])
        return user_info

    def _upload_img(self, path_img):
        file_name = os.path.basename(path_img)
        _, suffix = os.path.splitext(file_name)
        with open(path_img, 'rb') as fp:
            file = {
                "bits": fp.read(),
                "name": file_name,
                "type": self.mime[suffix]
            }
        url_new = self.cnblog_server.metaWeblog.newMediaObject(
                    self.dict_conf["blog_id"],
                    self.dict_conf["username"],
                    self.dict_conf["password"],
                    file)
        return url_new["url"]

    def _load_mime(self):
        with open("mime.json", "r") as fp:
            self.mime = json.load(fp)

    def _new_blog(self):
        md_parser = self.md_fmt

        if self.mime is None:
            self._load_mime()

        # 上传图片
        dict_images = md_parser.get_images("all")
        list_remove = []
        for line, url in dict_images.items():
            if url.startswith("http"):
                list_remove.append(line)

        for line in list_remove:
            del dict_images[line]

        md_parser.process_images(dict_images, self._upload_img)  # 更新上传服务器的URL
        dict_post = {
            "title": md_parser.metadata["title"],
            "categories": ["[Markdown]"] + md_parser.metadata["categories"],
            "description": "".join(md_parser.get_text())
        }
        postid = self.cnblog_server.metaWeblog.newPost(
                    self.dict_conf["blog_id"],
                    self.dict_conf["username"],
                    self.dict_conf["password"],
                    dict_post, True)

        print(f">> 完成blog的上传: [{postid}]")

        # 更新本地图像链接，用于修改文档时调用已上传图像

    def _repost_blog(self, postid):
        """ 重新发布 """
        postid = self.cnblog_server.metaWeblog.editPost(
                    postid,
                    self.dict_conf["username"],
                    self.dict_conf["password"],
                    dict_post, True)
        print(f">> 完成blog的更新: [{postid}]")

    def post_blog(self, path_md):
        # 格式化md
        format_anything(self.md_fmt, path_md)

        postid = self.get_postid(self.md_fmt.metadata["title"])
        if postid:
            self._repost_blog(postid)
        else:
            self._new_blog()

    def download_blog(self, title_or_postid):
        postid = self.get_postid(title_or_postid)
        if not postid:
            logger.error(f"本地数据库未存储blog: 【{title_or_postid}】，\
但不确定博客园服务器状态。如有必要，请指定postid值，重新查询。")
            return

        list_data = self.cnblog_server.metaWeblog.getPost(
                    postid,
                    self.dict_conf["username"],
                    self.dict_conf["password"])
        blog_data = list_data[0]
        print(f">> 已下载blog: [{blog_data}]")

    def delete_blog(self, postid_or_postid):
        postid = self.get_postid(title_or_postid)
        if not postid:
            logger.error(f"本地数据库未存储blog: 【{title_or_postid}】，\
但不确定博客园服务器状态。如有必要，请指定postid值，重新查询。")
            return

        try:
            self.cnblog_server.blogger.deletePost(
                    self.dict_conf["app_key"],
                    postid,
                    self.dict_conf["username"],
                    self.dict_conf["password"],
                    True)
        except Exception as e:
            logger.error(e)
        else:
            print(f"已删除blog: 【{title}】")

    def rename_blog(self, postid, path_new_md):
        postid = self.get_postid(title_or_postid)
        if not postid:
            logger.error(f"本地数据库未存储blog: 【{title_or_postid}】，\
但不确定博客园服务器状态。如有必要，请指定postid值，重新查询。")
            return

        self.delete_blog(postid)
        self.post_blog(path_new_md)

    def get_recent_post(self, num=9999):
        """
        return: {
            'dateCreated': <DateTime '20200523T20:47:00' at 0x7fbba8995fa0>,
            'description': '...',
            'title': 'Python数据结构',
            'categories': ['[随笔分类]33-python', '[随笔分类]3-syntax'],
            'enclosure': {'length': 0},
            'link': 'https://www.cnblogs.com/brt2/p/12944353.html',
            'permalink': 'https://www.cnblogs.com/brt2/p/12944353.html',
            'postid': '12944353',
            'source': {},
            'userid': '-2'
        }
        """
        recent_post = self.cnblog_server.metaWeblog.getRecentPosts(
                        self.dict_conf["blog_id"],
                        self.dict_conf["username"],
                        self.dict_conf["password"],
                        num)
        for post in recent_post:
            print(post)


#####################################################################

def getopt():
    import argparse

    parser = argparse.ArgumentParser("upload_cnblog", description="")
    parser.add_argument("-u", "--user", action="store_true", help="获取用户博客信息")
    parser.add_argument("-g", "--get", action="store_true", help="获取近期上传的列表")
    parser.add_argument("-d", "--delete", action="store", help="删除博客文档")
    parser.add_argument("-s", "--save", action="store", help="下载博客文档")
    return parser.parse_args()


if __name__ == "__main__":
    args = getopt()

    uploader = CnblogManager(".cnblog.json")

    # 处理命令行参数
    if args.user:
        uploader.get_user_info()
    elif args.get:
        uploader.get_recent_post()
    elif args.delete:
        uploader.delete_blog(args.delete)
    elif args.save:
        uploader.download_blog(args.save)
    else:
        path = input("请输入待处理文件path(支持直接拖拽): ")
        while True:
            path = path.strip()
            try:
                uploader.post_blog(path)
            except FileNotFoundError:
                print(f"Error: File [{path}] NOT found.")

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
