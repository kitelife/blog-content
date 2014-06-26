Title: 技术问题一问一答
Date: 2014-06-26
Author: youngsterxyf
Slug: recently-technology-tips
Tags: 笔记

- 如何方便地删除某目录下所有空文件？

`find . -size 0 -exec rm {} \;` 或 `find . -size 0 | xargs rm -f`

find默认会递归遍历所有子目录，如果想只在当前目录查找，可以添加参数`-prune`。

------

- 如何查看某进程打开了哪些文件？

先通过`ps aux | grep [进程名]`找到该进程的进程好，然后`ls -la /proc/[进程号]/fd`，输出不仅包含打开的普通文件。

另一种不太直观的方法是使用lsof，`lsof -c [进程名]`，但这个命令的输出包含进程打开的各种类型的文件，可以简单过滤一下`lsof -c [进程名] | grep REG`。

------

- 如何重启php-fpm？

php5.3.3以上版本的php-fpm不再支持php-fpm以前具有的`php-fpm (start|stop|reload)`等命令，需要使用信号控制：
master进程可以理解以下信号：
  - INT, TERM 立刻终止
  - QUIT 平滑终止
  - USR1 重新打开日志文件
  - USR2 平滑重载所有worker进程并重新载入配置和二进制模块

那么应该这样重启php-fpm：

`kill -USR2 php-fpm.pid` 或 先`ps aux | grep php-fpm`找到php-fpm主进程的进程号，然后`kill -USR2 [进程号]`。

------

- 对于Nginx、php-fpm等的日志文件使用shell脚本进行切分备份时，发现Nginx、php-fpm还是往备份的老文件中，而不是往新的access.log或error.log文件中写日志，如何解决？

shell脚本中通常使用mv + touch 或 cp + touch的方式对日志文件进行备份。由于Nginx或php-fpm进程其实只知道日志文件打开后的文件描述符，而不知道打开是哪个文件。使用mv或cp备份文件后，应该是修改了内核中文件描述符对应的文件路径（我猜的！），但Nginx或php-fpm并不知道现在该文件描述符指向的不再是原来的日志文件。所以解决方法就是通知Nginx或php-fpm根据配置重新打开日志文件就可以了！根据前一个问题，可知可以通过kill命令给进程发送USR1信号来实现。

	:::shell
    kill -USR1 `cat php-fpm.pid`
    kill -USR1 `cat nginx.pid`

------

- 工作中使用git的分支模式进行协作开发，需要在测试服务器（HTTP Server使用Nginx，应用程序基于PHP的Yii框架实现）上为每个分支开一个测试环境，为标识使用方便，希望使用HTTP同一个端口，不同的URL前缀标识不同的分支，如master分支的URL为/master/，其他分支的URL为/test/[分支名]/。该如何配置Nginx的虚拟主机？

我们的应用使用Yii框架默认的URL风格(/?r=controller/action)，意味着所有非静态内容(非js、css、图片等)请求指向的服务器资源都是相同的（如`/`或`/xxx/`），而Yii框架的请求处理入口统一为一个index.php文件。Nginx有一个配置变量`$uri`，保存着请求的URL（不带请求参数）。那么可以让所有分支的测试环境共用一个root，再将所有非静态内容请求重定向到`$uri/index.php`就可以了。对于静态文件请求让其根据路径直接获取文件内容即可。但还有一个问题，怎么让分支代码中所有静态文件请求都带上分支对应的URL前缀？这个可以未Yii配置一个名为url_prefix的参数，指定该分支的所使用的URL前缀，然后在HTML模板（我们使用smarty来渲染）中让所有静态文件超链接都带上这个URL前缀。

根据[Yii官方文档给出的Nginx虚拟主机配置](http://www.yiiframework.com/doc/guide/1.1/en/quickstart.apache-nginx-config#nginx)进行修改得到我们需要的配置，如下所示：

	:::text
    listen 80;
    server_name  localhost;

    root html;
    set $yii_bootstrap "index.php";
    location / {
    	index index.html $yii_bootstrap;
        try_files $uri $uri/ $uri/$yii_bootstrap?$args;
    }

    location ~ ^/(protected|framework|themes/\w+/views) {
        deny all;
    }

    location ~ \.(js|css|png|jpg|gif|swf|ico|pdf|mov|fla|zip|rar)$ {
        try_files $uri =404;
    }

    location ~ \.php {
        fastcgi_split_path_info ^(.+\.php)(.*)$;

        set $fsn /$yii_bootstrap;
        if (-f $document_root$fastcgi_script_name){
        	set $fsn $fastcgi_script_name;
        }

        fastcgi_pass 127.0.0.1:9000;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fsn;

       	fastcgi_param PATH_INFO $fastcgi_path_info;
        fastcgi_param PATH_TRANSLATED $document_root$fsn;
    }

	location ~ /\. {
    	deny all;
        access_log off;
        log_not_found off;
	}