Title: 关于Redis与Memcached的一点澄清（译）
Date: 2015-12-01
Author: youngsterxyf
Slug: redis-vs-memcached
Tags: 翻译, Redis, Memcached

原文：[Clarifications about Redis and Memcached](http://antirez.com/news/94)

译者：[youngsterxyf](https://github.com/youngsterxyf)


如果你了解我，就会知道我并不是那种认为竞品是一件坏事的人。实际上我喜欢用户有选择的空间，因此我很少做将Redis与其他技术做对比这类事情。

然而，为了选择正确的方案，用户必须获取正确的知识，这一点也是理所应当的。

本文的起因是读了Mike Perham写的一篇博文，你也许知道他是Sidekiq这一流行程序库的作者，Sidekiq又恰好使用Redis做后端。因此我毫不认为Mike是一个“反对”Redis的人。但在博文（你可以在 [http://www.mikeperham.com/2015/09/24/storing-data-with-redis/](http://www.mikeperham.com/2015/09/24/storing-data-with-redis/) 找到这篇博文）中，他陈述到：要用缓存，“你可能应该选择Memcached（而不是Redis）”。这样看来，Mike确实简单地相信Redis不适合用做缓存，在文章中他是这样论述的：

- 1) Memcached专为缓存而设计
- 2) 它根本不会有磁盘I/O操作
- 3) 它是多线程的，在多核上能线性扩展到每秒处理100,000个请求

我会一一辩驳以上陈述，之后会提供进一步的信息，这些信息在上面的句子中并没有得到表达，但在我看来与缓存用户及用例更加相关。

**Memcached专为缓存而设计**：我会跳过这个，因为这并不是一个论点。我同样可以说“Redis专为缓存而设计”。因此，就这一点而言，它们是一样的，我们接着来看下一个论点。

**它根本不会有磁盘I/O操作**：使用Redis时，你可以按需求禁用磁盘I/O，所有操作就是纯内存的了。此外，若你确实需要，可以只在重启Redis之时持久化数据库，例如：使用“SHUTDOWN SAVE”命令。再怎么说，即使你根本不使用Redis持久化功能，它也是一个附加值。

**它是多线程的**：确实如此。我的目标是把Redis的I/O线程化（像Memcached那样，从根本上说数据访问本身不是线程化的）。然而，Redis，特别是使用流水线（pipeling）模式后，每个线程每秒能处理超大量的请求（使用密集的流水线，通常能达到每秒50万左右；不使用流水线，也能达到每秒10万左右）。在普通的缓存场景中 - 每个Redis实例是一样的、角色为主、禁用磁盘操作、分区由客户端决定（像“Memcached分区模型”那样） - 每个系统上运行多个Redis进程并不可怕。一旦你这样做，得到的就是一套无共享多线程的设置，那么关键看的是单个线程能够处理的操作量了。上一次我检验Redis时，每个线程至少是和Memached一样快的。内部实现随着时间在改变，因此如今最新版可能有所出入，但我敢打赌两者的性能是相近的，因为它们都竭尽所能利用了能够使用的资源。Memcached的多线程仍然是个优势，因为它让一切更易于使用和管理，但我认为这不是关键性的部分。

再说一点。Mike在谈及每秒执行的操作时，并未说明操作的 \*质量\*。在Redis与Memached这类系统中，相比真正地获取内存数据结构中的数据，命令分发和I/O的代价是主要的。因此本质上在Redis中执行一个简单的GET、SET或一个复杂操作如ZRANK操作，其代价基本是相同的。但是从应用层的角度来看，通过复杂操作能节省很多工作。也许无需分5次获取缓存数据，你只要发送一个简短的Lua脚本就能搞定。因此这两个系统实际的“可扩展性”有许多维度，你能得到是其中之一。

Mike关注的几点问题，我认为唯一有根据的是多线程那个，如果我们将特殊用例下的Redis看做是Memcached的替代品，执行多个Redis进程也能反驳“Memcached多线程更好”这个观点，或者简单地执行一个Redis进程也行，因为做Memcached那样的操作要想打满一个线程是非常非常难的。

## 真正的区别

现在是时候谈论两个系统之间的真正区别了。

- 内存效率

这一点Memcached曾比Redis做得好。在一个被设计为用字典化字符串存储普通字符串的系统中，更好地利用内存相对会更简单。这一区别并不显著，而且大约有5年我没去检验这一点了，但曾经是值得注意的。

然而，如果我们考虑一个长期运行的进程的内存效率，事情就有些不同了。具体细节请读下一节。

但是在真正评估内存效率时，你应该记得考虑：Redis中特殊编码的小型聚合值内存效率非常高。例如：小整数集合在内存存储为一个8、16、32或64位整数的数组，当需要检查某些整数是否存在时，对数级时间就能访问到，因为这个数组是有序的，因为可以使用二分查找。

当你使用哈希来存储对象而不是借助JSON时，同样如此。因此，真正的内存效率必须基于手头的应用案例来评估。

- Redis LRU vs Slab内存分配器

从内存利用的角度来看，Memcached并不完美。如果你恰好有个应用随着时间会改变缓存数据的尺寸大小，很可能会导致严重的内存碎片问题，而唯一的解决方法就是重启应用。从这一视角来看，Redis对内存的利用不会变化莫测。

此外，Redis的LRU最近优化了很多，现在非常接近真正的LRU。进一步的信息可阅读：[http://redis.io/topics/lru-cache](http://redis.io/topics/lru-cache)。如果我没理解错的话，Memcached的LRU依旧是根据它的slab分配器来判断数据过期的，因此有时其行为与真正的LRU相差甚远，但我希望这方面的专家能够针对这个问题说点什么。如果你想测试Redis的LRU，在最近几个版本的Redis中可以使用redis-cli的LRU测试模式。

- 智能缓存

如果你想把Redis用作缓存，并且像Memcached那样使用，那你就真的要错失一些东西了。在我看来，这是Mike那篇博文中的最大错误。越来越多的人从Memcached切换到Redis，是因为他们发现可以以更有用的方式来表现缓存数据。如何保持只缓存某个东西的最新N项数据？使用“脱帽”列表（原文为：capped list）。想获取一个缓存的流行指数？使用一个有序集合，等等。

- 持久化和复制

若你需要，那它们就是重要的优势。例如：使用这一模型扩展高负载的缓存读操作就非常简单；基于持久化 - 按期快照缓存数据 - 重启服务而不丢缓存数据也很简单；诸如此类等等。但是对有些用法来说，这两个特性确实无关紧要。这里我想表达的是存在一些“纯缓存”的应用案例，其中持久化和复制也很重要。

- 可观测性

Redis提供了很多方式以便于观测Redis运行时的行为状态。它提供大量内部度量的详细报告，你可以扫描数据集，观察对象的有效期。可以调优LRU算法。可以为客户端连接命名并使用`CLIENT LIST`来查看关于它们的报告。可以使用`MONITOR`命令来调试你的应用，以及其他高级事项。我相信这是一大优势。

- Lua脚本编程能力

我相信在很多缓存应用案例中，Lua脚本编程能力都是一大助力。例如：如果你有一个JSON缓存数据块，使用一个Lua命令可以抽取其中某个字段并将其返回给客户端，而不需要传输所有东西（从概念上来说，直接使用Redis哈希来表现对象，也可以做到）。

## 结论

Memcached是一个伟大的软件，我多次阅读其源码，对于我们产业来说，它是一个革命，你应该自己查明对你来说，相比Redis，Memcached是否是更好的选择。然而，一切事物都必须如实评估。读到Mike的报告或这些年来读到的类似报告都让我有些恼怒了，所以我决定亮一亮自己的观点。如果你发现有些事情事实上我说得不对，请联系我，我会以“校订”一节来更新这篇博文。


