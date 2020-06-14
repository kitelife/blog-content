Title: 关于API访问频率限制的一个问题
Date: 2016-06-05
Author: youngsterxyf
Slug: frequency-limitation
Tags: Nginx, 笔记, 工作

工作中涉及一些对外开放的无需特殊权限的API，用户会因为某些需求而通过程序来频繁访问这些API，导致系统的负载陡增，可能影响系统其它功能的正常使用。虽然做了一些优化让这种API尽可能地轻量，但仍然不够，因此需要进行访问频率的限制。

由于这样的API并不多，所以我们并没有在Nginx这样的反向代理接入层中实现频率限制，而是API自己去实现，而且实现方案比较粗糙 - 基于Memcached的缓存自动过期特性。

方案的PHP示例实现如下所示：

```php
// 每个IP一分钟10次
$limit = 10;

$cache = new Memcached();
$cache->addServer('127.0.0.1', 11211);

$key = __FUNCTION__.$_SERVER['REMOTE_ADDR'];
$requestNum = $cache->get($key);

if ($requestNum !== FALSE && $requestNum > 10) {
    echo json_encode(array(
        'code' => 403,
        'message' => '请求太频繁，请一分钟后再试',
    ));
    return;
}

$cache->add($key, 0, time()+60);
$cache->increment($key, 1);

// ...
```

很明显这种方案有不少问题 --- 高并发时限制不严格，或者服务器内存不足时访问次数值尚未过期就已被剔除。

但本文想详述的是另一个问题。

------

根据访问来源IP进行频率限制，如果API中取到的来源IP是错误的，那么就瞎限制了。

先来看看一张架构图：

![api-request-limitation](https://i.loli.net/2020/06/14/KgHvYRDF7smy61h.png)

一眼就能看出图中“服务器C”的特别之处。

由于一些特殊的问题，我们把到服务器C的请求通过Nginx反向代理到另外两台服务器的Nginx进行处理。

可能有人会疑惑：为什么不直接把服务器C从负载均衡中下线？

原因是：考虑到跨网络运营商的问题，我们配置负载均衡器把来自不同运营商网络的请求转发到与请求来源的运营商相同的服务器。C与A、B不同属于一个网络运营商，比如C属于“北联通”，如果把C下线，就意味着北方联通的网络用户无法访问我们的服务。

所以我们临时性地把到C的服务请求转发到A、B。

------

那么问题来了 - 有用户反馈访问某个API时始终提示“请求太频繁，请一分钟后再试”，但自己并未频繁访问这个API。那么是用户撒谎还是系统的问题呢？

经过仔细排查，最终确定问题就出在Nginx配置C的请求被转发到A、B。对于用户客户端来说，C是服务器，对于A、B来说，C则是客户端。如果不做特殊配置，从C转发到A、B的请求在处理时，A、B拿到的请求来源IP是C的IP，也就意味着到C的API访问请求，都被A、B基于C的IP进行访问频率限制。

以Nginx为例，对于从C转发到A、B的请求，如果A、B要拿到请求的真实来源IP，则需要对A、B及C的Nginx做特殊配置。为解决这个问题，Nginx提供了一个额外的模块`ngx_http_realip_module`，这个模块默认没有编译在Nginx中，需以额外参数`--with-http_realip_module`进行编译。

并对C的Nginx反向代理配置（location块）添加一行：

```
# 把请求来源放在X-Real-IP请求头中
proxy_set_header  X-Real-IP $remote_addr;
```

对A、B的Nginx（server块）添加以下配置：

```
# 说明需要进行真实请求来源IP替换的请求来源，即C所属的IP段或者C的IP
set_real_ip_from 10.0.0.0/8;
# 说明从哪获取真实来源IP
real_ip_header X-Real-IP;
real_ip_recursive on;
```

详细的说明见Nginx文档：http://nginx.org/en/docs/http/ngx_http_realip_module.html

