
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
        + 检测权重，并重命名
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

    通过hugo_info记录标签，并跟踪至数据库中。

+ git管理

    当增加提交时，通过git-api检测修改的文档，对更新文档重新检测format和规范属性。

