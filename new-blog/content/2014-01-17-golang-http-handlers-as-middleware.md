Title: 如何实现Golang的http请求处理中间件（译）
Date: 2014-01-17
Author: youngsterxyf
Slug: golang-http-handlers-as-middleware
Tags: Golang, 翻译, 中间件

原文：[Golang Http Handlers as Middleware](http://capotej.com/blog/2013/10/07/golang-http-handlers-as-middleware/)

译者：[youngsterxyf](https://github.com/youngsterxyf)


大多数现代Web组件栈允许通过栈式/组件式中间件“过滤”请求，这样就能干净地从web应用中分离出横切关注点（译注：面向方面程序设计中的概念？）。
本周我尝试在Go语言的`http.FileServer`中植入钩子，发现实现起来十分简便，让我非常惊讶。

让我们从一个基本的文件服务器开始说起：

    :::go
    func main() {
        http.ListenAndServe(":8080", http.FileServer(http.Dir("/tmp")))
    }


这段程序会在端口8080上开启一个本地文件服务器。那么我们该如何在这其中植入钩子从而能够在文件请求处理之前执行一些代码？来看一下`http.ListenAndServe`的方法签名：

    :::go
    func ListenAndServe(addr string, handler Handler) error


看起来`http.FileServer`返回了一个`Handler`---给定一个根目录就能知道如何处理文件请求。那我们来看看`Handler`接口：

    :::go
    type Handler interface {
        ServeHTTP(ResponseWriter, *Request)
    }


根据Go语言的接口原理，任何对象只要实现了`ServeHTTP`就是一个`Handler`。那么似乎我们需要做的事情就是构造一个自己的`Handler`---封装`http.FileServer`的处理流程。
Go语言的net/http标准库模块内置了一个帮助函数`http.HandlerFunc`，用于将普通函数转变为请求处理函数（handler）：

    :::go
    type HandlerFunc func(ResponseWriter, *Request)


那么我们这样封装`http.FileServer`就可以了：

    :::go
    func OurLoggingHandler(h http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request)) {
            fmt.Println(*r.URL)
            h.ServeHTTP(w ,r)
        })
    }

    func main() {
        fileHandler := http.FileServer(http.Dir("/tmp"))
        wrappedHandler := OurLoggingHandler(fileHandler)
        http.ListenAndServe(":8080", wrappedHandler)
    }


Go语言的net/http标准库模块有很多内置的[处理函数](http://golang.org/pkg/net/http/#Handler)，如[TimeoutHandler](http://golang.org/pkg/net/http/#TimeoutHandler)和[RedirectHandler](http://golang.org/pkg/net/http/#RedirectHandler)，
可以相同的方式混合匹配使用。

------

**译者推荐阅读**

- [Golang Http Server源码阅读](http://www.cnblogs.com/yjf512/archive/2012/08/22/2650873.html)