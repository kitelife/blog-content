Title: 如何杀死defunct进程
Date: 2016-02-18
Author: youngsterxyf
Slug: kill-defunct
Tags: Linux

原文：[How to kill defunct process](https://kenno.wordpress.com/2007/04/04/how-to-kill-defunct-process/)

译者：[youngsterxyf](https://github.com/youngsterxyf)

defunct进程是指出错损坏的进程，父子进程之间不会再通信。有时，它们会演变成“僵尸进程”，存留在你的系统中，直到系统重启。可以尝试 “kill -9” 命令来清除，但多数时候不管用。

为了杀死这些defunct进程，你有两个选择：

- 重启你的计算机
- 继续往下读...

我们先看看系统中是否存在defunct进程：

```
$ ps -A | grep defunct
```

假设得到的输出如下所示：

```
8328 ? 00:00:00 mono <defunct>
8522 ? 00:00:01 mono <defunct>
13132 ? 00:00:00 mono <defunct>
25822 ? 00:00:00 ruby <defunct>
28383 ? 00:00:00 ruby <defunct>
18803 ? 00:00:00 ruby <defunct>
```

这意味着存在6个defunct进程：3个mono进程，以及3个ruby进程。这些进程之所以存在，可能是因为应用程序写得很烂或者用户做了不常见的操作，在我这，一定是我写的mono C#程序存在严重问题 :smile: 。

现在，我们来看看这些进程的ID及其父进程ID：

```
$ ps -ef | grep defunct | more
```

以上命令的输出如下：

```
UID PID PPID ...
---------------------------------------------------------------

kenno 8328 6757 0 Mar22 ? 00:00:00 [mono] <defunct>
kenno 8522 6757 0 Mar22 ? 00:00:01 [mono] <defunct>
kenno 13132 6757 0 Mar23 ? 00:00:00 [mono] <defunct>
kenno 25822 25808 0 Mar27 ? 00:00:00 [ruby] <defunct>
kenno 28383 28366 0 Mar27 ? 00:00:00 [ruby] <defunct>
kenno 18803 18320 0 Apr02 ? 00:00:00 [ruby] <defunct>
```

- UID：用户ID
- PID：进程ID
- PPID：父进程ID

如果你使用命令 “kill -9 8328” 尝试杀死ID为8328的进程，可能会没效果。要想成功杀死该进程，需要对其父进程（ID为6757）执行kill命令（`$ kill -9 6757`）。对所有这些进程的父进程ID应用kill命令，并验证结果（**$ps -A | grep defunct**）。

如果前一个命令显示无结果，那么搞定！否则，可能你需要重启一下系统。

## 参考文献

- [http://wagoneers.com/UNIX/KILL/Kill.html](http://wagoneers.com/UNIX/KILL/Kill.html)
- [http://www.cts.wustl.edu/~allen/kill-defunct-process.html](http://www.cts.wustl.edu/~allen/kill-defunct-process.html)

------

**译注**

执行命令 `ps aux | grep defunct`，如果进程为defunct，则其第8列为 `Z` 。如下所示：

```
work     13391  0.1  0.0      0     0 pts/0    Z    10:50   0:23 [python] <defunct>
work     13393  0.0  0.0      0     0 pts/0    Z    10:50   0:15 [python] <defunct>
work     13394  0.0  0.0      0     0 pts/0    Z    10:50   0:15 [python] <defunct>
work     13395  0.1  0.0      0     0 pts/0    Z    10:50   0:28 [python] <defunct>
work     13396  0.0  0.0      0     0 pts/0    Z    10:50   0:15 [python] <defunct>
work     13397  0.1  0.0      0     0 pts/0    Z    10:50   0:23 [python] <defunct>
work     13398  0.0  0.0      0     0 pts/0    Z    10:50   0:15 [python] <defunct>
work     13399  0.1  0.0      0     0 pts/0    Z    10:50   0:22 [python] <defunct>
work     13400  0.0  0.0      0     0 pts/0    Z    10:50   0:15 [python] <defunct>
work     13401  0.1  0.0      0     0 pts/0    Z    10:50   0:22 [python] <defunct>
work     13402  0.0  0.0      0     0 pts/0    Z    10:50   0:16 [python] <defunct>
work     13403  0.0  0.0      0     0 pts/0    Z    10:50   0:14 [python] <defunct>
work     13404  0.0  0.0      0     0 pts/0    Z    10:50   0:15 [python] <defunct>
work     13405  0.0  0.0      0     0 pts/0    Z    10:50   0:15 [python] <defunct>
work     13406  0.0  0.0      0     0 pts/0    Z    10:50   0:16 [python] <defunct>
work     13407  0.0  0.0      0     0 pts/0    Z    10:50   0:02 [python] <defunct>
work     13408  0.0  0.0      0     0 pts/0    Z    10:50   0:14 [python] <defunct>
```



