Title: 应用MySQL InnoDB全文索引
Date: 2016-06-11
Author: youngsterxyf
Slug: mysql-fulltext-application
Tags: MySQL, 笔记


## 问题

之前涉及的一项工作要求对某些数据做全文索引，并以API向其他内部系统提供搜索查询服务。

由于需要建全文索引的数据量并不大，且已有的数据都以InnoDB引擎存储，简单起见，我们选择MySQL InnoDB引擎的全文索引特性来实现。MySQL从版本5.6开始支持InnoDB引擎的全文索引，不过“从5.7.6版本开始才提供一种内建的全文索引ngram parser，支持CJK字符集（中文、日文、韩文，CJK有个共同点就是单词不像英语习惯那样根据空格进行分解的，因此传统的内建分词方式无法准确的对类似中文进行分词）”，我们使用的MySQL版本为5.6.28，并且需要建全文索引的数据部分是中文，所以这是个问题。

## 方案

我们先把这项工作按“分治”的思想拆分成几个小问题：

1. 由于版本5.6.28的MySQL不支持中文的全文索引，那么可以对需要建全文索引的数据进行预处理 - 分词，并以空格为间隔将分词结果拼接成一个字符串。
2. 但经过第1步仍是不够的 - MySQL的系统变量`ft_min_word_len`、`ft_max_word_len`分别规定了全文检索被编入索引单词的最小长度和最大长度，默认的最小值为4个字符，默认的最大值取决于使用的MySQL版本。为了不改变这个默认值同时也是兼考虑这个值对于英文的意义，则需要通过编码（`urlencode`、`base64`、`汉字转拼音`等）将中文词变长。将经过编码后的分词结果存入建全文索引的数据表字段。
3. API调用时，也对搜索关键词做1、2步处理，然后使用SQL的全文索引匹配语法进行查询。

对于第1步，我们选择公司内部的分词服务，当然也可以选择一些开源的分词方案，如：结巴中文分词、SCWS分词等。

对于第2步，我们选择urlencode编码，并过滤掉编码后的`%`，因为它也是分界符。

## 举个栗子

假设已有一个数据表`apps`，其有个字段`name`，需要对这个字段做基于全文索引的查询。

为了不变更已有数据，我们对该数据表新增一个字段`seg_name`，使用脚本批量地对`name`字段进行分词编码，将结果存入该字段。

```sql
ALTER TABLE `apps` ADD COLUMN `seg_name` VARCHAR(1024) DEFAULT NULL COMMENT 'name字段分词编码后的结果';
ALTER TABLE `apps` ADD FULLTEXT INDEX (`seg_name`);
```

API中对搜索关键词也进行分词并经编码，以下面的SQL来查询即可：

```sql
# 其中%s用搜索关键词分词编码后的结果进行替换
SELECT * FROM `apps` WHERE MATCH (seg_name) AGAINST ('%s' IN NATURAL LANGUAGE MODE);
```

可以看到我们选择了“	自然语言模式（IN NATURAL LANGUAGE MODE），即通过MATCH AGAINST传递某个特定的字符串来进行检索”。

## 参考资料

- [MySQL · 引擎特性 · InnoDB 全文索引简介](http://mysql.taobao.org/monthly/2015/10/01/)
- [MySQL中文全文检索demoSQL](http://www.cnblogs.com/martinzhang/p/3220345.html)