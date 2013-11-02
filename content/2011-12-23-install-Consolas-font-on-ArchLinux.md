Title: ArchLinux上安装Consolas字体
Date: 2011-12-23
Author: youngsterxyf
Slug: install-Consolas-font-on-ArchLinux
Tags: Linux, 字体

1. 从[http://www.iplaysoft.com/consolas.html](http://www.iplaysoft.com/consolas.html)下载Consolas字体。

2. 然后

		:::bash
    	sudo mkdir -p /usr/share/fonts/yahei
    	sudo cp YaHei.Consolas.1.11b.ttf /usr/share/fonts/yahei/

3. 改变权限：
		
		:::bash
		sudo chmod 644 /usr/share/fonts/yahei/YaHei.Consolas.1.11b.ttf

4. 安装：

		:::bash
    	cd /usr/share/fonts/yahei/
    	sudo mkfontscale
    	sudo mkfontdir
    	sudo fc-cache -fv
