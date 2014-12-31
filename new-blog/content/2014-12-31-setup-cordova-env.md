Title: Cordova/Phonegap应用构建环境搭建
Date: 2014-12-31
Author: youngsterxyf
Slug: setup-cordova-env
Tags: 笔记, Cordova, Phonegap

混合（Hybrid）移动开发将Web开发与原生开发优势互补，之后应该是一个不错的方向。Phonegap是混合移动开发的一个方案，
开发者可以使用标准的Web技术进行开发，然后使用Phonegap打包成原生APP，也可以为Phonegap开发插件来扩展APP功能。
Cordova是Apache的顶级项目，起于Adobe贡献给Apache基金会的Phonegap技术源码，之后Phonegap官方貌似则专注于提供Phonegap应用的云构建服务。
Phonegap官网的文档与Apache Cordova的文档是相同的，所以从技术上可以将Phonegap与Cordova视为同一个东西。

虽然Phonegap官方提供免费的开放（public）应用以及一个私有应用构建服务。但对于应用调试或插件开发来说，
使用云构建服务上传源码下载APP还是挺耗时间的，不太方便，所以搭建本地的应用构建环境是必要的。

依据Cordova文档的[The Command-Line Interface](http://cordova.apache.org/docs/en/4.0.0/guide_cli_index.md.html#The%20Command-Line%20Interface)
部分，针对Android应用，在Ubuntu上搭建Cordova应用构建环境的步骤如下所示：

#### 1. 安装Node.js和git客户端

- 从[NodeJS官网](http://nodejs.org/download/)下载Linux二进制压缩包，解压缩后将bin路径加入PATH环境变量，即可从命令行执行node、npm命令。
- `sudo apt-get install git`

#### 2. 安装Cordova：

- `sudo npm install -g cordova`

#### 3. 下载JDK：

- `sudo apt-get install default-jdk default-jre`

#### 4. 安装Android SDK：

- 从Android官网的[这里](http://developer.android.com/sdk/installing/index.html)下载Android Studio或独立的SDK工具

如果下载Android Studio，解压缩后执行`bin/android.sh`，Android Studio启动时需要从Google的服务器上获取一些SDK相关的文件，
由于GFW的原因，无法成功获取，也就无法顺利启动。Android Studio网络代理设置的方法（参考[这里](http://stackoverflow.com/questions/27683678/android-studio-component-installation-not-working-in-proxy-security-server?lq=1)）：

在Android Studio首次启动后，可以在HOME目录下找到文件` ~/.AndroidStudio/config/options/other.xml`，在该文件中，可以找到如下几行：

```
<option name="PROXY_TYPE_IS_SOCKS" value="false" />
<option name="USE_HTTP_PROXY" value="false" />
<option name="USE_PROXY_PAC" value="false" />
<option name="PROXY_HOST" value="" />
<option name="PROXY_PORT" value="80" />
<option name="PROXY_AUTHENTICATION" value="false" />
<option name="PROXY_LOGIN" value="" />
<option name="PROXY_PASSWORD_CRYPT" value="" />
<option name="KEEP_PROXY_PASSWORD" value="false" />
```

如果使用HTTP协议的代理，则将“USE_HTTP_PROXY”一项的value改为“true”，“PROXY_HOST”、“PROXY_PORT”的value分别设置为代理的域名和端口，
如果代理需要身份认证，则将“PROXY_AUTHENTICATION”的value改为“true”，并设置“PROXY_LOGIN”、“PROXY_PASSWORD_CRYPT”两项。

重启Android Studio即可。

------

如果下载独立的SDK工具，假设解压缩后的路径为`~/Android`，则添加环境变量`ANDROID_HOME=~/Android`，并将子目录tools加入PATH环境变量。

执行命令 `android` 打开Android SDK管理器，与Android Studio一样，也需要设置网络代理：

- 打开菜单项“Tools -> Options”，填入“HTTP Proxy Server”、“HTTP Proxy Port”两项的值，重新启动Android SDK管理器即可。

------

由于当前Cordora构建Android应用依赖于Android API 19，即Android 4.4.2，所以需要在“Android Studio”或“Android SDK管理器”
下载“Android API 19”相关的依赖包。

*注：下载速度很慢，请耐心等待...*


#### 5. 安装ant

当前Cordora构建Android应用也依赖于ant。从[Apache Ant](https://www.apache.org/dist/ant/binaries/)官网下载二进制包，
解压缩后，将子目录bin加入PATH环境变量。

#### 6. 测试

依次执行以下命令：

- `cordova create hello com.example.hello HelloWorld`，该命令会在当前目录下创建hello子目录；
- `cd hello`，进入该示例工程目录；
- `cordova platform add android`，为该工程添加Android平台支持；
- `cordova build android`，将该工程构建成原生Android应用；
- `cordova emulate android`，打开Android模拟器运行示例应用；

模拟器启动后如下图所示：

![cordova-demo](/assets/uploads/pics/cordova_demo.png)

------

最终生成的apk文件在`hello/platforms/android/ant-build/`路径下，默认名为“CordovaApp-debug.apk”。

对于Cordora项目来说，源码目录即项目的www子目录。
