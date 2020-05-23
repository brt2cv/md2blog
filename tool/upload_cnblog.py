#!/usr/bin/env python3
# @Date    : 2020-05-23
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.0.1

import os
import json
import xmlrpc.client

from db_mgr import DocumentsMgr

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
        self.doc_mgr = DocumentsMgr()

    def load_config(self, path_conf):
        with open(path_conf, "r") as fp:
            dict_conf = json.load(fp)
        for key, value in dict_conf.items():
            self.dict_conf[key] = value

    def _upload_img(self, path_img):
        pass

    def _new_blog(self, dict_post):
        postid = self.cnblog_server.metaWeblog.newPost(
                    self.dict_conf["blog_id"],
                    self.dict_conf["username"],
                    self.dict_conf["password"],
                    dict_post, True)
        print(f">> 完成blog的上传: [{postid}]")

    def _repost_blog(self, dict_post, postid):
        """ 重新发布 """
        postid = self.cnblog_server.metaWeblog.editPost(
                    postid,
                    self.dict_conf["username"],
                    self.dict_conf["password"],
                    dict_post, True)
        print(f">> 完成blog的更新: [{postid}]")

    def post_blog(self, md_parser):
        dict_post = dict(description="".join(md_parser.get_text()),
                         title=md_parser.metadata["title"],
                         categories=["[Markdown]"] + md_parser.metadata["categories"])

        postid = self.doc_mgr.exist_doc(md_parser.metadata["title"])
        if postid:
            self._repost_blog(dict_post, postid)
        else:
            self._new_blog(dict_post)

    def delete_blog(self, title):
        pass

    def rename_blog(self, src, dst):
        """ 上层封装 """
        pass

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
        title2id = {}
        recent_post = self.cnblog_server.metaWeblog.getRecentPosts(
                        self.dict_conf["blog_id"],
                        self.dict_conf["username"],
                        self.dict_conf["password"],
                        num)
        for post in recent_post:
            print(post)
            pass


#####################################################################

def getopt():
    import argparse

    parser = argparse.ArgumentParser("upload_cnblog", description="")
    parser.add_argument("-g", "--get", action="store_true", help="获取近期上传的列表")
    return parser.parse_args()


if __name__ == "__main__":
    from fmt_md import MarkdownFormatter, format_anything

    args = getopt()

    fmt = MarkdownFormatter()
    uploader = CnblogManager(".cnblog.json")

    def process_in_all(path_md):
        if not os.path.exists(path):
            print(f"Error: File [{path}] NOT found.")
            return

        # 格式化md
        format_anything(fmt, path_md)
        # 上传数据
        uploader.post_blog(fmt)


    # 处理命令行参数
    if args.get:
        uploader.get_recent_post()

    else:
        path = input("请输入待处理文件path(支持直接拖拽): ")
        while True:
            path = path.strip()
            process_in_all(path)

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
