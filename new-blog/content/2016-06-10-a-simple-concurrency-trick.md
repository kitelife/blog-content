Title: 关于并发的一个小技巧
Date: 2016-06-10
Author: youngsterxyf
Slug: a-simple-concurrency-trick
Tags: 笔记, SQL

前段时间在参与实现一个新业务系统的Demo。该系统集成了多个已有系统的数据，涉及的数据量较大，但由于人力少，时间短，没法专门做一个数据处理子系统，所以只能写了很多数据处理的脚本。

![](https://raw.githubusercontent.com/youngsterxyf/youngsterxyf.github.com/master/assets/uploads/pics/a-simple-concurrency-trick.png)

为了复用一些代码，这些数据处理脚本和业务系统一样都是使用PHP实现。在某些数据上报API写入的数据较快较多时，脚本处理不过来（特别在脚本涉及一些网络请求时），只能搞起并发处理 - 在我们的情况下，最简单的并发方式就是多运行几个脚本实例。

但一切没那么简单：脚本从数据库中取出未经处理的多行数据，逐行处理数据，并将处理后的数据更新到原来的数据行中，运行多个脚本实例时，为了避免更新冲突，只好加事务，但加事务后就会频繁发生事务回滚，数据处理速度还是上不去。

那么该怎么办呢？

参考哈希的思路，我对脚本做了一点调整，下面举例说明：

- 假设对同一脚本运行`5`个实例，为每个实例进程分配一个ID，依次为：0、1、2、3、4
- 对脚本实例获取数据的SQL，增加选择条件：`MOD(id, 5)=SID`（SID为当前脚本实例的ID） - 即使用数据行的`id`对实例数取模，如果结果等于实例的ID，则取出来。这样多个实例之间不会取到相同的数据行，也就不会发生冲突回滚。

写个SHELL脚本来启动脚本的多个实例：

```shell
#!/usr/bin/env bash

pn=5
for id in 0 1 2 3 4
do
/path/to/bin/php /path/to/script.php $pn $id > script-$id.log 2>&1 &
done
```

------

嗯，这只是一个小技巧。

