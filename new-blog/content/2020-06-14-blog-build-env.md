Title: 博客构建环境准备
Date: 2020-06-14
Author: xiayf
Slug: blog-build-env

好记性不如烂笔头。

1、Python 虚拟环境

```bash
virtualenv -p python3 ~/.py3
source ~/.py3/bin/activate
```

2、安装 Python 依赖包

```bash
pip install pelican[Markdown]   # 可能需要先安装 pip：easy_install pip
```

3、安装主题包

```bash
git clone https://github.com/youngsterxyf/my-pelican-themes.git ~/github/youngsterxyf/my-pelican-themes
pelican-themes -i ~/github/youngsterxyf/my-pelican-themes/my-gum
```

4、构建

```bash
make html
```

---

另，更新艺术字体或字集：

(1) 下载 fontmin-app：https://github.com/ecomfe/fontmin-app

(2) 导入字体 SentyZHAO（汉仪新蒂赵孟頫体）：https://github.com/youngsterxyf/blog-content/blob/master/new-blog/SentyZHAO.ttf

![fontmin](https://i.loli.net/2020/06/14/Xn8b9kZDIfWoLmp.png)

(3) 生成字体样式，并拷贝更新到目标主题包目录中：https://github.com/youngsterxyf/my-pelican-themes/tree/master/my-gum/static

(4) 更新主题包：

```bash
pelican-themes -r my-gum
pelican-themes -i ~/github/youngsterxyf/my-pelican-themes
```

(5) 重新构建生成博客