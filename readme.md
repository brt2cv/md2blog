
# My Notebook in Markdown

## 设计目标

+ 文档存储
    + 可下载link图像，进行本地化存储
    + 压缩内嵌图像，最小化上传
+ 支持随时浏览 & **快速查找**
    + 同步到cnblog!
    + 支持mkdocs的发布
    + 支持hugo编译成静态文件

## 各平台的对比

+ cnblog
    + 支持查找
    + 无需搭建个人服务器
    - 不支持文档排序
+ mkdocs
    + 支持动态修改md和实时渲染
    + 支持主题切换
    - 需要个人服务器（内网限制）
+ gitbook（hugo/hexo）
    + 支持hugo多皮肤更换
    + 使用git快速部署，无需个人服务器
    - 尚不支持查找功能（待确认）
    - 不支持动态更新，编译的过程较复杂

## 流程设计

1. 编写md文档，或使用“简阅”下载markdown
1. 修改文档内容，可以正常在本地浏览器渲染即可
1. 通过封装好的git_push.sh执行上传
    + 利用fmt_md.py格式化文档
        + head元数据
        + 去除H1标题
        + 检测权重，通过权重配置mkdocs的目录结构
    + 选择是否下载link图像（download_img_link.py）
    + 图片压缩（png2jpg_md_img.py）
    + 使用db_mgr.py对文档树进行管理
    + upload_cnblog.py上传到“博客园”
    + git commit & push 当前仓库

## 规范要求

+ 目录

    应该按照一定的分类标准，对所有的文档进行放置。

+ 文件命名

    关于blog的title采用如下策略：

    + 优先使用"description": 一句吸引人眼球的标题，例如：“他写微信软文赚了1173万元，愿意手把手教你文案秘籍——只在这周六”（博客也需要标题党）
    + "title": 如果"description"为空（默认），则使用title作为标题，这个可以“程序化”，简洁明了——“git rebase 使用技巧”
    + 文件名仅用于本地文件记录，与blog的title并不对应。
    + 文件名影响mkdocs的排序：
        * 文件名是mkdocs的默认排序规则
        * mkdocs通过程序，索引文章的weight，并记录于_index.md中

+ 标签

    通过hugo_info记录标签，并跟踪至~~数据库~~json中（由于db不支持git跟踪，改为json）。

+ git管理

    可以直接使用git来指示upload_cnblog.py对文档的上传管理：

    1. 对于需要上传或更新的文档，使用 `git add` 添加到repo中
    2. 执行 `python3 upload_cnblog.py -a` 自动查询当前repo的变化
    3. upload_cnblog格式化Markdown文件，上传至cnblog，并改写本地数据库表
    4. 自动更新当前repo——由于added文档格式化，需要重新add。同理图像目录也需要重新添加仓库，以及 `.database.json` 数据库
    5. 实现对 `git commit` 的提交

+ 简化操作
    * 创建新文件时使用格式模板
    * 上传时自动格式化Markdown文件
    * 自动对Headings排序，生成层级索引——“1.2.4”
    * 图像不会进行重复上传
    * 自动压缩图像，减小空间占用
    * 自动png转jpg
    * 支持过高分辨率的resize压缩
    * 自动实现category的管理
    * 支持label管理
    * 支持文档目录自动生成

## 使用

```sh
# 创建Git-Repo
cd REPO_DIR
git init
...

# 创建配置文件，初始化仓库路径
git clone git@gitee.com:brt2/md2blog.git
cd md2blog
python3 upload_cnblog.py -r REPO_DIR

cp demo/cnblog.json .cnblog.json
# 修改 .cnblog.json 文件，具体配置内容见："配置文件 .cnblog.json 的说明"
vi .cnblog.json

# 编辑markdown
cd REPO_DIR
vi test.md

# 方式1: 手动上传
python3 upload_cnblog
在此拖入md文档，回车上传~

# 方式2: 使用自动上传功能
git add test.md
python3 upload_cnblog.py -a
根据需要，手动push你的Git仓库
```

上传方式推荐2，可以将内容commit提交到git。另，这个方式会自动将文件记录到数据库（json）中，便于修改、移动、删除文档时追踪文件。

### 配置文件 .cnblog.json 的说明

* blog_url: "https://rpc.cnblogs.com/metaweblog/brt2"
* blog_id: "anything"  # cnblog并不验证此项目，尽管你能够获得你的ID
* app_key: "brt2",
* user_id: "2039866",  # 此项用于下载图像链接时，忽略自己博客的图像地址
* username: "brt2",
* password: "this is a secret",
* repo_dir: "D:\\Home\\workspace\\note"  # 指向你的Git-Repo

关于 `user_id` ，特别说明下：并没有明确的接口可以获取到该ID，它不同于blog_id。本人获取这个的方法是，上传一张图像后，查询其生成的URL地址，从中提取，例如： https://img2020.cnblogs.com/blog/2039866/202006/2039866-20200602142016960-1926272797.jpg 中可以提取到我的user_id: 2039866

## Markdown编辑工具推荐

基于vscode

* Markdown Shortcuts: 支持各种md格式化，最牛的就是自动生成表格的功能
* Markdown TOC
* Markdown AutoTOC
* markdown-helper
* Paste Image
* Markdown Preview Enhanced（其实vscode默认md预览就很棒了）
* Open In Default Browser（这个就很鸡肋了，还不如vscode自带预览功能）

基于sublime

* Markdown Editing
* Markdown Preview: 只能在浏览器中预览
* imagepaste: 这个强烈推荐，可以直接粘贴剪切板图片，并存储在同名目录下。
    - 标准的插件，有个瑕疵： 只能存储为png图像，图像体积较大
    - 推荐个人修改版本（其实改动很简单），默认存储jpg格式: https://gitee.com/brt2/subl-imgpaste.git
* SublimeTmpl: 用于生成各类文件的模板，包括Markdown
* 还有sublime自定义快捷键的功能，可以快速实现对H2/H3...等常见结构的格式化

基于Simpread（简阅）

* 安利一下这款国人开源工具，工具后台已经对上百个常见网站做了适配，可以直接将html页面转码Markdown下载。
* 当然，下载的格式毕竟还是有必要人工修整一下的，但已经节约了90%的时间了，知足吧
* 本工具会自动再上传时标记【转载】字样，同时建议用户保留 `本文由 简悦 SimpRead 转码， 原文地址...` 的内容。

## 关于Markdown的格式（模板）

```
<!--
+++
title       = "This is title to show!"
description = ""
date        = "2020-06-01"
weight      = 5
tags        = ["我的标签"]
categories  = ["我的分类", "我的另一个分类"]
keywords    = []
+++ -->

[TOC]

## This is a heading

Body text...

* item_0
* item_1
    - item_1_1
    - item_1_2
* item_3

## This is another heading

Body text...

```

## Todo List

- [x] 实现对多余图像的挑选和删除
- [x] 对于分辨率过高的图像进行resize操作
- [x] 实现git_rename、git_move操作
- [x] 已上传图像的link需要再次验证上传
- [x] 实现从cnblog获取database，更新本地json数据库
- [x] 通过url下载html并转换为MarkDown格式

## Buglist

+ 通过上传md时，在post_struct["categories"]增加"[文章分类]"，无法解决上传作为“文章”类型的问题。暂时没有方式可以实现该需求。
+ 目前cnblog不支持webp的动图格式，但测试webp比gif压缩率更高；所以建议手动转换webp -> gif，上传cnblog后，源文档 `<!-- 注释 xxx.webp -->` 保留并git存储webp原图和gif转换图。
+ html2text使用空格缩进来处理 `<code>` ，容易实现但无法体现代码语言类型，需要改成反引号的格式。

## 寻求帮助

欢迎各界高手施以援手，答疑解惑~

- [ ] 如何将内容直接发布到“文章”中？
- [ ] 如何在post上传时，添加tag标签？
- [ ] 如何使用博客园API，实现对博客园“收藏”等内容的管理？
