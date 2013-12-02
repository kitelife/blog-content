Title: HAProxyConsole简介
Date: 2013-12-02
Author: youngsterxyf
Tags: HAProxy,Keepalived,负载均衡,笔记,总结
Slug: re_introduce_haproxyconsole

之前在[Golang中如何让html/template不转义html标签](http://youngsterxyf.github.io/2013/11/01/unescape-html-in-golang-html_template/)、[搭建高可用负载均衡组件及缓存DNS](http://youngsterxyf.github.io/2013/10/16/high-availability-load-balancer-and-dns/)两篇文章中都提到为了方便使用HAProxy，我实现了一个简单的HAProxy负载均衡任务管理系统。前些天我把[代码放在Github上](http://youngsterxyf.github.io/haproxyconsole/)，算是开源吧。

同事使用该管理系统，遇到问题时，由于不清楚其实现，也就无法分析问题出在哪，同时也会有些恐慌，生怕搞挂了HAProxy，毕竟上面承载了一些关键的业务，所以我绘制一张图用于说明HAProxyConsole的应用场景和工作原理。

![HAProxyConsole-arch](/assets/uploads/pics/HAProxyConsole-arch.png)

图中蓝色标识的部分都属于HAProxyConsole。

- 用户通过Web页面增/删/改/查负载均衡任务，但这4个操作直接修改的都仅是数据库（DB.json或MySQL数据库）。另外，HAProxyConsole的Web页面中还嵌入了主从HAProxy自带的数据统计页面。
- 只有当用户点击按钮“应用到主HAProxy”或“应用到从HAProxy”后，HAProxyConsole才会根据DB.json或MySQL中存储的数据和配置文件haproxy_conf_comm.json生成最新的HAProxy配置文件，然后拷贝一份为主HAProxy的配置文件或远程拷贝一份为从HAProxy的配置文件，最后重启HAProxy进程（/path/to/haproxy/sbin/haproxy -f /path/to/haproxy/conf/haproxy.conf -st \`cat /path/to/haproxy/haproxy.pid\`），使最新的配置生效。重启的过程中HAProxy会先检测最新配置文件的正确性，如果不正确，则不会重启。

在部署HAProxyConsole，应按实际情况修改配置文件`app_conf.ini`中的参数值。另外，由于HAProxyConsole在为HAProxy应用最新配置时，是直接覆盖HAProxy原来的配置文件，所以`haproxy_conf_comm.json`中指定的HAProxy数据统计页面所使用的端口应与你原来为HAProxy指定的数据统计页面的端口一致。
