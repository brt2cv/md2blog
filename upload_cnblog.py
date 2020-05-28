#!/usr/bin/env python
# @Date    : 2020-05-27
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.4

import os.path


def getopt():
    import argparse

    parser = argparse.ArgumentParser("upload_cnblog", description="")
    parser.add_argument("-r", "--repo", action="store", help="初始化仓库路径")
    parser.add_argument("-u", "--user", action="store_true", help="获取用户博客信息")
    parser.add_argument("-g", "--get", action="store_true", help="获取近期上传的列表")
    parser.add_argument("-d", "--delete", action="store", help="删除博客文档")
    parser.add_argument("-s", "--save", action="store", help="下载博客文档")
    parser.add_argument("-S", "--resize", action="store_true", help="缩放图像")
    parser.add_argument("-p", "--pull_img", action="store_true", help="下载博客中链接的http图像")
    parser.add_argument("-a", "--auto", action="store_true", help="使用git自动上传cnblog")
    return parser.parse_args()

def init_repo(path_dir):
    import json
    from db_mgr import DocumentsMgr

    path_db = os.path.realpath(path_dir)
    assert not os.path.exists(os.path.join(
            path_db, DocumentsMgr.default_conf)), f"已存在数据库文件，不支持覆盖重写"
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

def auto_upload(uploader):
    import os
    # from handle_git import git_status
    # from call_git import git_status, git_commit, git_add
    from call_git import GitRepo

    repo_dir = uploader.dict_conf["repo_dir"]
    git = GitRepo(repo_dir)
    repo_files_to_update = [uploader.db_mgr.get_database(), ]

    map_actions = {
        "added"     : uploader.post_blog,
        "modified"  : uploader.post_blog,
        "deleted"   : uploader.delete_blog
    }
    def execute_upload(action):
        list_files = git.status(action)

        for path_file in list_files:
            if not path_file.endswith("md"):
                continue
            abspath_file = os.path.join(repo_dir, path_file)
            map_actions[action](abspath_file)

            # 将文件更新到记录列表
            repo_files_to_update.append(abspath_file)
            dir_res = abspath_file[:-3]  # 去除.md后缀
            if os.path.exists(dir_res):
                repo_files_to_update.append(dir_res)

    for action in map_actions:
        execute_upload(action)

    # 更新repo的状态
    git.add(repo_files_to_update)

    # git commit, 若无需提交，则Ctrl+C终止程序即可
    commit_message = input(f"Input commit message [回车默认提交]: ")
    git.commit(commit_message)


if __name__ == "__main__":
    args = getopt()
    path_cnblog_account = ".cnblog.json"

    # 处理命令行参数
    if args.repo:
        init_repo(args.repo)
        exit()

    from cnblog_mgr import CnblogManager
    uploader = CnblogManager(path_cnblog_account)
    if args.auto:
        auto_upload(uploader)
    elif args.user:
        info = uploader.get_user_info()
        print(info)
    elif args.get:
        uploader.get_recent_post()
    elif args.delete:
        uploader.delete_blog(args.delete)
    elif args.save:
        uploader.download_blog(args.save)
    elif args.resize:
        from png2jpg import resize
        from glob import glob

        path = input("请输入待处理文件path/dir(支持直接拖拽): ")
        path = path.strip().strip('"')
        assert os.path.isabs(path)
        ratio = input("图像缩放比例 [默认0.5]: ")
        ratio = float(ratio) if ratio else 0.5

        min_size = 1024*10
        if os.path.isdir(path):
            list_png = glob(path + "/*.png")
            list_jpg = glob(path + "/*.jpg")
            for path_img in list_jpg + list_png:
                # print(path_img)
                resize(path_img, ratio, min_size=min_size)
        else:
            resize(path, ratio, min_size=min_size)
    else:
        path = input("请输入待处理文件path(支持直接拖拽): ")
        while True:
            path = path.strip().strip('"')
            try:
                if args.pull_img:
                    uploader.pull_img(path)
                    uploader.md_fmt.convert_png2jpg()
                    uploader.md_fmt.overwrite()
                else:
                    uploader.post_blog(path)
            except FileNotFoundError as e:
                print(e)

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
