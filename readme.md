
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

## 流程

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

## 规范

+ 目录

    应该按照一定的分类标准，对所有的文档进行放置。

+ 文件命名

    使用 n-string 方式命名。其中n代表权重（1-9），直接影响文档在mkdocs的排序。由于文件名的限制，string无法等同于文档title。

+ 标签

    通过hugo_info记录标签，并跟踪至~~数据库~~json中（由于db不支持git跟踪，改为json）。

+ git管理

    可以直接使用git来指示upload_cnblog.py对文档的上传管理：

    1. 对于需要上传或更新的文档，使用 `git add` 添加到repo中
    2. 执行 `python3 upload_cnblog.py -a` 自动查询当前repo的变化
    3. upload_cnblog格式化Markdown文件，上传至cnblog，并改写本地数据库表
    4. 自动更新当前repo——由于added文档格式化，需要重新add。同理图像目录也需要重新添加仓库，以及 `.database.json` 数据库
    5. 实现对 `git commit` 的提交

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

## Todo List

- [x] 实现对多余图像的挑选和删除
- [ ] 对于分辨率过高的图像进行resize操作
- [ ] 实现git_rename、git_move操作
- [ ] git仓库的database.json使用中文来记录path
- [x] 已上传图像的link需要再次验证上传
- [ ] 实现从cnblog获取database，更新本地json数据库
- [x] 添加对mime文件对.webp图像的支持

## Buglist

+ 通过上传md时，在post_struct["categories"]增加"[文章分类]"，无法解决上传作为“文章”类型的问题。暂时没有方式可以实现该需求。
+ 目前cnblog不支持webp的动图格式，但测试webp比gif压缩率更高；所以建议手动转换webp -> gif，上传cnblog后，源文档 `<!-- 注释 xxx.webp -->` 保留并git存储webp原图和gif转换图。
+ H2超过10之后，会发成显示重复（例如：11. 11. title）。但本地文件却并没有问题，只是cnblog中的md内容发生重复。目前不确定该差别是否为cnblog平台问题（毕竟程序对1-9都显示正常)

## 寻求帮助

欢迎各界高手施以援手，答疑解惑~

- [ ] 如何将内容直接发布到“文章”中？
- [ ] 如何在post上传时，添加tag标签？
- [ ] 如何使用博客园API，实现对博客园“收藏”等内容的管理？
