Title: 那些Python党踩过的PHP坑
Date: 2015-09-05
Author: youngsterxyf
Slug: php-trap-and-tip
Tags: PHP, 笔记

虽说题目是说“PHP坑”，但主要还是因为个人经验不足导致。

#### JSON反序列化 json_decode

函数 `json_decode` 默认反序列化的结果是对象。Python党在做PHP开发用到这个方法时，很可能会跳进这个坑，认为结果应该是个数组，因为Python中json.loads返回的是一个字典。 `json_decode` 的第二个参数 $assoc 可用来指定反序列化的结果为数组。

文档：[http://php.net/manual/zh/function.json-decode.php](http://php.net/manual/zh/function.json-decode.php)

------

#### 数组序列化

Python党初学PHP，可能类比于Python的列表和字典，认为PHP中明确区分索引数组和关联数组。但：

> PHP 实际并不区分索引数组和关联数组，都是一种有序映射。

虽然很多时候索引数组和关联数组在表现上是不一样的，比如对以下两个数组进行序列化：

```php
<?php
$arrA = array('a', 'b', 'c');
echo json_encode($arrA) . "\n";

$arrB = array('a' => 1, 'b' => 2, 'c' => 3);
echo json_encode($arrB) . "\n";
```

结果为：

```
["a","b","c"]
{"a":1,"b":2,"c":3}
```

如果把序列化的结果作为JSON输出到前端，对于JS来说，是两种不同的数据结构：数组和对象。

其中 `$arrA` 的初始化值是 `array(0 => 'a', 1 => 'b', 2 => 'c')` 的简写方式。

再来看另一段程序：

```php
$arrA = array('a', 'b', 'c');
echo json_encode($arrA) . "\n";

$arrA = array(0 => 'a', 1 => 'b', 2 => 'c');
echo json_encode($arrA) . "\n";

$arrA = array(1 => 'a', 2 => 'b', 3 => 'c');
echo json_encode($arrA) . "\n";

$arrA = array(0 => 'a', 2 => 'b', 3 => 'c');
echo json_encode($arrA) . "\n";
```

输出为：

```
["a","b","c"]
["a","b","c"]
{"1":"a","2":"b","3":"c"}
{"0":"a","2":"b","3":"c"}
```

从输出可以知道：仅当数组的key是从0开始的整数，并且key连续不间断，对其序列化的结果才是JS中的数组，也就是通常认为的PHP索引数组。

这个坑可能在某些时候不小心就掉进去了，比如我曾对一个索引数组应用array_filter函数操作，然后json_encode序列化输出到前端，认为前端反序列化出来的是一个数组，没想到却是个对象。

函数`array_filter`的文档说明：

> array array_filter ( array $input [, callable $callback = "" ] )
> 
> 依次将 input 数组中的每个值传递到 callback 函数。如果 callback 函数返回 TRUE，则 input 数组的当前值会被包含在返回的结果数组中。数组的键名保留不变。

注意是对值进行filter，结果中值原本对应的key不变，而不是使用新的key。

文档：[http://php.net/manual/zh/language.types.array.php](http://php.net/manual/zh/language.types.array.php)，[http://php.net/manual/zh/function.array-filter.php](http://php.net/manual/zh/function.array-filter.php)

#### 引用传递

先来看一段代码：

```php
<?php
class CommonUtils {
    static $TASK_INTERVAL_SEMANTIC_INT_MAPPER = array(
        'PER_DAY' => 86400,
        'TWO_DAY' => 172800,
        'PER_WEEK' => 604800,
        'TWO_WEEK' => 1209600,
        'PER_MONTH' => 2592000,
    );
}
$ha = array_pop(array_keys(CommonUtils::$TASK_INTERVAL_SEMANTIC_INT_MAPPER));
var_dump($ha);
```

在 `error_reporting = E_ALL` 时，上面的代码会抛出一个严格模式错误：` Only variables should be passed by reference` 。这是为什么呢？

[PHP文档](http://php.net/manual/zh/language.references.pass.php)中说明只有三种内容可以通过引用传递：

- 变量，例如 foo($a)
- New 语句，例如 foo(new foobar())
- 从函数中返回的引用，例如：

```
<?php
function &bar()
{
    $a = 5;
    return $a;
}
foo(bar());
?>
```

**任何其它表达式都不能通过引用传递，结果未定义。**

上面代码中 `$ha = array_pop(array_keys(CommonUtils::$TASK_INTERVAL_SEMANTIC_INT_MAPPER));` 一行，调用了 `array_pop` 和 `array_keys`，`array_pop` 的函数签名为：`mixed array_pop ( array &$array )` ，但 `array_keys` 函数调用返回的是一个array值，不属于上面列出三种内容，所以会抛错。但 **这个情况下这种错误** 的级别不同版本的PHP也不一样：

- 自 PHP 5.0.5 起导致致命错误
- 自 PHP 5.1.1 起导致严格模式错误
- 自 PHP 7.0 起导致 notice 信息

但如果直接给 `array_pop` 传递一个数组值，则会导致致命错误，如：

```
<?php
array_pop(array(1, 2, 3, 4));
```

会抛出错误：

```
PHP Fatal error:  Only variables can be passed by reference in /Users/xiayf/test.php on line 2
```

文档：[http://php.net/manual/zh/language.references.php](http://php.net/manual/zh/language.references.php)