#!/usr/bin/env python
# @Date    : 2020-05-25
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.2

import os
import shutil
from pathlib import Path
import json
import xmlrpc.client

from fmt_md import MarkdownFormatter, format_anything
from db_mgr import DocumentsMgr

try:
    from utils.log import getLogger
except ImportError:
    from logging import getLogger
logger = getLogger()

TESTING = False
if TESTING:
    print("\n" + "#"*49)
    print("注意：当前为模拟上传环境")
    print("#"*49 + "\n")


class PostidNotUnique(Exception):
    """ 获取到postid不唯一，可能是存在同名title的文档 """

class CnblogManager:
    def __init__(self, path_cnblog_account):
        self.dict_conf = {
            # "blog_url": "",
            # "blog_id" : "",
            # "app_key" : "",
            # "user_id" : "",
            # "username": "",
            # "password": "",
            # "repo_dir": ""
        }
        self.load_cnblog_conf(path_cnblog_account)
        self.cnblog_server = xmlrpc.client.ServerProxy(self.dict_conf["blog_url"])
        self.mime = None

        self.md_fmt = MarkdownFormatter()
        self.md_fmt.set_ignore_websites(["cnblogs.com/blog/" +
                                        str(self.dict_conf["user_id"])])

        repo_dir = self.dict_conf["repo_dir"]
        assert os.path.isabs(repo_dir), "[repo_dir]必须为绝对路径"
        assert repo_dir, "请先为配置文件指定操作的repo目录..."
        self.db_mgr = DocumentsMgr(repo_dir)

    def load_cnblog_conf(self, path_conf):
        with open(path_conf, "r") as fp:
            dict_conf = json.load(fp)
        for key, value in dict_conf.items():
            self.dict_conf[key] = value

    # def load_repo_conf(self, path_conf):

    def get_postid(self, title_or_postid):
        if title_or_postid.isdecimal():
            postid = title_or_postid
        else:
            postid = self.db_mgr.get_postid(title_or_postid)
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

    def pull_img(self, path_md):
        self.md_fmt.load_file(path_md)

        if self.md_fmt.get_images("http"):
            self.md_fmt.download_img()

    def _upload_img(self, path_img):
        if TESTING:
            return "https://img2020.cnblogs.com/blog/2039866/202005/2039866-20200525195318772-1131646535.jpg"

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

    def _new_blog(self, struct_post):
        if TESTING:  # 模拟博客上传
            postid = "12960953"
        else:
            postid = self.cnblog_server.metaWeblog.newPost(
                        self.dict_conf["blog_id"],
                        self.dict_conf["username"],
                        self.dict_conf["password"],
                        struct_post, True)
        print(f">> 完成blog的上传:【{postid}】")
        self.db_mgr.add_doc(self.md_fmt, str(postid))

    def _repost_blog(self, postid, struct_post):
        """ 重新发布 """
        if TESTING:  # 模拟博客上传
            status = True
        else:
            status = self.cnblog_server.metaWeblog.editPost(
                        postid,
                        self.dict_conf["username"],
                        self.dict_conf["password"],
                        struct_post, True)
        print(f">> 完成blog的更新:【{status}】")
        self.db_mgr.modify_doc(self.md_fmt)

    def _is_article(self, path_md):
        abspath_article = os.path.join(self.db_mgr.repo_dir, self.db_mgr.data["dir_article"])
        return path_md.find(abspath_article) >= 0

    def _update_categories(self, path_md):
        assert os.path.isabs(path_md)
        assert path_md.find(os.path.abspath(self.db_mgr.repo_dir)) == 0

        essay_dirname = self.db_mgr.data["dir_essay"]
        article_dirname = self.db_mgr.data["dir_article"]

        # 通过相对路径
        def get_categories(key_dirname):
            # path_dir = Path(os.path.dirname(path_md)).as_posix()
            path_parts = Path(os.path.dirname(path_md)).parts  # tuple
            assert key_dirname in path_parts, f"Error: {key_dirname} not in {path_parts}"
            index = path_parts.index(key_dirname)
            return list(path_parts[index +1:])

        categories = get_categories(article_dirname if self._is_article(path_md) else essay_dirname)
        if self.md_fmt.metadata["categories"] != categories:
            self.md_fmt.metadata["categories"] = categories
            self.md_fmt.update_meta()
            return True
        else:
            return False  # 无需更新

    def _rebuild_images(self, path_md):
        dir_img = path_md[:-3]  # 同名文件夹
        has_dir = os.path.exists(dir_img)

        md_parser = self.md_fmt

        # 上传图片
        dict_images_relpath = md_parser.get_images("local", force_abspath=False)
        if not has_dir:
            assert not dict_images_relpath, f"Markdown文档引用的图像未存储在同名文件夹下: {dict_images_relpath}"
            return False

        list_dir = os.listdir(dir_img)
        if not dict_images_relpath:
            md_parser.unlock_text()
            logger.warning(f"Markdown文档并未引用图像，同名dir内容如下: {list_dir}")
            if input("是否清除同名文件夹？ [Y/n]: ").lower() != "n":
                shutil.rmtree(dir_img)
                logger.warning(f"已清除未引用文件夹:【{dir_img}】")
            return False

        # 删除未被引用的（多余）图像
        set_redundant = set(list_dir) - {os.path.basename(i) for i in dict_images_relpath.values()}
        str_redundant = '\n'.join(set_redundant)
        if set_redundant and input(f"""################ 是否删除多余图片文件：
{str_redundant}
################ [Y/n]:""").lower() != "n":
            for file in set_redundant:
                os.remove(file)

        # 将图像链接地址改写为cnblog_link
        dict_images = {}
        # if dict_images_relpath:
        for line_idx, rel_path in dict_images_relpath.items():
            dict_images[line_idx] = os.path.join(os.path.dirname(path_md), rel_path)
        md_parser.process_images(dict_images, self._upload_img)

        # 备注原本地图像链接
        text_lines = md_parser.get_text()
        # if dict_images_relpath:
        for line, url_local in dict_images_relpath.items():
            # path_rel = os.path.relpath(url_local, md_parser.file_name)
            md_parser.modify_text(line, f"{text_lines[line].rstrip()} <!-- {url_local} -->")
        return True

    def post_blog(self, path_md):
        md_parser = self.md_fmt

        if self.mime is None:
            self._load_mime()

        # md_parser读取文档，并初步格式化
        format_anything(md_parser, path_md)

        # 图片的处理
        images_updated = self._rebuild_images(path_md)
        # 更新category
        category_updated = self._update_categories(path_md)
        if images_updated or category_updated:
            # 保存修改url的Markdown
            md_parser.overwrite()

        if self._is_article(path_md):
            md_parser.metadata["categories"] = ["[文章分类]"+c for c in md_parser.metadata["categories"]]
        struct_post = {
            "title": md_parser.metadata["title"],
            "categories": ["[Markdown]"] + md_parser.metadata["categories"],
            "description": "".join(md_parser.get_text())
        }
        postid = self.get_postid(md_parser.metadata["title"])
        if postid:
            self._repost_blog(postid, struct_post)
        else:
            self._new_blog(struct_post)

    def download_blog(self, title_or_postid, ignore_img=True):
        if not ignore_img:
            raise Exception("尚未开发，敬请期待")

        postid = self.get_postid(title_or_postid)
        if not postid:
            logger.error(f"本地数据库未存储blog: 【{title_or_postid}】，\
但不确定博客园服务器状态。如有必要，请指定postid值，重新查询。")
            return

        dict_data = self.cnblog_server.metaWeblog.getPost(
                    postid,
                    self.dict_conf["username"],
                    self.dict_conf["password"])

        dir_download = "cnblog_bak"
        if not os.path.exists(dir_download): os.makedirs(dir_download)
        path_save = f"{dir_download}/{postid}.md"
        with open(path_save, "w", encoding="utf8") as fp:
            fp.write(dict_data['description'])
        print(f">> 已下载blog:【{path_save}】")

    def delete_blog(self, title_or_postid):
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
            print(f">> 已删除blog:【{title_or_postid}】")

            path_rel = self.db_mgr.data["postids"]["postid"]
            self.db_mgr.remove_doc(path_rel)

    def rename_blog(self, title_or_postid, path_new_md):
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
