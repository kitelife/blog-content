Title: 中心化日志记录架构（译）
Date: 2014-10-14
Author: youngsterxyf
Slug: centralized-logging-architecture
Tags: 翻译, 日志, 架构

原文：[Centralized Logging Architecture](http://jasonwilder.com/blog/2013/07/16/centralized-logging-architecture/)

译者：[youngsterxyf](https://github.com/youngsterxyf)

在[中心化日志记录](http://jasonwilder.com/blog/2012/01/03/centralized-logging/)一文中，我介绍了几个工具，用于解决中心化日志记录的问题。但这些工具一般仅能解决这个问题的一部分，
这意味着你需要综合使用几个工具来构建一个健壮的解决方案。

你需要解决问题的这几个主要方面：*收集*、*传输*、*存储*、以及*分析*。某些特殊的应用场景下，也许还希望具备*告警*的能力。


#### 收集

应用程序以不同的方式产生日志，一些是提供syslog，其他一些是直接写到文件。如果考虑一个运行在linux主机上的典型web应用，在`/var/log`目录会有十几个甚至更多的日志文件，
如果一些应用指定日志存放在HOME目录或者其他位置，则这些目录下也是如此。

如果你正在支持一个基于web的应用，开发人员或者运维同事需要快速地访问日志数据以便对线上问题进行排错，那么就需要一个能够近乎实时监控日志文件变化的方案。
如果你使用基于日志拷贝的方式 --- 文件以固定的时间间隔拷贝到一台中心服务器上，那么你仅能检查与复制操作频率相同的新增日志数据。当站点已经挂掉，而你正在等待相关日志数据的复制，
那么一分钟一次的 rsync cron 任务也许还不够快。

从另外一个角度来看，如果你需要分析线下日志数据，计算各种度量指标，或者其他批量工作，那么文件复制的策略也许正合适。


#### 传输

日志数据会在多个主机上快速地累积起来。为了高效传输日志数据到中心位置，并保证数据不丢失，可能需要额外的工具。

[Scribe](https://github.com/facebookarchive/scribe)、[Flume](http://flume.apache.org/)、[Heka](https://github.com/mozilla-services/heka)、[Logstash](http://logstash.net/)、
[Chukwa](http://chukwa.apache.org/)、[fluentd](http://www.fluentd.org/)、[nsq](https://github.com/bitly/nsq)、[Kafka](http://kafka.apache.org/) 这些框架正是被设计用于
从一个主机到另一个主机可靠地传输大量数据。虽然它们都是用于解决数据传输问题的，但做法却不相同。

例如，[Scribe](https://github.com/facebookarchive/scribe)、[nsq](https://github.com/bitly/nsq) 以及 [Kafka](http://kafka.apache.org/)，要求客户端通过它们的API记录日志数据，
通常，应用程序代码会编写成直接将日志写到这些工具中，这样能够减小延迟，提高可靠性。如果你需要的是中心化的日志文件数据，那么就需要跟踪(tail)日志文件变更，
然后将日志数据通过这些工具各自的API流式写入。如果产生需要收集的日志数据的应用由你控制着，一切会高效得多。


[Logstash](http://logstash.net/)、[Heka](https://github.com/mozilla-services/heka)、[fluentd](http://www.fluentd.org/) 以及 [Flume](http://flume.apache.org/) 则提供许多输入源方式，
支持本机跟踪(tailing)文件变化并可靠地传输数据。对于更广泛的日志收集来说，是个更合适的选择。

虽然 [rsyslog](http://rsyslog.com/)和[Syslog-ng](http://www.balabit.com/network-security/syslog-ng) 通常被认为是事实上的日志收集器，但并不是所有应用程序都使用 syslog。


#### 存储

现在可以传输日志数据了，但数据存放在哪呢？中心化的存储系统需要能够处理随着时间数据的增长。每天都会增加一定量的数据存储，数据量和产生日志数据的主机和进程数量相关。

如何存储依赖于以下几个问题：

- *需要存储多长时间* --- 如果日志是用于长期归档的目的，并且不需要即时分析，那么 [S3](http://aws.amazon.com/cn/s3/)、[AWS Glacier](http://aws.amazon.com/cn/glacier/) 或磁带备份
    也许是合适的选择，因为它们对于大量数据的存储相对比较廉价。如果仅需要几天或者几个月的日志，将数据存储到某种分布式存储系统，
    如：[HDFS](http://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)、[Cassandara](http://cassandra.apache.org/)、
    [MongoDB](http://www.mongodb.org/) 或 [ElasticSearch](http://elasticsearch.org/)也是不错的。如果仅需要保留几个小时的数据用于实时分析，使用[Redis](http://redis.io/)也可以。

- *应用场景的数据量* --- Google一天的日志数据量肯定远大于ACME运输物资公司（译注：原文是ACME Fishing Supplies，正确的应该是ACME Shipping Supplies）一天的日志。
    你选择的存储系统当数据量增大时应该允许水平扩展。

- *需要如何访问日志* --- 某些存储系统是适于实时甚至批量分析的。AWS Glacier 或磁盘备份加载一个文件就需要花费若干小时。如果需要访问日志进行产品排错，这就不好使了。
    如果计划进行更多的交互式数据分析，将日志数据存储到 [ElasticSearch](http://elasticsearch.org/) 或 [HDFS](http://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
    让你能够更加有效地使用原始数据。某些日志数据非常庞大，就只能使用面向批量处理的框架进行分析了。这种情况下事实上的标准方案是 [Apache Hadoop](http://hadoop.apache.org/) 
    配合 [HDFS](http://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)。


#### 分析

一旦日志已经存到一个中心化存储平台，就需要一种方式来分析日志。最常见的方式是定期执行一个面向批量处理的进程。如果日志是存储在 [HDFS](http://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html) 中，
那么 [Hive](http://hive.apache.org/) 或 [Pig](http://pig.apache.org/) 相比编写原生MapReduce任务，更易于帮助分析数据。

如果需要一个用于分析的用户界面，可以将解析过的日志数据存到 [ElasticSearch](http://elasticsearch.org/)，然后使用一个前端方案，如 [Kibana](http://kibana.org/) 或 
[Graylog2](http://www.graylog2.org/)来查询检查数据。日志解析可以通过 [Logstash](http://logstash.net/) 或 [Heka](https://github.com/mozilla-services/heka)，
应用程序也可以直接以JSON格式记录日志。这种方式允许更加实时、交互式的数据获取，但不适于大批量的处理。


#### 告警

最后一个组件，有时是可以锦上添花的 --- 针对日志模式或基于日志数据计算出来的度量指标进行告警。两种常见用法是：错误报告和监控。

多数日志数据是无关紧要的，但错误日志则通常说明存在问题。让日志系统在问题发生时给相关人员发送邮件或通知，相比让某个人重复地监视事件，要高效得多。
有几种服务组件可单独提供应用错误日志记录的功能，如 [Sentry](https://www.getsentry.com/) 或 [HoneyBadger](https://www.honeybadger.io/) 。这些服务也可以聚合重复的异常，
方便你获知错误发生的频率是怎样的。

另一个使用案例是监控。例如，你可能有上百个web服务器，想知道它们是否开始返回500响应状态码。如果可以解析web日志文件，根据状态码记录一个度量指标，
当度量指标超过了一个特定的阈值就可以触发告警。 [Riemann](http://riemann.io/) 就是被设计用于检测这种场景的。


希望本文能提供一个基本模型帮助你针对你的应用环境设计一个中心化日志记录方案。
