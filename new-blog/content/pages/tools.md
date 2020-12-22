Title: 工具集
Date: 2013-11-02
Author: youngsterxyf
Slug: tools

## 命令行工具与解决方案

- （置顶）[命令行乐园](http://www.commandlinefu.com/commands/browse)
- （置顶）[命令行的艺术](https://github.com/jlevy/the-art-of-command-line/blob/master/README-zh.md)

- [The Linux Alternative Project](http://www.linuxalt.com/)
- [Windows命令行列表](http://technet.microsoft.com/en-us/library/bb490890.aspx)
- [Bash scripting cheatsheet](https://devhints.io/bash)
- [Curl cheatsheet](https://devhints.io/curl)
- [httpie cheatsheet](https://devhints.io/httpie)
- [shellcheck](https://www.shellcheck.net/)

- `docker commit [container id] bwse:1.0`

- `docker run -it -v /Users/xiayf:/home/xiayf bwse:1.0 /bin/bash`

- 使用 pv 和 nc 传输文件并显示进度条：`pv [文件路径] | nc [服务端 ip] [服务端 nc 端口]` 

- 带过滤条件和条数限制的 HBase 扫表：`scan 'ad:indexlib', {LIMIT => 10, FILTER => "SingleColumnValueFilter('meta', 'isOnline', =, 'binary:0')"}`

- 并行运行：`cat data | parallel -j 10 -L 1 ./run.sh`：`-j 10` - 启动10个进程，`-L 1` - 一个进程处理多少行数据

- 删除1天内未更改过的文件：` find . -mtime +1 -exec rm {} \;`

- 按某列排序输出（比如第2列）：sort -n -k2 file

- bat：better cat，https://github.com/sharkdp/bat

- shell/bash 交集、并集、差集：并：`sort -m <(sort file1 | uniq) <(sort file2 | uniq) | uniq`；交：`sort -m <(sort file1 | uniq) <(sort file2 | uniq) | uniq -d`；差(file1 - file2)：`sort -m <(sort file1 | uniq) <(sort file2 | uniq) <(sort file2 | uniq) | uniq -u`

- 按模式批量删除redis数据项：`bin/redis-cli -a 'password' --raw KEYS "cron_task_status__*" | xargs -d '\n' bin/redis-cli -a 'password' DEL`

- 递归查询某目录下的最大文件：`find -type f -exec stat -c "%s %n" {} \; | sort -nr | head -1`

- 查看所有库/模块的docstring：`python -m pydoc -p 8080`

- Linux中查看当前所有的资源限制：`ulimit -a`；设置内核可以同时打开的文件描述符的最大值为2048：`ulimit -n 2048`

- 使用HTTP/HTTPS协议push大文件时失败，提示RPC failed; result=22, HTTP code = 411，可能是因为Git默认post数据buffer比较小，需要自己设置下：`git config http.postBuffer 524288000 #Set to 500MB`

- 当git不支持https协议时，可以通过禁用SSL认证来继续使用：`git config --global http.sslVerify false`

- Git签出某个tag的代码：`git checkout -b branch_name tag_name` 或 `git checkout tag_name` 或 `git checkout tag/tag_name`

- Ubuntu为Firefox安装Adobe Flash插件： `sudo apt-get install flashplugin-installer`

- 从某网卡上删除绑定的ip：`ip addr del 192.168.2.201/32 dev eth0`

- 图片缩放、格式转换等：`convert`

- Linux上如何删除文本文件中来自Windows的CRLF(^M)的换行符：`dos2unix filename`

- Windows命令行下查看本地路由表： `route print`

- 系统监控工具：``Glances``，可以监控本机也可以通过客户端服务器模式监控其他机器；Glances提供了基于XML/RPC的API便于其他程序调用，可编程；Glances可以将数据输出保存到csv或html格式的文件方便其他程序处理（报告或绘制图形）。Glances是用Python开发的，使用psutil库来采集系统数据，在用户的终端上实时动态的显示重要的系统数据和变化。显示的数据包括：CPU、内存、磁盘、网络等使用情况，内核、运行队列、负载、I/O 状态、消耗资源最多的进程等等。

- 修改文件编码： `iconv -f encoding -t encoding inputfile`

- 查看防火墙设置（包含防火墙规则绑定的网卡）： `iptables -nvL`

- 使用一行python命令查看/解压缩/创建zip文件：1.查看 - `python -m zipfile -l
test.zip`, 2.解压缩 - `python -m zipfile -e test.zip test`, 3.创建 - `python -m
zipfile -c release.zip *.py`

- 查看所有用户的crontab任务(root权限执行)： `for user in $(cut -f1 -d: /etc/passwd); do echo "### Crontabs for $user ####"; crontab -u $user -l; done`

- 删除当前目录下大小为0的文件，且不进一步递归查找：`find -size 0 -prune -exec rm {} \;`

- 从命令行使用HTTP协议做测试的强大工具：cURL，参考 [9 uses for cURL worth knowing](https://httpkit.com/resources/HTTP-from-the-Command-Line/)

- 追踪命令执行过程中的系统调用和信号： `strace`

- CPU/磁盘/网络等系统资源统计工具： `dstat`（很好很强大，可替代vmstat，iostat，ifstat）

- 查看PHP会动态加载的扩展模块： `php -m`

- 递归查找当前目录下所有名为test.txt的文件： `find ./ -name test.txt`

- Windows上查看端口占用情况：`netstat -ano`

- 查看LINUX发行版的名称及其版本号的命令：1. `cat /etc/issue`；2. `lsb_release -a`；3. `cat /etc/redhat-release`(针对redhat，Fedora)

- [ack-grep](http://betterthangrep.com/) --- 比grep更好用的搜索工具，专为程序员优化

- 禁用触摸板：`sudo rmmod psmouse`，开启触摸板：`sudo modprobe psmouse`

- 将man手册转换为pdf格式打印出来阅读，如直接将man命令的手册页转换为pdf格式:`man -t man | ps2pdf - > man.pdf`

- 显示进程树：`pstree`

- 更新Python第三方软件包：`pip install -U [package_name]`

- 从命令行安装.deb文件：`sudo dpkg -i package.deb`

- 打印环境变量：`printenv`

- 查看通过USB接口连接的硬件：`lsusb`

- 查看已安装的软件包：`dpkg --get-selections`

- 由大到小输出home目录下的所有文件（递归的）：`du -a ~/ | sort -n -r | less`

- 每隔x秒执行命令command，显示输出：`watch -n [number_of_seconds] [command]`

- 监听来自端口的网络输入，存入文件中：`netcat -l [recieving_port] > file_copied`

- 将命令的输出通过管道经网络传递给目标ip端口：`[command] | netcat -w [number_of_seconds_before_timeout] [target_ip] [target_port]`

- 使用tar压缩文件并将文件作为流输出，通过管道经网络传递给目标ip端口：`sudo tar -czf - [filename] | netcat -w [number_of_seconds_before_timeout] [target_ip] [target_port]`

- `traceroute`：查看到目标机器/ip的网络路由，如`traceroute www.google.com.hk`

- `nmap`：扫描机器检查开放的网络端口，如`nmap 127.0.0.1`---扫描本地机器的开放端口

- `tee`：在标准输出显示的同时输出到文件，如`ls | tee ls.txt`

- 显示软件包的详细描述信息：`apt-cache show [package_name]`

- `ls`按文件名逆序输出结果：`ls -r`；递归遍历目录：`ls -R`；按时间顺序：`ls -t`，按时间逆序：`ls -tr`；按文件大小排序：`ls -S`。（默认按文件名排序，`-r`表示逆序，`-t`表示按时间排序，`-S`表示按文件大小排序，`-h`表示以方便人阅读的形式输出）

- 系统负载监控：top/htop/nmon

- 查看所有进程：`ps -e`或`ps aux`，另外可通过`ps -e | grep name`来模糊查找是否存在特定进程

- 根据进程名终止进程：`sudo pkill process_name`

- 以树状分支罗列目录内容：`tree [dir_name]`

- 大数据传输：1.`scp -P remoteport username@remoteip:remotedir localdir`或`scp -P remoteport localfile username@remoteip:remotedir`；2.scp之外可以使用命令组合：`gzip -c /home/xiayf/data | ssh username@ip "gunzip -c - > /home/xiayf/data"`

- `ping ip -f`：持续不断地ping某台服务器(泛洪？)，可能会ping死那台服务器

- 重装Ubuntu，一个个安装程序太麻烦，可先在原来的Ubuntu上执行`dpkg --get-selections|awk '{print $1}' > o.txt`导出一个所有已安装程序的列表，然后就可以一键安装了：`cat o.txt | xargs sudo apt-get install`

- 打包后，以 gzip 压缩：`tar -zcvf /tmp/etc.tar.gz /etc`；打包后，以 bzip2 压缩：`tar -jcvf /tmp/etc.tar.bz2 /etc`

- 在Linux系统下, 可以用一个命令很容易批量删除.svn的文件夹：`find . -name .svn -type d -exec rm -fr {} \;`

- 查看当前正在监听的网络端口：`lsof -i` 或者 `netstat -tlnp`

- linux下查看某目录占用的空间大小：`du -h -s`或`du -h -s /* | sort`

- python内嵌的简单便捷HTTP Server：`python -m SimpleHTTPServer Port`

- Python命令行美化输出json数据：`python -mjson.tool json_filename`或者通过管道`some_cmd | python -mjson.tool`，也可以直接在命令行使用双引号包围一个json数据字符串来替代json_filename的位置。而且，如果你安装了 Pygments 模块，可以高亮地打印JSON：`echo '{"json":"obj"}' | python -mjson.tool | pygmentize -l json`。

- 保存某个virtualenv中已安装的package列表，并在另一个virtualenv中原样恢复：1.`(some_env)$pip freeze > requirements.txt`; 2. `(another_env)$pip install -r requirements.txt`

- [Linux性能分析工具](/assets/uploads/pics/linux-performance-analysis-tools.png)

- [酷毙的Linux单行命令](http://www.commandlinefu.com/commands/browse/sort-by-votes)

- [Gnome/KDE键盘快捷键](http://www.novell.com/coolsolutions/tip/2289.html)

## VIM

配置文件：[https://github.com/youngsterxyf/mydotfiles](https://github.com/youngsterxyf/mydotfiles)

