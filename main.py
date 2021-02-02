#!/usr/bin/env python
# @Date    : 2020-07-30
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.6

import os.path
import shutil
from collections import OrderedDict


def getopt():
    import argparse

    parser = argparse.ArgumentParser("upload_cnblog", description="")
    parser.add_argument("-r", "--repo", action="store", help="初始化仓库路径")
    parser.add_argument("-c", "--check", action="store_true", help="校正本地数据库")
    parser.add_argument("-u", "--user", action="store_true", help="获取用户博客信息")
    parser.add_argument("-g", "--get", action="store_true", help="获取近期上传的列表")
    parser.add_argument("-d", "--html2md", action="store_true", help="爬取html为markdown")
    parser.add_argument("-D", "--delete", action="store", help="删除博客文档（参数为postid或待删除的path）")
    parser.add_argument("-s", "--resize", action="store_true", help="缩放图像")
    parser.add_argument("-S", "--save", action="store", help="下载博客文档")
    parser.add_argument("-p", "--pull_img", action="store_true", help="下载博客中链接的http图像")
    parser.add_argument("-m", "--move", action="store_true", help="使用git记录文件路径变动，并更新至数据库（无需网络操作）")
    parser.add_argument("-a", "--auto", action="store_true", help="使用git自动上传cnblog")
    return parser.parse_args()

def path_str2list(path_str):
    path = path_str.strip()
    for q in ["\"", "\'"]:
        multi_files_gap = "{0} {0}".format(q)
        if path.find(multi_files_gap) >= 0:
            list_args = path.split(multi_files_gap)
            # break
            return [path.strip(q) for path in list_args]

    return [path.strip("\"").strip("\'")]

def init_repo(path_dir, path_cnblog_account):
    import json
    from db_mgr import DocumentsMgr

    path_db = os.path.realpath(path_dir)
    assert not os.path.exists(os.path.join(
            path_db, DocumentsMgr.default_conf)), "已存在数据库文件，不支持覆盖重写"
    DocumentsMgr.template_data(path_db)

    # 记录cnblog操作目录
    if os.path.exists(path_cnblog_account):
        with open(path_cnblog_account, "r") as fp:
            dict_conf = json.load(fp)
    else:
        account_ = input("请输入博客园 账户名@密码 [e.g. brt2@123456]: ")
        your_name, password = account_.split("@")
        dict_conf = {
            "blog_url": f"https://rpc.cnblogs.com/metaweblog/{your_name}",
            "blog_id" : "anything",
            "app_key" : your_name,
            "user_id" : "",
            "username": your_name,
            "password": password,
            "repo_dir": path_db
        }
    with open(path_cnblog_account, "w", encoding="utf8") as fp:
        # fp.seek(0)
        # fp.truncate()
        json.dump(dict_conf, fp, indent=2)

def upload_cnblog(uploader):
    import os
    # from handle_git import git_status
    from util.gitsh import GitRepo

    repo_dir = uploader.get_repodir()
    git = GitRepo(repo_dir)
    if git.is_status_mixed():
        print("当前Stage暂存区有文件未更新至最新状态，无法判定用户明确的上传意图，请更新Repo仓库Git状态")
        return

    repo_files_to_update = [uploader.db_mgr.get_database(), ]

    map_actions = OrderedDict([
        ("modified_added"  , uploader.post_blog),
        ("deleted_added"   , uploader.delete_blog),
        ("new_added"       , uploader.post_blog),
        ("rename_added"    , uploader.move_blog)
    ])

    def execute_upload(action):
        list_files = git.status(action)

        for path_file in list_files:
            isRename = action.startswith("rename")
            if isRename:
                path_file, path_to = path_file.split(" -> ")

            if not path_file.endswith(".md"):
                continue
            abspath_file = os.path.join(repo_dir, path_file)
            if isRename:
                abspath_to = os.path.join(repo_dir, path_to)
                map_actions[action](abspath_file, abspath_to)
            else:
                map_actions[action](abspath_file)

            # 将文件更新到记录列表
            dir_res = abspath_file[:-3]  # 去除.md后缀
            if action == "deleted_added":
                if os.path.exists(dir_res):
                    os.rmdir(dir_res)
                    repo_files_to_update.append(dir_res)
            elif action == "rename_added":
                if os.path.exists(dir_res):
                    dir_to = abspath_to[:-3]
                    shutil.move(dir_res, dir_to)
                    repo_files_to_update.extend([dir_res, dir_to])
            else:
                repo_files_to_update.append(abspath_file)
                if os.path.exists(dir_res):
                    repo_files_to_update.append(dir_res)

    for action in map_actions:
        execute_upload(action)

    # 更新repo的状态
    git.add(repo_files_to_update)

    # git commit, 若无需提交，则Ctrl+C终止程序即可
    commit_message = input("Input commit message [回车默认提交]: ")
    git.commit(commit_message)

# Html2MarkdownEngine = html2md.HTML2Text()
def html2markdown(url, save_dir):
    j = urllib.urlopen(url)
    data_body = j.read()
    data_utf8 = data_body.decode("utf-8")

    html_parser = html2md.HTML2Text()
    md = html_parser.handle(data_utf8)
    assert md, "解析错误，未转换成Markdown格式文本"

    title = data_utf8.split('<title')[1].split(">", 1)[1].split('</title>')[0]
    path_save = os.path.join(save_dir, title + ".md")
    with open(path_save, "w", encoding="utf8") as fp:
        fp.write(md)
    print(f"[+] 已存储Markdown至【{path_save}】")

def resize_imgs(path, ratio_default, min_size_default, max_shape_default):
    from util.imgfmt import resize
    from glob import glob

    ratio = input(f"图像缩放比例 [默认{ratio_default}]: ")
    ratio = float(ratio) if ratio else ratio_default

    if os.path.isdir(path):
        str_size = input(f"忽略的最小文件size [默认为 {min_size_default} KB]: ")
        if not str_size:
            str_size = min_size_default
        min_size = int(1024*float(str_size))

        max_shape = input("是否限定允许的最大像素 [Y/n]：")
        if max_shape.lower() == "n":
            max_shape = None
        else:
            _int = input(f"请输入最大允许像素，默认{max_shape_default}（e.g. 670 or 800,600): ")
            if not _int:
                max_shape = [max_shape_default] * 2
            else:
                max_shape = [int(i) for i in _int.split(",")]
                if len(max_shape) == 1:
                    max_shape = max_shape * 2

        list_png = glob(path + "/*.png")
        list_jpg = glob(path + "/*.jpg")
        for path_img in list_jpg + list_png:
            resize(path_img, ratio, min_size=min_size, max_shape=max_shape)
    else:
        resize(path, ratio, min_size=0, max_shape=None)

def movefile_db_update(uploader):
    ok = input("请确认您未修改移动文件的内容，否则可能造成损失 [Y/n]:")  # 要不R识别为D&A，要么commit后，不再触发修改的上传操作
    if ok.lower() == "n":
        return

    from util.gitsh import GitRepo

    repo_dir = uploader.get_repodir()
    git = GitRepo(repo_dir)
    if git.is_status_mixed():
        print("当前Stage暂存区有文件未更新至最新状态，无法判定用户明确的上传意图，请更新Repo仓库Git状态")
        return

    list_move = git.status("renamed")
    for couple in list_move:
        path_old, path_new = couple
        if path_new[-3:] != ".md":
            continue
        try:
            uploader.db_mgr.move_doc(path_old, path_new)
            print(f"[+] 已完成数据库更新: {path_old} -> {path_new}")
        except Exception as e:
            print(f"[-] 未能成功移动元数据: {path_old}\n", e)
            # assert False

def check_db_from_cnblog(uploader):
    """ 网络、本地、数据库同步检测:
        + 存在性(postid, title)
        + 标签(tags): 需要通过网络爬虫实现
    """
    from pprint import pprint
    from db_mgr import DocumentsMgr

    results = {
        "blog": set(),  # 多出项, tuple(postid, title)
        "db"  : set(),
        "repo": set(),  # 缺失项
    }

    # 数据库
    repo_dir = uploader.get_repodir()
    doc_mgr = DocumentsMgr(repo_dir)
    db_postids = doc_mgr.data["postids"]
    # db_titles = doc_mgr.data["titles"]

    # 本地文件set集合
    repo_files = doc_mgr.walk_repo(["_index.md"])  # \\ or / ??

    # 网络cnblog博客数据
    list_posted = uploader.get_recent_post()
    for dict_post in list_posted:
        web_title  = dict_post['title']
        web_postid = dict_post['postid']
        # 数据库的存在性
        if web_postid not in db_postids:
            results["blog"].add((web_postid, web_title))
            continue

        # 本地文件的存在性
        path_local = db_postids[web_postid]
        if path_local not in repo_files:
            results["repo"].add(path_local)
        else:
            repo_files.remove(path_local)
        del db_postids[web_postid]

    def report(msg, repo_diff):
        if repo_diff:
            print(msg)
            pprint(repo_diff)

    report("web_cnblog多出了以下文章:", results["blog"])
    report("本地文件缺失了数据库记录文档:", results["repo"])
    db_remains = set(db_postids.values())
    report("web_cnblog缺失了以下记录:", db_remains & repo_files)
    report("数据库未记录的本地文档:", repo_files - db_remains)
    report("数据库记录了的无效文档:", db_remains - repo_files)


if __name__ == "__main__":
    args = getopt()
    path_cnblog_account = ".cnblog.json"

    # 处理命令行参数
    if args.repo:
        init_repo(args.repo, path_cnblog_account)
        exit()

    from cnblog_mgr import CnblogManager
    uploader = CnblogManager(path_cnblog_account)
    if args.auto:
        upload_cnblog(uploader)
    elif args.user:
        info = uploader.get_user_info()
        print(info)
    elif args.check:
        check_db_from_cnblog(uploader)
    elif args.get:
        uploader.get_recent_post()
    elif args.delete:
        uploader.delete_blog(args.delete)
    elif args.save:
        uploader.download_blog(args.save)
    elif args.move:
        movefile_db_update(uploader)
    else:
        path = input("请输入待处理文件path(支持直接拖拽): ")
        if args.html2md:
            import urllib.request as urllib
            from util import html2md

            tmp_dir = os.path.join(uploader.get_repodir(), "download")
            if not os.path.exists(tmp_dir):
                os.mkdir(tmp_dir)
        elif args.resize:
            ratio = input("请输入默认的缩放比例【默认0.6】: ")
            if not ratio:
                ratio = "0.6"
            elif ratio[0] == ".":
                ratio = "0" + ratio
            ratio = float(ratio)

        while True:
            for path in path_str2list(path):
                try:
                    if args.pull_img:
                        uploader.pull_img(path)
                        uploader.md_fmt.convert_png2jpg()
                        uploader.md_fmt.overwrite()
                    elif args.html2md:
                        html2markdown(path, tmp_dir)
                    elif args.resize:
                        resize_imgs(path,
                                    ratio_default=ratio,
                                    min_size_default=10,
                                    max_shape_default=670)
                    else:
                        uploader.post_blog(path)
                except FileNotFoundError as e:
                    print(e)

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
