
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
+ gitbook
    + 支持hugo多皮肤更换
    + 使用git快速部署，无需个人服务器
    - 尚不支持查找功能！
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

## Buglist

+ H2超过10之后，会发成显示重复（例如：11. 11. title）。但本地文件却并没有问题，只是cnblog中的md内容发生重复。目前不确定该差别是否为cnblog平台问题（毕竟程序对1-9都显示正常)
