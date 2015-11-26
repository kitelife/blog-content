Title: 青云 iframe 应用开发
Date: 2015-11-20
Author: youngsterxyf
Slug: qingcloud-iframe-app
Tags: 笔记, 工作, 总结

上周的主要工作是将产品的功能集成到青云。青云提供 iframe 的方式来集成第三方服务，这是一种互利的做法，而且对于青云来说，实现的代价也非常小。

先上图，看看集成的效果：

![ygc-in-qingcloud](https://raw.githubusercontent.com/youngsterxyf/youngsterxyf.github.com/master/assets/uploads/pics/ygc-in-qingcloud.png)

------

对于青云来说，一个iframe应用就是一个URL，由应用开发者提供这个URL，当青云用户访问应用所在的页面时，页面先自动向应用服务器的URL发送数据请求，请求会携带认证信息，应用服务端需要先校验请求确实来自青云，并获取请求中的用户信息，最终响应一个HTML页面内容，青云应用页面收到响应数据后将其置于一个iframe标签中，之后青云用户在iframe页面中的操作都是直接与应用服务器交互。

![qingcloud-iframe-interaction](https://raw.githubusercontent.com/youngsterxyf/youngsterxyf.github.com/master/assets/uploads/pics/qingcloud-iframe-interaction.png)

上图交互流程的第**2**步中，青云服务器向用户响应的内容最终会生成一个包含以下内容的页面：

```html
<form method="POST" action="URL" target="appframe">
    <input type="hidden" name="payload" value="...">
    <input type="hidden" name="signature" value="...">
</form>
<iframe id="..." name="appframe" width="100%" height="100%" frameborder="0">
</iframe>
```

其中`form`的`target`属性指定在何处打开`action`属性值URL。`form`表单会被自动提交到应用服务器的URL，应用服务器响应的页面内容会被置于`target`属性所指定的iframe中展示给用户。

注意：这里form的target属性值与iframe的name属性值应一致；`action`属性值即应用开发者提交给青云的URL。

`form`表单包含两个数据项：`payload` 和 `signature`。

`payload` 是一个JSON字符串经过base64 URL编码后的结果，JSON字符串包含user_id、access_token、action等字段，其中`user_id`是用户在青云的唯一性ID，而 `access_token` 则是调用青云API获取用户相关详细信息时需要的授权码，因为`payload`并没有包含用户相关的详细信息，所以应用服务器在处理URL请求时，如果需要用户的详细信息，则需要经第**4**步来获取。

`signature` 是由base64 URL编码后的payload按HmacSHA256签名，并base64 URL编码得到。

------

为了增强整个交互过程中的数据安全性，青云本身使用HTTPS协议，并且要求应用的URL也必须使用HTTPS协议。

另外，如上所述，为了防止请求伪造，form表单包含一个签名数据项`signature`，应用服务器在处理URL请求时应先校验签名，确认请求来自青云页面。

form表单使用的编码算法和签名生成算法，见[青云文档](https://docs.qingcloud.com/app/common/tutorial.html)，其PHP、Python实现如下所示：

**PHP**:

```php
// base64 URL编码
function base64_URL_encode($data) {
  return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

// HmacSHA256签名
hash_hmac('sha256', $payload, $secret_app_key, true)
```

**Python**:

```python
# base64 URL编码
import base64

def base64_URL_encode(data):
    return base64.urlsafe_b64encode(str(data)).rstrip('=')
    
# HmacSHA256签名
import hmac
from hashlib import sha256

def hmac_sha256(data, secret_app_key):
    hmac_256 = hmac.new(secret_app_key, digestmod=sha256)
    hmac_256.update(data)
    return hmac_256.digest()
```

其中HmacSHA256签名算法需要参数 `secret_app_key` ，这个参数值应为青云为你的iframe应用分配的密钥`secret_app_key`，同时，青云会为每个iframe应用分配一个唯一性ID。

如果你的应用需要经第**4**步获取用户相关详细信息，则还需从青云后台获取API密钥（包含`qy_access_key_id` 和 `qy_secret_access_key` 两项），API请求数据也使用了签名算法，并且算法与上述form表单数据所使用的签名算法相同，青云官方文档对于这一点貌似叙述有误。详细信息见 [青云文档](https://docs.qingcloud.com/app/common/tutorial.html#api)。

------

在开发青云 iframe 应用过程中，我们遇到了两个问题：

1. 用户可能会在浏览器中只刷新iframe内容，比如chrome浏览器中，在iframe内容区域右击鼠标选择“重新加载框架”。之前说过用户在iframe中的操作都是直接与应用服务器交互的，刷新iframe其实是直接向iframe应用URL发送HTTP请求，而不是提交form表单到应用URL，所以请求中没有携带校验信息，无法判断请求是否来自青云。
2. 由于我们的应用服务器有多台，并且未使用集中式session管理，那么如果使用传统的session中记录用户ID的方式，当首次iframe请求之后的请求由不同的服务器来处理，就无法识别出用户。

这两个问题我们都使用了cookie来解决。

对于第1个问题，在处理form表单请求响应结果之前，将表单的payload和signature写入cookie，cookie的路径为应用的相对URL，这样每次用户刷新iframe，这个cookie会自动被发送到应用服务器，服务器端处理请求时，先校验是否存在合法的表单字段payload和signature，如果没有，则检查cookie中是否存在这两个字段值，从而实现兼容。

对于第2个问题，在form表单请求成功处理，识别出当前用户后，将用户的基本信息经过对称加密后存入cookie，cookie的路径为`/`，用户在iframe中操作时产生的所有AJAX请求，应用服务器处理请求时都会先解密该cookie值识别出当前用户。这个过程中涉及的加密方和解密方都是应用服务器，所以虽然使用了对称加密，但并不需要网络传输密钥。

------

青云用户在首次使用我们产品的iframe应用时，系统会自动为青云用户创建一个特定类型的账号X，用户在iframe中操作产生的数据都会被绑到该账号X下。可能存在某些青云用户同时已有我们产品的账号Y，为了方便这种用户，我们的iframe应用允许用户将账号X绑定到账号Y，绑定的过程只需要在iframe应用中登录一次我们产品的账号Y，而这背后的实现是识别出X和Y，将X下的数据绑定到Y，账号绑定之后，用户在iframe中操作产生的数据都是绑定到账号Y的。

------

软件应用肯定需要经过测试才能发布上线（总不能让用户帮你测试吧，哈哈），那么青云iframe应用该如何测试呢？

青云iframe应用在创建之后，需要经过青云官网审核才会上线，上线之后用户才可见。在创建之后、提交审核之前，你可以修改应用的配置信息（比如URL），这一阶段应用只对你自己可见可用，所以你可以将这个阶段作为测试阶段。更重要的是，在青云后台创建应用时，青云服务器并不会检测iframe的URL是否可访问，而且对该URL的请求也是由用户浏览器发起的，这样在测试阶段完全可以配置一个局域网内可访问的URL，测试完成在应用提交审核之前再将URL改成正式的外网可访问的URL即可。


