Title: 《HBase 参考指南》笔记
Date: 2019-08-16
Author: xiayf
Slug: hbase-book-notes
Tags: HBase, 笔记

> Column families physically colocate a set of columns and their values, often for performance reasons. Each column family has a set of storage properties, such as whether its values should be cached in memory, how its data is compressed or its row keys are encoded, and others. Each row in a table has the same column families, though a given row might not store anything in a given column family.
> Physically, all column family members are stored together on the filesystem. Because tunings and storage specifications are done at the column family level, it is advised that **all column family members have the same general access pattern and size characteristics**.

