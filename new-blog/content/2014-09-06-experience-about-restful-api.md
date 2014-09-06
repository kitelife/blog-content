Title: RESTful API设计的一点经验
Date: 2014-09-06
Author: youngsterxyf
Slug: experience-about-restful-api
Tags: 笔记, RESTful

前段时间的工作涉及产品开放API的设计与实现，整个过程大致可分为以下几个步骤：

1. 根据需求、原有数据库设计等，花了半天左右的工夫完成初稿；
2. 就初稿与相关同事进行讨论，确定一些细节问题，逐步完善；
3. 根据设计稿，基于Yii框架，配置路由，实现用户身份认证模块；
4. 基于步骤3，逐个实现业务相关API；
5. 对部分代码进行重构，减少不必要的代码重复。主要使用Yii控制器的before_action方法来实现多层过滤器。

### 设计

考虑到RESTful API简洁明了的接口表现形式，一开始我们就一致确定使用RESTful风格的API。参考以前自己使用多个开放平台API的经验，
及[Github的开放API文档](https://developer.github.com/v3/)，大致完成设计初稿。

#### 资源

RESTful API主要有两个核心：

1. HTTP协议的4个谓词 - GET、POST、PUT、DELETE，分别对应“查询”、“新增”、“更新”、“删除”4种操作
2. 资源（resource）

RESTful风格API的设计，最难之处，我认为就是“资源”。

“资源”是什么？“资源”并不是对应数据库中一个一个数据表，“资源”是一个抽象的概念，
你需要思考你的产品服务要通过API为用户提供什么？一个API提供的数据可能涉及多张数据表，所以“资源”与具体的数据库设计是独立的。

“资源”的抽象会遇到一个“粒度”的问题，比如一个API返回的数据不应该太多太复杂。

另外，不同“资源”之间可能存在归属关系，那么是否需要在HTTP API的URL中体现这种归属关系？如果要体现，那么当归属关系的层次较多时，URL的长度可能过长。

举个简单的例子来进一步解释上述问题：

假设我们要通过API提供“全国县一级的天气预报数据”。从这句话的表述可以很明显地知道（因为这句话本身是一个明确的需求）这里的“资源”是“全国县一级的天气预报数据”。

这个“全国县一级的天气预报数据”其实仍是抽象的，天气预报数据可能包含天气、气温、湿度、空气质量等指标，这些指标又是分别存储在不同的数据表中的，那么这个API
的代码逻辑就需要读取几张数据表，然后做合并处理。又或者数据库中存储的数据是区域范围更小更准备的天气预报数据，那么也需要对这些数据按照一定的算法进行处理
得出县一级的天气预报数据。

如果仅通过一个API来提供全国所有县一级的天气数据，那么可以想象，这个API返回的数据有多大多复杂。并且用户可能需要更灵活的数据查询方式，如仅查询某个省份
所有县一级的天气预报数据。那么可以将这个API拆分成以下几个API：

    :::text
    GET /province/
    GET /province/{province_name_or_id}/county/
    GET /province/{province_name_or_id}/county/{county_id_or_name}/weather/

拆分之后，可能需要多次调用API才能获取到需要的数据，但每个API的定义都简单而明确。

对于``GET /province/{province_name_or_id/county/{county_id_or_name/weather/}}``这个URL，可能有人觉得它过长了，可以缩短设计为：

    :::text
    GET /county/{county_id_or_name}/weather/

甚至

    :::text
    GET /{county_id_or_name}/weather/

但我更倾向于归属关系明确的长URL，主要原因是，API服务器端可以验证province_name_or_id与county_id_or_name之间的归属关系，以避免用户错误地调用API，
特别是当涉及增删改操作时。

所以RESTful API设计时有许多细节之处需要权衡。

#### 响应码

RESTful API请求的响应码通常有两种表现形式，一种是直接使用HTTP协议的HTTP code，另一种是HTTP协议的响应码始终为200，但在响应体中加入类似名为code的字段，
来表达当前API请求的响应状态，这个code字段值的含义就是HTTP code含义，除了code字段外可能还会附加一个类似名为message的字段来进一步解释响应状态。

我倾向使用第二种形式，理由是：HTTP协议的HTTP code，在为404、500等错误码时，表现的应该是API服务器端程序的健壮性等问题，是未预期的错误，而响应体中的code字段，
在返回404或500等错误码时，表达是API服务器端已预期到这些可能存在的错误，是主动返回这样的错误码的。这样API的调用者也能更容易判断某些问题的原因；

#### 请求的唯一标识

为了方便快速定位用户反馈的问题，我们在每个API的响应内容中加入一个request_id字段作为API请求的唯一性标识，这个请求处理过程中产生的所有日志都是和这个
request_id关联的，这样可以根据request_id聚合处理关联的log。在用户反馈问题时，仅需提供request_id，我们很容易地就能找到这个请求的所有日志。

但这个request_id是应该作为HTTP相应头的一个字段，还是作为响应体的一个字段返回？我倾向于第二种，理由是：我们希望API调用方能够在日志或数据库中记录
所有请求的request_id，便于以后发现问题时进行问题追踪。对于这种调用方应该处理的响应数据项，明确地放在响应体中会更好。

另外，我们也会每个request_id记录对应请求的监控数据，如响应码、请求处理耗费的时间、请求的调用方、请求处理的路由等。这样在对监控数据进行数据可视化后，
可以主动发现某些隐藏的问题。

### 实现

我们的开放API是基于Yii框架实现。

#### 路由

Yii框架默认的路由形式为：查询字符串r=xxx/yyy，其中xxx为控制器(controller)的名称，yyy为动作方法(action)的名称，这种路由形式对应Yii内部的get路由类型，
因为是默认形式，所以无需额外配置。
Yii另外提供一种名为path的路由形式，即使用URL的路径(path)部分来表达路由。要这种形式的路由需要额外配置Yii框架，如下所示：

    :::php
    'components' => array(
        'urlManager' => array(
            'urlFormat' => 'path',
            'rules' => array(
                array('aaa/bbb', 'pattern' => '/xxx/yyy', 'verb' => 'POST'),
                ...
            ),
        ),
        ...
    ),

urlManager是Yii使用的路由管理组件，其中的urlFormat指明使用path形式的路由，rules中的每一数组项即一个路由配置，路由配置数组的第一个元素（如aaa/bbb），
其中aaa为实际控制器类的名称(不包含Controller后缀)，bbb为控制器类aaa中实际动作方法的名称(不包含action前缀)，pattern元素指明当前路由配置项会处理的URL，
xxx为控制器名称，yyy为动作方法名称，这里可以看出HTTP API URL中的控制器名称、动作方法名称可以和实际的控制器类名称、动作方法名称不一样。verb元素指明
当前路由配置项会处理哪个或哪些HTTP谓词对URL“/xxx/yyy”的请求，多个谓词时以逗号分隔。

#### 响应码

对于API可能用到的所有响应码及其说明，我们使用一个单独的类来集中管理，以避免API中硬编码响应码，以及避免代码重复。如下所示：

    :::php
    <?php
        class CodeStatus {
            const OK = 200; // 成功
            const CREATED = 201; // 创建成功

            const REQUEST_WRONG = 400;
            const TOKEN_WRONG = 403; // token已过期或不存在
            const NOT_FOUND = 404; // 资源不存在
            const LACK_PARAM = 423; // 缺少必要的请求参数
            const WRONG_PARAM = 425; // 请求参数不正确
            const DUPLICATE_RESOURCE = 426; // 已经存在相同的资源

            const SYSTEM_ERROR = 500; // 系统异常

            ...

            public static $status_code = array(
                self::OK => '成功',
                self::CREATED => '创建成功',
                self::TOKEN_WRONG => 'token已过期或不存在',
                self::LACK_PARAM => '缺少必要的请求参数',
                self::SYSTEM_ERROR => '系统异常',
                self::WRONG_PARAM => '请求参数不正确',
                self::DUPLICATE_RESOURCE => '已经存在相同的资源',
                self::NOT_FOUND => '资源不存在',
                ...
            );
        }

API中仅需使用CodeStatus类定义的常量成员即可（如CodeStatus::OK）。


### 推荐阅读

- [Github API v3](https://developer.github.com/v3/)
- [Heroku HTTP API Design Guide](https://github.com/interagent/http-api-design)
