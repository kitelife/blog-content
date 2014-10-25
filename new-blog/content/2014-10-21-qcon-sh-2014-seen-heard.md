Title: QCon上海2014大会见闻录
Date: 2014-10-21
Author: youngsterxyf
Slug: qcon-sh-2014-seen-heard
Tags: 笔记, 总结


## 技术

#### 主题演讲

**软件项目变更的管理和生存之道**

个人对这个演讲的印象比较深。演讲者即是最近比较火的《Java程序员修炼之道》一书的作者。

演讲大致以“提出问题 -> 分析问题 -> 解决问题”的思路陈述。

问题是：在软件演化的整个过程中，变化是始终存在的。如：

- 基础架构层面的变化：迁移到新的服务提供商、系统升级
- 用户数的变化：突然的增长、持续稳定地增长
- 代码的变更：发布新版本、依赖库升级、新的子系统

这些变化可能会导致两个问题的发生：

- 服务中断：完全无法为用户提供服务，特别是生产环境变更导致的，发布后的服务中断
- 性能问题：性能退化/降级，但可能也不是完全不可用，在预览版(pre-release)和正式发布后(post-release)都可能发生，经常是因为不完全的性能测试造成的。(性能测试是指**基于测量的方法**来理解一定负载下应用的行为)

“变化”导致的问题，说到底是人为造成：

> No matter what they tell you, it's always a people problem.    --- Gerald Weinberg

应对“变化”所带来的问题，需要实现以下几个目标：

- 降低变化的风险
- 提升可靠性：减小服务中断的损失
- 提高可维护性：减小整个平台的耗费
- 可量化的影响：最好可以以节省了多少钱来衡量

“服务中断”、“性能问题”发生的原因通常有：

- 误解了生产环境
	- UAT is My Desktop：“User Acceptance Test”的简写，也就是用户验收测试
	- PROD-like Data is Hard
- 配置问题
- 不恰当的焦点
	- Blame Donkey (all the blame and problems of a situation are being placed upon a single person)
	- 微观分析 (Micro-analysis)
- 孤岛思维 (Silo Mentality)：即团队成员通常仅仅关注各自的职能部门或业务单元。如此有限的关注，阻碍了组织的个别部门对整体运营卓越性的促进作用。
	- Throw It Over The Wall

针对“不恰当的焦点”，需理解，性能调优不是：

- 小提示和技巧的集合
- 秘密武器
- 在项目的末期你洒下的魔法粉尘
- “英雄豪杰”才能干的事情
- ...

不要把问题的原因始终归于某些组件。如果轻易就Blame Donkey只能说明对问题的分析不够充分。**应顶住压力不忙于下结论，分析分析再分析，并与相关人沟通分析的结果。**

不要把精力聚焦在系统非常低的层面(very low-level aspects)上，微观变化(micro-changes)的整体影响是不可知的，实际上可能还会降低系统的性能。
不要做微观分析，除非你的项目是一个已知对此微观分析有效的案例(a known use case for it)，如构建一个通用的库或框架，理解其中的权衡；使用已有的工具来做分析，不要构建你自己的分析工具，使用广泛地与他人讨论你的分析结果。

总而言之，就是测量啊测量，profiling啊profiling。

> The first principle is that you must not fool yourself, and you are the easiest person to fool. -- Richard Feynman

好吧，上边这些只是在解释问题是什么，然后分析了一下问题，那么如何有效地解决问题？

- 理解架构！！！
	- 能凭记忆画出整个应用的架构吗？ 组件关系图、时序图、数据流图 ...
	- 部署：知道应用是如何跨机器/虚拟机分布的吗？
	- 如果架构都没理解，服务中断了还搞个屁啊
- 以数据说话
	- 收集监控数据：应该作为一个正式的流程存在，而不是得到出问题才去临时收集。监控数据也应该集中化收集保存
	- 分析数据：这一环节经常缺失；数据分析解释的技能非常罕见；如果可能就用工具来自动生成报表
	- 确保所有团队都能看到分析报表：团队之间的沟通是必不可少的
	- 理解正常的系统功能是啥样的
- 测量与分析
	- 对抗认知偏见最好的工具就是数据
	- 打日志、以及监控：但更需要分析，数据量可能非常大，问题的模式并非总能肉眼就能识别
	- 常规的/适当的收集过程是必要的，临时抱佛脚肯定不行
	- 确保日志充分：啥叫充分？能够追溯导致服务中断的所有步骤

关于性能，还想说：

- 没有完美的性能，只有可接受的性能（尼玛就不要没完没了地优化了）
- 是最终用户决定性能需求
- 性能不是功能性的需求：但必须有可观测的量化目标，也需要和系统相关人共同来设定
- 性能测试一个迭代的过程

另外，实际操作的过程也得讲究科学的方法啊...

演讲的PPT：[见这里](/assets/uploads/files/Managing-and-Surviving-Change.pdf)

------

**Building a strong engineering culture**

演讲人：Kevin Goldsmith，Spotify公司的技术主管(Director of Engineering)

1 . 什么是文化？

> A pattern of **shared basic assumptions** that a group has learned as it solved its problems of external adaptation and internal integration, that has worked well enough to be considered valid and therefore, to be taught to new members as the correct way to perceive, think, and feel in relation to those problems.   -- Edgar Schein [百度百科](http://baike.baidu.com/view/1177302.htm)

演讲者提出的理解：

> Culture is **the manifestation of the shared values** of the organization as **represented by the actions** of its members.

Values -> Culture -> Processes(流程) + Artifacts(人工制品，如Logo、T恤等) + Rituals(仪式，礼仪) + Beliefs(信仰、新年)

Spotify公司的一些价值观(Values)：

- Learn from failure
- Innovation at every level
- Iterative development
- Agile-ﬁrst
- Data-driven
- Autonomous Teams
- Continuous improvement
- Shared Responsibility
- Transparency
- Trust
- Servant Leadership

2 . 为什么文化很重要？

> Apply the same level of deep thinking about building a culture as you would about building a product. -- Tim O'Reilly, O’Reilly Media

3 . 优秀工程[师]文化(engineering culture)的构成是什么？

- Stuﬀ gets done
- It gets done well
- People are happy
- Leaders provide direction and guidance and GET OUT OF THE WAY
- Success is celebrated
- Failure is used as a way to learn

4 . 保护文化

- Walk the talk
- Hiring is crucial
- Firing is also crucial
- Communicate your values
- Measure against your values
- Your organization reﬂects your values
- Watch out for warning signs

5 . 修复破败的文化

如何知道文化在破败？

- People don’t care
- (Good) People are leaving
- You spend time on the wrong things instead of building your product

如何修复？

- Start with yourself
- Then your team
- Build on successes
- Recruit others
- Grow bottom up

6 . 总结

You have a culture, Whether you think you do or not

Work on your culture, It will determine how things get (or don’t get) done

If you have a good culture, protect it, Make sure everyone understands what you value as a team. Make sure everyone you hire will be happy in your culture.

If you have a bad culture, transform it, A long process, start small and grow. Don’t try to rush it.

You are the culture, The culture is the intersection (average) of the values of the people in it. Want to improve your culture? LIVE THE VALUES

------

还有另外两个主题演讲“The Containerised Cloud”（集装箱式/容器化的云，看题目也能猜出是介绍Docker的）和“SDN控制器集群中的分布式技术实践”貌似也不错，可惜鄙人对于Docker和SDN都没什么实践经验，不甚了解，也就不多写了。

#### 移动与Web

**Blend - 完美地融合WebApp与Native app**

演讲人是来自百度的雷志兴(berg)

对于做Web开发，觉得原生移动App学与做都比较有难度的人来说，这种主题是比较有吸引力的。

当然，难度不是主要原因，原因在于混合式开发移动应用的优点，同时具备：

- Web的灵活性，如：应用可随时发布更新，无需用户下载更新新版本
- 原生移动应用(Native App)良好的体验，包括：交互与性能

从而达到Web应用和原生移动应用的优势互补。

![native-vs-web](/assets/uploads/pics/native-vs-web.png)

那么如何完美融合，以Web技术开发类原生移动应用呢？百度的同学提出Blend技术方案。

Blend是一套灵活、低耦的组件库、API及运行环境。Blend将常用或核心组件Native化， 转场、动画、重点组件由Native完成，Native代码针对关键问题，代码规模小，可控；提出“Every element can be a webview”，单个webview变⼩小，局部性能可控。

具体技术细节见如下PPT截图：

![Blend-technique-overview-1](/assets/uploads/pics/blend-technique-overview-1.png)

![Blend-technique-overview-2](/assets/uploads/pics/blend-technique-overview-2.png)

![Blend-technique-overview-3](/assets/uploads/pics/blend-technique-overview-3.png)

进一步的信息可访问Blend官网：[Clouda.com](http://clouda.com/)

好吧，其实我没有移动开发的经验，所以对这一块的技术也不太懂，待学习。

演讲的PPT：[见这里](/assets/uploads/files/Blend-hybrid-app.pdf) （嗯，PPT很漂亮！）

------

**手机 QQ Hybrid App 优化新思路**

演讲人是来自腾讯 AlloyTeam 的陈桂鸿

这个演讲的内容和上面百度同学的类似，同一个技术方向。

AK (AlloyKit) - 高性能 Hybrid Web 开发框架

AK 架构体系

![ak-arch](/assets/uploads/pics/ak-arch.png)

演讲的PPT：[见这里](/assets/uploads/files/AK-hybrid-app.pdf)

貌似AK还没开源？

AlloyTeam博客：[见这里](http://www.alloyteam.com/)，Github：[见这里](https://github.com/AlloyTeam)

------

**前后端分离实践** 与 **另一个角度看前后端分离**

这两个演讲的内容基本一致，题目更具体点就是“基于Node.js的前后端分离”。演讲人都来自阿里，一个淘宝，一个天猫。

涉及的技术问题用一张图大致就能说明：

![nodejs-split-frontend-backend](/assets/uploads/pics/split-frontend-backend.png)

这种分离方案所要解决的问题是什么呢？

我们通常将“编写运行在浏览器中的代码”的工程师称为Web前端工程师，“编写运行在服务器上的代码”的工程师称为Web后端工程师，这是一种“物理的”区分方法。

在这种区分方法下，目前的Web后端开发基本都是采用MVC框架，那么前后端工程师的工作在View层就有耦合 - 前端工程师编写HTML页面模板，后端工程师负责往模板中注入数据进行渲染展示。这种耦合一方面导致需要更多的时间用于协调沟通，另一方面前端也无法尽可能灵活地优化。

这种耦合在前端也引入MVC框架（如AngularJS、Backbone、EmberJS）后得到解决，但也引入了新的问题：

- 性能问题
- SEO问题
- 代码重用问题

然后就有了上图的方案。前端工程师们振臂呐喊 - 我们不要局限于浏览器！后端工程师们，后端MVC的View、Controller、以及部分Model层的开发都由前端工程师来完成吧，你们就负责部分Model层、负责提供数据就行啦！我们有NodeJS神器！我们不再是前端工程师，我们是全栈工程师！

但这种方案就没问题了么？个人认为至少存在两个问题：

- 这种工程方案的推广的难度有多大？有多少前端工程师熟悉后端开发中的问题？后端开发并不是简单地换个地方写JS代码。
- 这种工程方案必须依赖于NodeJS。任何技术都不是银弹，也不会恒久长存。个人认为如果一种工程解决方案必须依赖于某种具体的技术、甚至一门语言，那就不值得推广。

综合权衡来看，这种工程方案仅在一定的条件（不缺牛逼的全栈工程师、确实需要将前端性能做到极致）下才有采用的必要。

相比这种前后端分离方案，我更赞同演讲中提出的“基于JSON + HTTP接口的版本化管理”，让接口的一切变更都可追溯，这个想法是值得思考和实践的。

演讲PPT：[前后端分离实践](/assets/uploads/files/刘磊-前后端分离实践.pdf)，[另一个角度看前后端分离](/assets/uploads/files/另一个角度看前后端分离.pdf)

推荐阅读：

- [Web 研发模式演变](https://github.com/lifesinger/lifesinger.github.com/issues/184)
- [BigPipe学习研究](http://www.searchtb.com/2011/04/an-introduction-to-bigpipe.html)

------

**乐逗游戏发行平台**

演讲人：余中强

这个演讲的干货很多，值得一看。

其中提到的“定位问题-建设云监控系统”和“API监控系统”是我在做或想做的。

![ledou-cloud-monitor](/assets/uploads/pics/ledou-cloud-monitor.png)

![ledou-api-monitor](/assets/uploads/pics/ledou-api-monitor.png)

整个系统的演化经历了：

- 萌芽期

![ledou-arch-stage1](/assets/uploads/pics/ledou-arch-stage1.png)

- 发展期

发展期的第1阶段只是添加缓存、负载均衡集群化：

![ledou-arch-stage2](/assets/uploads/pics/ledou-arch-stage2.png)

发展期的第2阶段则是根据业务垂直化切分系统、水平拆分数据表等：

![ledou-arch-stage2-ext](/assets/uploads/pics/ledou-arch-stage2-ext.png)

- 壮大期

![ledou-arch-stage3](/assets/uploads/pics/ledou-arch-stage3.png)

在系统演化过程中也得到了如下经验：

![ledou-optimize-lessons](/assets/uploads/pics/ledou-optimize-lessons.png)

![ledou-design-lessons](/assets/uploads/pics/ledou-design-lessons.png)

演讲PPT：[见这里](/assets/uploads/files/余中强-乐逗手游发行技术平台.pdf)

------

(未完待续...)