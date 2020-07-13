#!/usr/bin/env python3
# @Date    : 2020-07-12
# @Author  : Bright Li (brt2@qq.com)
# @Link    : https://gitee.com/brt2

import os
import json
from random import randint

import requests
# from terminaltables import SingleTable

class FileExists(Exception):
    """ 文件名重复 """

class UploadError(Exception):
    """ 图像上传失败 """

def format_filename(path_file):
    if not os.path.exists(path_file):
        return path_file

    path_, ext = os.path.splitext(path_file)
    filename_base = path_.rsplit("_", 1)
    # 重命名：filename_base + random
    while True:
        suffix = randint(0, 9999)
        path_file = f"{filename_base}_{suffix}{ext}"
        if not os.path.exists(path_file):
            return path_file

class CMMS_v2:
    endpoint = "https://sm.ms/api/v2/upload/"
    profile_endpoint = "https://sm.ms/api/v2/profile/"
    upload_history_endpoint = "https://sm.ms/api/v2/upload_history/"

    default_conf = ".database.json"

    def __init__(self, repo_dir, api_token=None):
        self.api_token = api_token
        self.path_db = os.path.join(repo_dir, self.default_conf)
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.path_db):
            self.data = {}
            return
        with open(self.path_db, "r") as fp:
            self.data = json.load(fp)

    def save_data(self):
        with open(self.path_db, "w+", encoding="utf8") as fp:
            json.dump(self.data, fp, ensure_ascii=False, indent=2)

    def upload(self, path_file):
        filename = os.path.basename(path_file)
        if filename in self.data:
            raise FileExists(path_file)
        with open(path_file, 'rb') as fp:
            multipart_form_data = {
                'smfile': (filename, fp)
            }

            headers = {'Authorization': self.api_token} if self.api_token else None
            r = requests.post(self.endpoint, files=multipart_form_data, headers=headers)

            json_content = json.loads(r.text)
            if not json_content['success']:
                print(json_content)
                raise UploadError()

            print(f"[+] 完成上传: {path_file}")
            self.data[filename] = [
                json_content["data"]["url"],
                json_content["data"]["delete"]
            ]

    def get_profile(self):
        """ return user info """
        assert self.api_token, "未提供用户API_TOKEN信息"
        headers = {
            'Authorization': self.api_token
        }
        r = requests.post(self.profile_endpoint, headers=headers)
        json_content = json.loads(r.text)
        return self.draw_profile_table(json_content)

    def draw_profile_table(self, json_response):
        """ Visualize the user history JSON response by SM.MS. """
        _j = json_response
        data = [
            ['username', _j['data']['username']],
            ['Role', _j['data']['role']],
            ['Group Expire Time', _j['data']['group_expire']],
            ['Disk Usage', _j['data']['disk_usage']],
            ['Disk Limit', _j['data']['disk_limit']],
        ]
        table_instance = SingleTable(data, 'SM.MS User Profile')
        table_instance.inner_row_border = True
        return table_instance.table

    def get_upload_history(self):
        """
        Get user upload history.
        """
        headers = {
            'Authorization': self.api_token
        }
        r = requests.get(self.upload_history_endpoint, headers=headers)
        json_content = json.loads(r.text)
        return self.draw_user_history_table(json_content)

    def draw_user_history_table(self, json_response):
        """
        Visualize the user history JSON response by SM.MS.
        """
        _j = json_response
        data = []
        title_line = ['Image URL','Delete URL']
        data.append(title_line)
        for item in _j['data']:
            picture_item = []
            picture_item.append(item['url'])
            picture_item.append(item['delete'])
            data.append(picture_item)
        table_instance = SingleTable(data, 'SM.MS User History')
        table_instance.inner_row_border = True
        return table_instance.table

    def draw_upload_status_table(self, json_response):
        """
        Visualize the upload JSON response by SM.MS.
        Example:
        {'success': True,
        'code': 'success',
        'message': 'Upload success.',
        'data': {'file_id': 0,
                'width': 1350,
                'height': 449,
                'filename': 'ccc.jpg',
                'storename': 'hHt4IcpxNXo5TdS.jpg',
                'size': 141115,
                'path': '/2019/08/03/hHt4IcpxNXo5TdS.jpg',
                'hash': 'u3dpSRFMslx7PAZNGTCQjYL4r6',
                'url': 'https://i.loli.net/2019/08/03/hHt4IcpxNXo5TdS.jpg',
                'delete': 'https://sm.ms/delete/u3dpSRFMslx7PAZNGTCQjYL4r6',
                'page': 'https://sm.ms/image/hHt4IcpxNXo5TdS'},
        'RequestId': 'FD6277E3-F2AB-4762-A575-21A7600D5BEA'}
        """
        _j = json_response
        data = [
            ['Image URL', _j['data']['url']],
            ['Deletion URL', _j['data']['delete']],
        ]
        table_instance = SingleTable(data, 'SM.MS Upload Status')
        table_instance.inner_row_border = True
        return table_instance.table

def getopt():
    import argparse

    parser = argparse.ArgumentParser("upload_cnblog", description="")
    parser.add_argument("-f", "--folder", action="store_true", help="将文件夹内的图像重命名")
    return parser.parse_args()

# from call_git import run_cmd
def move_folder_files(repo_dir):
    import glob
    import shutil
    # cwd = os.path.abspath(os.curdir)
    os.chdir(repo_dir)

    for path_file in glob.glob("**/*"):
        path_dst = path_file.replace('/', '-')
        # input(f">> 是否将 {path_file} -> {path_dst}")
        shutil.move(path_file, path_dst)

def upload_smms(repo_dir, cmms_token):
    from call_git import GitRepo

    git = GitRepo(repo_dir)
    if git.is_status_mixed():
        print("当前Stage暂存区有文件未更新至最新状态，无法判定用户明确的上传意图，请更新Repo仓库Git状态")
        return

    list_files = git.status("untracked")
    # 检查文件格式
    for file in list_files:
        assert os.path.splitext(file)[1] in [".jpg", ".png", ".gif"], f"不符合图床格式的文件【{file}】"

    # 上传
    smms_client = CMMS_v2(repo_dir, cmms_token)

    def uploading():
        all_Right = True
        list_uploaded = []
        list_untracked = git.status("untracked")
        assert list_untracked, "不存在需要上传的文件"
        for path_file in list_untracked:
            try:
                smms_client.upload(os.path.abspath(path_file))
            except FileExists:
                all_Right = False
                path_new = format_filename(path_file)
                os.rename(path_file, path_new)
            except UploadError:
                print(f"[-] 文件上传失败【{path_file}】")
                # all_Right = False
            else:
                list_uploaded.append(path_file)

        if list_uploaded:
            git.add(list_uploaded)
        return all_Right

    while not uploading():
        pass
    smms_client.save_data()
    git.add(smms_client.path_db)
    git.commit(message=None)


if __name__ == "__main__":
    path_smms_conf = ".smms.json"

    with open(path_smms_conf, "r") as fp:
        dict_conf = json.load(fp)
        repo_dir = dict_conf["repo_dir"]
        cmms_token = dict_conf.get("smms_token")

    args = getopt()
    if args.folder:
        move_folder_files(repo_dir)
    else:
        upload_smms(repo_dir, cmms_token)
