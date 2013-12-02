Title: 仓库作业机器监控系统设计与实现
Date: 2013-11-29
Author: youngsterxyf
Tags: 技术, 总结, 笔记, Golang
Slug: inner_warehouse_monitor_system

近期在参与一个仓库作业机器监控项目。该项目的需求背景是：公司的电商业务在全国各地有多处或大或小的仓库，仓库的作业人员（没有IT技术背景）经常反馈/投诉作业机器断网、断电、连不了服务等问题。实际情况经常与反馈的不一致，但运维侧并没有数据可以证明，所以才有了这个项目的需求。

为了避免大量监控数据上报影响到生产系统的网络服务，系统采用如下结构：

![inner_warehouse_monitor](/assets/uploads/pics/inner_warehouse_monitor.png)

1. 实现一个agent用于在仓库作业PC或作业PDA上获取机器的监控数据；
2. 在仓库本地服务器上实现一个数据收集处理服务，提供API给agent上传监控数据；数据收集处理服务会将接收到的数据持久化到数据库，提供给仓库本地服务器上的webApp进行数据展示等；
3. 中心服务器可以调用各个仓库本地服务器上的webApp提供的数据查询接口（数据用于定位、发现问题）；定期按需对各个仓库本地服务器上的数据进行归档。

这样，主要的工作都集中在**作业机器上的agent**和**数据收集处理服务、webApp**。这其中最关键的又是**数据收集处理服务**。考虑到需要多地部署运维仓库本地服务器，而且某些大仓库作业机器的数目目前已多达800-1000，我们做了如下技术选型：

1. Golang实现agent、数据收集处理服务、webApp；
2. 以SQLite作为数据库来存储agent上报的所有数据；
3. 以[NSQ](http://bitly.github.io/nsq/)作为异步消息队列中间件；

选用Golang的理由是：可以静态编译，部署简单，只需将变异好的可执行二进制程序丢到服务器上跑起来就可以了。
选用SQLite的理由是：不必像MySQL那样安装server程序，无需额外部署维护。当然SQLite的文件锁会大大影响数据库读写性能，我们通过尽可能拆分数据库，将不同的指标数据存储在不同的SQLite DB文件中，甚至将每台作业机器每个指标的每天的数据分别存储在不同的DB文件中，来尽可能减小文件锁的性能影响，目前看来效果还不错。
选择NSQ的理由是：Golang实现、分布式、伸缩性好、性能高、支持HTTP/TCP协议、自带web管理界面等。

详细的系统结构图如下所示：

![inner_warehouse_monitor-arch](/assets/uploads/pics/inner_warehouse_monitor-arch.png)

NSQ支持多topic（不同topic的数据不同），topic又可以有多个channel（同一个topic的所有channel中的数据相同，以多播的方式实现，每个channel在client中有一个对应的处理流程来处理channel中的数据）。我们将作业机器不同的监控指标数据作为不同topic传入NSQ，多数指标数据只需持久化到数据库以备后用，所以这些topic仅需一个channel。

webApp基于Beego框架实现，避免重复造轮子、工作量小。webApp中的数据展示采用HighCharts、Raphael实现，兼容性好。

对于机器指标数据，其实不应该使用关系型数据库来存储，因为这种数据的特点是：写入之后只读不改、时间序列的、几乎没有关系型的读取操作、连续批量数据读取，所以开源监控系统如Cacti、Ganglia等均使用RRDtool来读写指标数据。所以如上所述，我们将指标数据的存储尽可能地拆分成多个文件以提高读写性能而不会造成其他问题。

目前，系统工作良好。之后会对系统做压测，如果出现瓶颈，多半还是在数据存储上，这样的话我们可能会尝试RRDtool或[InfluxDB](http://influxdb.org/)。
