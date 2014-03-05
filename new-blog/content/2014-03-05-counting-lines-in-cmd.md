Title: Windows命令提示符中统计行数（译）
Date: 2014-03-05
Author: youngsterxyf
Slug: counting-lines-in-cmd
Tags: Windows, 翻译

原文：[Counting lines in Windows command prompt](http://rickardnobel.se/counting-lines-in-windows-command-prompt/)

译者：[youngsterxyf](https://github.com/youngsterxyf)


**使用内置工具FIND统计cmd.exe输出的行数非常方便！**

在命令行环境中工作时，能够统计不同工具的输出结果的行数有时会非常有用。许多Unix/Linux操作系统都包含带有许多功能选项的**wc**
工具，Windows则没有内置一样的替代品，但是Windows命令提示符(cmd.exe)原生支持了部分相同功能。

本文将讲述在cmd.exe中我们可以如何使用**FIND**工具来统计行数。工具find，有些类似于Unix上的grep，自MS-DOS以来就一直存在，
使用简单。


假设我们有一台Windows服务器，想看看当前有多少个活跃的TCP会话。这可以使用netstat命令，并且通过管道连接FIND来查找已建立的会话。


**netstat -ano | find /i "estab"**

![established-TCP-2.png](https://raw.github.com/youngsterxyf/youngsterxyf.github.com/master/assets/uploads/pics/established-TCP-2.png)


这行命令的输出可能会有几百行以至于占满整个命令提示符窗口，而我们可能仅仅关心会话的数目。通过在这行命令之后增加一个**/c**开关选项，
我们就能得到打开的TCP会话的数目。

我们仍然使用上一个命令的过滤规则（通过查找字符串“estab”来找到包含ESTABLISHED状态的行）但带有/c，这样就会仅显现匹配行的数目。

![established-TCP.png](https://raw.github.com/youngsterxyf/youngsterxyf.github.com/master/assets/uploads/pics/established-TCP.png)


如下另一个示例则是查看本地缓存的DNS记录的数目。

![displaydns.png](https://raw.github.com/youngsterxyf/youngsterxyf.github.com/master/assets/uploads/pics/displaydns.png)


选项/c也可以用于统计一个命令输出的所有行。例如，我们想知道目录服务(Active Directory)中分组的数目。通过一个管道连接到**FIND /v "" /c**，
我们能统计所有不匹配(**/v**)空字符串（""）的行（即非空白行）。如果你使用过Unix工具wc，这就相当于**wc -l**。

![find-group-2.png](https://raw.github.com/youngsterxyf/youngsterxyf.github.com/master/assets/uploads/pics/find-group-2.png)


另一个示例是：事件查看器命令行工具**wevtutil**会输出大量日志数据行。如果仅仅想知道现代Windows系统中不同日志的数目，我们可以将几百个日志文件的文件名
通过管道传输给``FIND /v "" /c``。

![wevutil.png](https://raw.github.com/youngsterxyf/youngsterxyf.github.com/master/assets/uploads/pics/wevutil.png)

最后一个示例是：假设有一个日志文件或者类似文件，总共有上千行内容。我们想快速知道包含特定短语的数据行的数目。

**TYPE C:\Windows\Schedlgu.txt | FIND /i "task failure" /c**


------

### 相关阅读

- [Technet - Find](http://technet.microsoft.com/en-us/library/cc725655.aspx)
- [The TYPE command](http://www.robvanderwoude.com/type.php)
- [Technet - Type](http://technet.microsoft.com/en-us/library/cc732507.aspx)
- [Technet - Wevtutil](http://technet.microsoft.com/en-us/library/cc732848.aspx)
- [Technet - Dsquery](http://technet.microsoft.com/en-us/library/cc732952.aspx)