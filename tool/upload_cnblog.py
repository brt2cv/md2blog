#!/usr/bin/env python
# @Date    : 2020-05-25
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2
# @Version : 0.1.2


def getopt():
    import argparse

    parser = argparse.ArgumentParser("upload_cnblog", description="")
    parser.add_argument("-r", "--repo", action="store", help="初始化仓库路径")
    parser.add_argument("-u", "--user", action="store_true", help="获取用户博客信息")
    parser.add_argument("-g", "--get", action="store_true", help="获取近期上传的列表")
    parser.add_argument("-d", "--delete", action="store", help="删除博客文档")
    parser.add_argument("-s", "--save", action="store", help="下载博客文档")
    return parser.parse_args()


if __name__ == "__main__":
    args = getopt()
    path_cnblog_account=".cnblog.json"

    # 处理命令行参数
    if args.repo:
        import os.path
        import json
        from db_mgr import DocumentsMgr

        path_db = os.path.realpath(args.repo)
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
                "username": your_name,
                "password": password,
                "repo_dir": path_db
            }
        with open(path_cnblog_account, "w", encoding="utf8") as fp:
            # fp.seek(0)
            # fp.truncate()
            json.dump(dict_conf, fp)
        exit()

    from cnblog_mgr import CnblogManager
    uploader = CnblogManager(path_cnblog_account)
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
            except FileNotFoundError as e:
                print(e)

            path = input("继续输入path，按[Q]退出: ")
            if path.lower() == "q":
                break
