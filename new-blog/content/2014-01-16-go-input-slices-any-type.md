Title: Go - 以任意类型的slices作为输入参数（译）
Date: 2014-01-16
Author: youngsterxyf
Slug: go-input-slices-any-type
Tags: Golang, 翻译

原文：[Go – taking slices of any type as input parameters](https://ahmetalpbalkan.com/blog/golang-take-slices-of-any-type-as-input-parameter/)

译者：[youngsterxyf](https://github.com/youngsterxyf)

最近参与的一个业余项目，[go-linq](https://github.com/ahmetalpbalkan/go-linq)，让我了解到Go语言的类型系统并不是为任何类面向
对象编程而设计的。没有泛型，没有类型继承，也没有提供任何对这些特性有用的东西。

但是，提供了一个名为`interface{}`的类型，你可以向其赋予几乎任意类型的值，不会抛出编译错误，就像.NET的`Object`或Java的`Object`：

    :::go
    var o interface{}
    o := 3.14
    o := Student{Name: "Ahmet"}

我们假设你需要一个可以接收任意类型slices的函数，如果考虑如下这样实现：

    :::go
    func Method(in []interface{}){...}
    ...
    slice := []int{1, 2, 3}
    Method(slice)   // 抛出错误

这样的代码会抛出编译错误，因为`[]int`不是`[]interface{}`。那么该如何解决这个问题呢？你可以要求`Method`的使用者先把slices
转换为`[]interface{}`类型。也就是说他们必须借助于如下类似函数将他们的`[]AnyType`类型参数转换为`[]interface{}`类型：

    :::go
    func conv(in []AnyType) (out []interface{}) {
        out = make([]interface{}, len(in))
        for i, v := range in {
            out[i] = v
        }
        return
    }

但这种实现的扩展性并不好。如果`Method`的使用者（可以是一个常用函数如`Map`、`Filter`等）想向`Method`传递N种不同类型的参数，
那么他们就必须编写N个`conv`函数。

对此，我们该怎么办呢？使用**reflection**（反射）呀！实现一个函数以`interface{}`（可以赋任意类型的值）为输入参数类型，在函数内部
将这个输入参数转换为一个slice，然后用于我们`Method`函数。如下所示：

    :::go
    func takeSliceArg(arg interface{}) (out []interface{}, ok bool) {
        slice, success := takeArg(arg, reflect.Slice)
        if !success {
            ok = false
            return
        }
        c := slice.Len()
        out = make([]interface{}, c)
        for i := 0; i < c; i++ {
            out[i] = slice.Index(i).Interface()
        }
        return out, true
    }

    func takeArg(arg interface{}, kind reflect.Kind) (val reflect.Value, ok bool) {
        val = reflect.ValueOf(arg)
        if val.Kind() == kind {
            ok = true
        }
        return
    }

函数`takeArg()`尝试将传入的参数值转换为指定的[reflect.Kind](http://golang.org/pkg/reflect/#Kind)类型，然后函数`takeSliceArg()`
尝试将传递给它的值（经`takeArg()`转换后）转换为一个`interface{}`的slice。虽然，这样会因为反射而影响到一点性能，但影响并不大。

就是这样了。这种方案启发于Tobia Confronto的[fn项目](https://github.com/tobia/fn)，并[应用到go-linq中](https://github.com/ahmetalpbalkan/go-linq/commit/fa1548dc4ad8126e62c1848df6e6d961753d976e#diff-3)。
