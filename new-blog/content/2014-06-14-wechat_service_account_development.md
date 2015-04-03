Title: 微信服务号开发笔记
Date: 2014-06-14
Author: youngsterxyf
Slug: wechat-service-account-development
Tags: 微信, PHP, 笔记

### 原理

微信服务号的原理比较简单。从请求响应角度来看，逻辑是：

**用户微信客户端 <---> 微信服务器 <---> 微信服务号后台程序 <---> 数据库或Web Service**

也就是，用户的各种请求先经过微信的服务器，微信服务器将请求转发给微信服务号后台程序。

既然是微信服务器把用户请求数据转发给我们开发的微信服务号后台程序，那么在启用服务号的开发模式时就需要提供一个URL。另外为了安全
考虑，还需要提供一个token，用来校验请求是否来自微信服务器。校验的方法见[微信开发者文档](http://mp.weixin.qq.com/wiki/index.php?title=%E9%AA%8C%E8%AF%81%E6%B6%88%E6%81%AF%E7%9C%9F%E5%AE%9E%E6%80%A7)。校验又分两种：

> 在开发者首次提交验证申请时，微信服务器将发送GET请求到填写的URL上，并且带上四个参数（signature、timestamp、nonce、echostr），开发者通过对签名（即signature）的效验，来判断此条消息的真实性。

> 此后，每次开发者接收用户消息的时候，微信也都会带上前面三个参数（signature、timestamp、nonce）访问开发者设置的URL，开发者依然通过对签名的效验判断此条消息的真实性。效验方式与首次提交验证申请一致。

微信服务器转发到微信服务号后台程序的消息以及服务号后台程序返回给微信服务器的响应，都是XML格式，消息中都会指明发送者和接收者。
请求消息中的发送者为微信用户的openid，接收者为服务号开发者微信号，响应消息则相反。

消息中还有一个关键字段MsgType指明消息类型。微信将请求消息分为：普通消息、事件推送、语音识别结果三大类，其中，

- 普通消息分6种：文本、图片、语音、视频、地理位置、链接。
- 事件推送分4种：关注/取消关注事件、扫描带参数二维码事件、上报地理位置事件、自定义菜单事件(点击菜单拉取消息时的事件推送、点击菜单跳转链接时的事件推送)

响应消息也分6种：文本、图片、语音、视频、音乐、图文。

工作中为产品开发的微信服务号，目前对于普通消息，服务号后台程序自动响应一段文本消息；对于事件推送中的关注事件，则是响应一段欢迎、
功能简介的文本消息。

另外我们使用了自定义菜单事件，要想使用该事件，先要为你的微信服务号提供自定义菜单。自定义菜单是通过微信提供的API向其推送的。

在通过API向微信服务器推送自定义菜单时，微信服务器需要确认是否为可信任请求，确认方法是基于请求参数access_token。
access_token需要通过API向微信服务器获取。成功启用服务号的开发模式后，微信会为服务号分配一个AppId和AppSecret，获取access_token时
需要带上这两个参数，用于微信服务器确认是否为已注册服务号的请求。access_token相关文档见[这里](http://mp.weixin.qq.com/wiki/index.php?title=%E8%8E%B7%E5%8F%96access_token)。

当成功获取access_token后就可以通过API创建、删除、查询服务号的自定义菜单了。

自定义菜单相关文档见[这里](http://mp.weixin.qq.com/wiki/index.php?title=%E8%87%AA%E5%AE%9A%E4%B9%89%E8%8F%9C%E5%8D%95%E5%88%9B%E5%BB%BA%E6%8E%A5%E5%8F%A3)。

以下Python代码是对自定义菜单API的简单封装：

    :::python
    #coding: utf-8

    import requests
    import os
    import json
    import time


    class WechatAdmin:
        def __init__(self):
            self.app_id = ''
            self.app_secret = ''
            self.session = requests.session()
            self.access_token_file = 'access_token.json'
            self.access_token = ''

        def fetch_access_token(self):
            if self.access_token != '':
                return self.access_token
            if os.path.exists(self.access_token_file):
                with open(self.access_token_file) as fh:
                    origin_content = json.load(fh)
                    if float(origin_content['update_time']) + float(origin_content['expires_in']) < time.time():
                        return self._remote_fetch_access_token()
                    else:
                        return origin_content['access_token']
            else:
                return self._remote_fetch_access_token()

        def _remote_fetch_access_token(self):
            target_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' \
                         % (self.app_id, self.app_secret)
            r = self.session.get(target_url)
            if r.status_code == 200:
                response_data = r.json()
                if response_data.get('access_token', '') != '' and response_data.get('expires_in', '') != '':
                    new_access_token, expires_in = response_data['access_token'], response_data['expires_in']
                    with open(self.access_token_file, 'w+') as fh:
                        json.dump({'access_token': new_access_token, 'expires_in': str(int(expires_in) - 20),
                                   'update_time': time.time()}, fh)
                    return new_access_token
                else:
                    raise Exception(u'响应内容不对！')
            else:
                raise Exception(u'非正常响应，%d' % (r.status_code,))

        def create_menu(self, content):
            menu_create_api = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s'
            target_url = menu_create_api % (self.fetch_access_token(),)
            try:
                r = self.session.post(target_url, data=content)
                if r.status_code == 200:
                    print r.json()
                else:
                    raise Exception(u'非正常响应, %d' % (r.status_code,))
            except Exception as e:
                print e.message
                self._remote_fetch_access_token()
                self.create_menu(content)

        def fetch_menu(self):
            target_url = 'https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s' % (self.fetch_access_token(),)
            try:
                r = self.session.get(target_url)
                if r.status_code == 200:
                    print r.json()
                else:
                    raise Exception(u'非正常响应，%d, %s' % (r.status_code, r.text))
            except Exception as e:
                print e.message
                self._remote_fetch_access_token()
                self.fetch_menu()

        def delete_menu(self):
            target_url = 'https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=%s' % (self.fetch_access_token(),)
            try:
                r = self.session.get(target_url)
                if r.status_code == 200:
                    print r.json()
                else:
                    raise Exception(u'非正常响应, %d, %s' % (r.status_code, r.text))
            except Exception as e:
                print e.message
                self._remote_fetch_access_token()
                self.delete_menu()


    def main():
        wechat = WechatAdmin()
        # print wechat.fetch_access_token()

        with open('menus.json') as fh:
            wechat.create_menu(fh.read())

        wechat.fetch_menu()
        # wechat.delete_menu()


    if __name__ == '__main__':
        main()

### 开发

对于微信服务号后台程序，当然可以参照微信官方文档，从头开始实现。但可用非官方微信公众号SDK也不少。比如我使用的PHP
SDK是[这个](https://github.com/netputer/wechat-php-sdk)。

其他语言的SDK也可以找找看。


### 注意

- 我在启用微信服务号的开发模式之后，就直接使用该服务号进行开发测试，但在开发测试过程中，已经有一些产品的用户关注了该服务号，那么这个过程中用户的体验会很差。正确的过程应该是**先申请测试帐号进行开发测试，等开发测试完成后，再上线服务号**。

- 自定义菜单在变更之后并不是实时更新的，官方文档的说明是：*创建自定义菜单后，由于微信客户端缓存，需要24小时微信客户端才会展现出来。建议测试时可以尝试取消关注公众账号后再次关注，则可以看到创建后的效果*。

- 微信客户端应该是基于浏览器内核技术的，所以能解释渲染网页元素。图文消息中图片其实是一个img元素，所以需要你自己提供图床。微信官方的公众平台提供的消息发送功能，对于图文消息要求必须带图片，但服务号后台程序响应的图文消息中其实可以留空图片链接，这样用户收到图文消息看到的效果也许就是你需要的。另外，文本消息也是可以带超链接a元素的。
