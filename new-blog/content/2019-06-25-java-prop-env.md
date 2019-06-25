Title: Java System.getProperty VS. System.getenv（译）
Date: 2019-06-25
Author: xiayf
Slug: java-prop-env
Tags: 翻译, Java

原文：[Java System.getProperty vs System.getenv](https://www.baeldung.com/java-system-get-property-vs-system-getenv)

## 1、简介

Java 应用代码中会自动引入 `java.lang` 包。这个包包含很多常用的类，包括 `NullPointerException`、`Object`、`Math`、`String` 等等。

其中 `java.lang.System` 类是一个 final 类，这意味着开发者无法继承它，其所有方法都是静态的（static）。

System 类中有两个方法，分别来**读取系统属性（system properties）和环境变量（environment variables）**，下面我们来看看这两者的区别。

## 2、使用 System.getProperty()

Java 平台使用一个 `Properties` 对象来提供**本地系统相关的信息和配置**，我们称之为 **系统属性**。

系统属性包括当前用户、当前 Java 运行时版本 以及 文件路径分隔符诸如此类的信息。

如下代码中，我们使用 `System.getProperty("log_dir")` 来读取 *log_dir* 属性值。我们也会使用默认值参数，这样如果属性不存在，`getProperty` 则返回 */tmp/log*：

```java
String log_dir = System.getProperty("log_dir", "/tmp/log");
```

如果希望在运行时变更系统属性，则可以使用 `System.setProperty` 方法：

```java
System.setProperty("log_dir", "/tmp/log");
```

我们可以以如下格式使用命令行参数向应用传递指定属性或配置值：

```
java -jar jarName -DpropertyName=value
```

比如 将 app.jar 的 foo 属性值设置为 bar：

```
java -jar app -Dfoo="bar"
```

System.getProperty 返回的一定是一个字符串。

## 3、使用 System.getenv()

环境变量是类似 Properties 的一些 键/值 对。许多操作系统都提供环境变量的方式向应用传递配置信息。

设置环境变量的方式，各操作系统之间有所不同。例如，Windows 中，我们使用控制面板中的系统工具（System Utility）应用来设置，而 Unix 系统则使用 shell 脚本。

**创建一个进程时，该进程默认会从其父进程继承一个克隆的上下文环境**。

如下代码片段演示：使用一个 lambda 表达式来输出所有环境变量。

```java
System.getenv().forEach((k, v) -> {
    System.out.println(k + ":" + v);
});
```

**getenv() 返回一个只读的 `Map`**。尝试向该映射中添加值，会抛出 `UnsupportedOperationException` 异常。

可以使用变量名称作为参数调用 `getenv` 来获取单个变量值：

```java
String log_dir = System.getenv("log_dir");
```

此外，我们可以在应用中创建一个新进程，并向其上下文环境中添加新的环境变量。

Java 中，我们使用 `ProcessBuilder` 类来创建新进程，该类有一个名为 `environment` 的方法，此方法返回一个 `Map`，不过这个映射不是只读的，这样就可以向其添加新元素：

```java
ProcessBuilder pb = new ProcessBuilder(args);
Map<String, String> env = pb.environment();
env.put("log_dir", "/tmp/log");
Process process = pb.start();
```

## 4、区别

这两者本质上都是提供 字符串类型 键值 信息的映射，区别在于：

1. 我们可以在运行时变更 系统属性（Properties），但是 环境变量（Environment Variables）仅是操作系统环境变量的一个不可变拷贝。
2. 仅 Java 平台包含这个 系统属性 特性，而 环境变量 则是操作系统层面提供，全局可用的 - 运行在同一个机器上的所有应用都可以访问。
3. 系统属性 在打包应用时就必须存在[^1]，而 环境变量 则任意时刻都可以在操作系统中创建。

## 5、总结一下

虽然这两者在概念上比较相似，但是 系统属性 和 环境变量 的应用方式差别很大。

二选一通常考量的是生效范围。使用 环境变量，同一个应用可以部署到多个机器上运行不同的实例，并在操作系统级别或者在 AWS / Azure 云平台控制台中进行配置，以免更新配置时还得重新构建应用（**译注：其实使用 系统属性 也可以实现这个效果，比如在 shell 脚本中获取系统环境变量，然后作为系统属性通过 Java 命令行参数传递给应用**）。

`getProperty` 方法名称是驼峰风格，但 `getenv` 不是，谨记！

[^1]: 
    原文是这么写的，但我认为这句话有问题。系统属性明明可以在应用运行时通过命令行参数指定，也可以将属性文件打包到应用包中，在运行时加载（通过 `System.getProperties().load` 方法）。
