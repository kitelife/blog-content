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

**跨平台移动应用的自动化验收测试**

演讲人：平安科技 柴锋、高云

内容主要是基于Cucumber实现的一个自动化测试工具

Cucumber官网：[http://cukes.info](http://cukes.info/)，推广“行为驱动的开发”（behaviour driven development - BDD），貌似挺有意思。

------

#### 大数据

**eBay用户行为数据流实时处理系统**

演讲人：eBay 汪兴朗

用户行为数据流是指用户在系统/网站的操作，以及操作之间的前后关系。这些数据经过过滤噪音抽取后可以用于用户行为分析、个性化推荐等。

![ebay-jetstream-arch](/assets/uploads/pics/ebay-jetstream-arch.png)

图中Jetstream是eBay自研的一个系统，貌似年内会开源，可以关注一下。

系统处理好的metrics数据存储在TSDB（OpenTSDB？）中。

![ebay-jetstream-key-tech](/assets/uploads/pics/ebay-jetstream-key-tech.png)

演讲PPT：[见这里](/assets/uploads/files/汪兴郎-eBay用户行为数据流实时处理系统.pdf)

------

**互联网常用场景下的大数据架构解析**

演讲人：MediaV 聚效CTO 胡宁

> 一切不以具体应用为前提谈大数据都是耍流氓！

精准的网络广告和个人化推荐（如网购）的原理是一样的。通过这页PPT看看“精准”“个性化”需要考虑的哪些问题：

![for-precise-advertisement](/assets/uploads/pics/for-precise-advertisement.png)

------

**京东基于大数据技术的个性化电商搜索引擎**

演讲人： 京东 刘尚堃

1 . 为什么需要个性化搜索

- 帮助用户从海量商品中快速找到商品
- 满足不同用户的检索诉求
- 提升搜索的惊喜性
- 帮助京东提升长尾商品的曝光

2 . 京东个性化搜索考虑的因素

- 行为
- 偏好
	- 用户画像：兴趣、类目、产品、品牌、修饰（主客观）、购买力、性别、敏感度
	- 偏好三要素：长期偏好、实时偏好、偏好跨平台能力
- 地域
	- 身边的陌生人对什么感兴趣
- 时间
- 好友
	- 身边的熟人对什么感兴趣

------

#### 云计算

**云服务-精益创业者的工具箱**

演讲人：英语流利说 胡哲人

- 计算资源 + 数据的存储：阿里云, AWS中国, 青云, UCloud
- 用户行为的分析：Talking Data, 友盟
- 多媒体资源的存储和分发：七牛, 又拍云
- 消息推送：个推，极光推送
- 系统监控：监控宝，OneAPM
- 邮件发送：SendCloud
- 其他：
	- IM服务：环信/LeanCloud
	- 社交分享：ShareSDK/友盟

精益创业：创业团队专注自己的产品，快速迭代

------

**环信支持千万并发即时通讯的技术要点**

演讲人：环信联合创始人 刘少壮

![huanxin-1](/assets/uploads/pics/huanxin-1.png)

![huanxin-2](/assets/uploads/pics/huanxin-2.png)

![huanxin-3](/assets/uploads/pics/huanxin-3.png)

![huanxin-4](/assets/uploads/pics/huanxin-4.png)

------

#### 自动化运维

**实时运维数据分析**

演讲人：医树网 曾勇

基于 ElasticSearch + Logstash + Kibana 实现日志的集中收集分析展示。

![yishu-elk-usage](/assets/uploads/pics/yishu-elk-usage.png)

------

**织云自动化运维技术介绍**

演讲人：腾讯 梁定安

1 . 运营规范

- 环境标准化
- 操作工具化
- 对象抽象化

一切均可配置，从而达到低维护成本。

2 . 资源设计

![tencent-resource-design](/assets/uploads/pics/tencent-resource-design.png)

------

**海量在线交易背后的运维监控体系建设**

![ctrip-monitor-set](/assets/uploads/pics/ctrip-monitor-set.png)

其中 CATS 用于监控告警追踪管理，包含以下功能：

- 处理报警统一入口
- 报警信息补充
- 重复报警去除
- 报警优先级区分
- 报警抑制
- 报警聚合
- 与工作流系统联动

![ctrip-monitor-future](/assets/uploads/pics/ctrip-monitor-future.png)

![ctrip-monitor-future-arch](/assets/uploads/pics/ctrip-monitor-future-arch.png)

------

#### 互联网金融

**火币网比特币交易所构建实践**

演讲人：巨建华

![huobi-arch-timeline](/assets/uploads/pics/huobi-arch-timeline.png)

------

**浅谈互联网金融的资金安全和对账体系**

演讲人：爱投资CTO 谷云

![aitouzi-definition](/assets/uploads/pics/aitouzi-definition.png)

互联网金融的价值之一在于发挥平台的专业性，给用户提供更多的投资产品选择。

------

**互联网金融浅析**

演讲人：聚爱财 任衡

![juaicai-simple-analysis-1](/assets/uploads/pics/juaicai-simple-analysis-1.png)

*金融的本质是实现资产最优配置，要求平等、高效，而这，恰好与互联网的精髓不谋而合*
*互联网金融的三大基石：货币、支付交易、信用体系*

![juaicai-people-credit](/assets/uploads/pics/juaicai-people-credit.png)

![juaicai-2014-trend](/assets/uploads/pics/juaicai-2014-trend.png)

*Lending Club 会对贷款项目进行评级*

![juaicai-p2b](/assets/uploads/pics/juaicai-p2b.png)

------

#### 隐私与安全

**程序员与黑客**

架构思想：

- 黑客思维需要贯穿「...->架构->研发->运维->...」
- 优美的架构一定是健壮的
- 优美的架构一定是处处优美的：文档、代码、逻辑、人->团队
- 安全的本质是信任
	- 「紧内聚、松耦合」设计思想：紧内聚 -> 最小单元 -> 到一段逻辑代码，松耦合 -> 分离 -> 不信任任何输入

漏洞产生的本质：黑客通过输入提交「特殊数据」，特殊数据在数据流的每个单元里处理，如果某个单元没处理好，在单元输出的时候，就会出现相应单元的安全问题。

分离的艺术：

- 人员职权分离：人是万恶之源；每个角色应该职权清晰，在保证这个「生态系统」可以稳定运行的基础上，尽可能限制目标角色的职权
- 服务器分离：
	- 研发与线上服务器分离：杜绝在线上调试，杜绝把不成熟的代码发布到线上
	- 线上服务器各司其职：按业务分离（主站、子站等业务不一样）、按服务器类型分离（Web、数据库、缓存、X、Y、Z、...）
- 账号权限分离：账号权限和认证授权模型有关
- 文件目录分离：
	- 文件目录设计的关键：命名风格要优美，目录各司其职 & RWX权限要做好
- 代码分离：
	- 代码设计的关键：命名风格要优美；代码紧内聚、松耦合（系统、包、文件、类、函数、一段逻辑代码……）；  挫代码 -> 一堆bugs -> 必然包含一堆漏洞
	- 线上不应该出现SVN/Git权限
	- 线上如果能提交编译后的文件就编译后的
- Cookie分离
- 子域分离：
	- 子域设计的关键：不同的业务放到不同的子域下；松耦合的公共模块可以考虑放到其他域名下
	- 域分离对于XSS攻击来说是一只「拦路虎」

技术选型：

- 任何组件都有漏洞：
	- 一般规律：越流行的开源组件越靠谱；越靠谱的团队打造的组件越靠谱
	- 时刻做好被黑个透的准备：优美的架构多重要；分离设计能大大提高入侵门槛；快速应急 -> 快速自愈

千里之堤溃于蚁穴：

- 程序员使用不靠谱的组件、工具：
	- 有些模块/代码直接COPY自不靠谱的地方
	- 研发、运维工具下载自不靠谱的地方
- 升级中心的相关程序被植入后门
	- 建议用靠谱的源、官方源
	- 做正确的MD5校验
	- 但绝大多数情况下会非常无奈，所以有些高保密机构就不会轻易允许升级
- GitHub Hack：
	- GitHub的搜索语法：
		- smtp @163.com
		- insert password extension:sql size:>1000
		- svn co username password
- 邮箱Hack
- 组件严重漏洞爆发

好建议：

- 黑客思维需要贯穿「...->架构->研发->运维->...」
	- 安全意识优先，安全经验逐渐培养
- 一定要有个优美的架构
	- 更少Bugs意味着更少漏洞
- 透彻理解：安全的本质是信任
	- 明白单元与分离的重要性
- 安全策略的部署一定要全面
- 定期备份机制一定要有
	- 出问题能快速diff排查
- Code Review值得提倡：
	- 万一代码被植入了后门，还有机会发现
- 应急响应要争分夺秒
- 可以请专业的安全团队把把脉
	- 四个维度：培训、防御、审计、监控
- 善用安全辅助工具
	- 日志分析：splunk, logcheck, logwatch
	- 入侵检测/防御：snort, iptables, ipfw, fail2ban, portsentry, tripwire, ossec
	- 后门检测：rkhunter, chkrootkit, lynis
	- 流量监控：Nagios, Cacti, Zabbix
	- 环境隔离：chroot
	- Web抗D/CC：推荐自家产品 jiasule

------

#### 扩展性、可用性、高性能

**基于PXC的MySQL高可用架构探索**

演讲人：去哪儿网 周彦伟

- MMM：http://mysql-mmm.org
- Galera
- Percona Xtradb Cluster（PXC）

------

**构建高可用和弹性伸缩的KV系统**

演讲人：Ucloud 吴斌炜

Redis

- 使用场景：
	- 取最新N个数据的操作
	- 排行榜应用，取TOP N操作
	- 需要精准设定过期时间的应用
	- 计数器应用
	- 消息队列
	- 缓存

------

#### 创业

**我们在豌豆荚如何做产品研发**

演讲人：丁吉昌

豌豆文化：开放、透明、公平

- 董事会议、报告和文档全员可阅
- 你可以问创始人任何问题并得到答复
- 个人成就及评级全公司可阅

研发五步骤：

- 立项（定方向）
	- 电梯时间（一句话愿景）
	- 目标用户的特征和核心需求
	- 现存的解决方案和各自的优劣势
	- 依赖、相关技术驱动和限制
	- 人力需求、发布策略和核心衡量指标
- 定目标（目标管理）：团队朝一个方向努力
	- Objectives & Key Results
		- 首先是个沟通工具
		- 努力的方向和目标，非 Roadmap
		- 必须可量化
		- 制定和执行者一致，团队和个人目标一致
		- 和个人绩效考核无关，不是 KPI
	- 季度 OKR & Review
		- 最佳实践：目标不变，调整主要成果
	- 月度会议 Month Review：
		- 是否需要资源和方向调整
- 控进度（项目管理）
	- 状态同步透明
	- 用最合适的方式多方位沟通
	- 周会/总结
	- 数据验证 (MUCE)
- 带团队（人员管理）
	- 找最优秀的人
	- Re-Org & 换组：绩效合格，每季度可申请换组/工作内容
	- One on One：
		- 经理还是教练？
		- 排忧解难助成长
		- 分享职业规划
	- 个人绩效：
		- 绩效不与 OKR 挂钩
		- 鼓励挑战难度
		- 鼓励超越优秀
		- 低 Level 的事情做不到优秀会惩罚
		- 做事不及格会惩罚
- 排干扰（兴趣管理）
	- Hack Day 发现好玩意
	- Polish Week 查漏补缺

------

**创业期技术团队杂谈**

演讲人：岳旭强

创业实践

- 快速试错
- 活下去是第一诉求
- 极致结果：
	- 简化沟通：下乡、突击队、扁平化
	- 兴趣激发：自由选择权、黑暗骑士
		- 技术工作的三个特性：产品性、工程性、技术(艺术)性。对于这三个特性，工程师有不同的偏向
	- 成就感驱动
		- 明意义
		- 重参与
		- 追结果
	- 极致环境
		- 氛围：自由、简单、开放
		- 极致要求：凡事必有解，且必有最优解
		- 攻城师支持：工具平台、一日三餐、全员Mac、1:1 （实际上应该是有条件了才会有这些福利）

文化养成

- 选拔人才
	- 技术热情
	- 逻辑思维
	- 拿到结果
	- 工程 vs 产品 vs 技术
	- 计划 vs 随机应变
	- 严谨 vs 脱缰野⻢马
	- 重细节 vs 重宏观
	- 深度 vs 广度

------

**Building Lean**

演讲人：Kevin Goldsmith

> The one thing you can’t recycle is wasted time. -- Taiichi Ohno

Key Lean Concepts:

- Anything that doesn’t produce value for customers is waste and a candidate for elimination
- Get value to customers as quickly as possible
- Validate product/market fit in the shortest amount of time necessary
- Scientific, data-driven, approach

Key Lean Ideas：

- Minimum Viable(可行的) Product
- Create hypotheses, validate with experiments and DATA （大胆假设、小心验证？）
- Learn fast, fail fast
- The speed of iteration is more important than the quality of iteration  -- John Boyd

Overcoming doubt：

- Ruthlessly cut features to make the launch
- Commit to consistent, quick, iterations to make up the features we cut

------

## 吐槽

梁漱溟晚年口述一书《这个世界会好吗》，我的回答是：会！只不过需要不断地吐槽！！！

#### 演讲即招聘

这一点本来是没什么好吐槽的。各种大大小小技术会议几乎每个演讲都会在最后附带一句“我们在招人！”，为了增大吸引力，还在演讲中有意无意地说明公司的待遇如何如何、美女如何如何。不过，我倒怀疑这种招聘形式到底能成功招到几个牛人呢？牛人都是主动规划自己的人生的，想去你们公司的，即使你不说招人，他们也会主动联系你，不想去的，说了也等于没说。特别是那些演讲内容或演讲效果一坨屎的，你还想啥呢。所以，对于技术会议，如果要演讲，就好好准备点干货，好好分享，这样才能给招聘增加吸引力。

#### 演讲即产品推销

这种演讲，我真想将它吐槽至死！一点节操都不要！厚着脸皮浪费大家的时间。作为技术人应该是最讨厌这种，产品推销反而适得其反。（好吧，也许这只是我的想法）

#### 演讲即不知所云

这种演讲，怎么说呢... 特别是如果演讲人是个高级工程师之类的，就真心对不起公司、对不起人民了。如果哆哆嗦嗦、词不达意、连个完整的话都说不清、不知所云，通常并不是你水平不行，只能说明你没有好好准备。作为高级工程师，或者有个title的人，紧张、心理素质不好，不应该成为一个糟糕演讲的理由。你的一个糟糕演讲对公司带来的负面影响是很大的，更别想在演讲的最后说“我们招人！”。

该如何准备一次演讲？我的想法是：

- 只分享自己有心得的：如做过的事情或者认真研究过的技术，不是真正懂的东西就不要提，不要给自己挖坑
- 制作幻灯片
	- 先写大纲，划一个演讲内容的范围
	- 根据大纲，逐个部分充实内容
	- 最后根据叙述逻辑（一个比较通用的叙述逻辑是：提出问题->分析问题->解决问题的方案）调整内容的位置，目的是方便听众快速理解
- 在正式演讲前对着幻灯片演练几遍，组织一下表述的语言，特别是幻灯片切换时的语言表述，在大脑中大致记住整个幻灯片的起承转合

好吧，虽然我说得貌似挺有道理，但也多少经验，有时间准备读读《演说之禅：职场必知的幻灯片秘技》一书。

## 感想

技术这东西，基本上都是围着业务转（不管是技术选型，还是深入实践），各家的业务不同，所以有各自的技术方案，但道道也就那些，没多少神奇之处。对于技术人来说，应该紧抓业务深研技术，才能出好成果，涨牛逼经验。

故此，技术会议也没必要那么积极参加，个人觉得大型技术会议对于各中小公司的业务交流及宣传比较有用，对于技术交流的作用其实比较有限。非技术细节的东西要么没必要知道，要么已知道；技术细节也是如此。

不过对于年轻的技术人来说，可以以讲师的身份多参加技术会议，可能对自己的帮助更大。

------

[QCon上海2014大会 幻灯片下载](http://2014.qconshanghai.com/slides.html)