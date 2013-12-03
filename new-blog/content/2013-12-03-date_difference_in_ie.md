Title: IE下JavaScript Date对象的不同之处
Date: 2013-12-03
Author: youngsterxyf
Tags: JavaScript, 笔记
Slug: date_difference_in_ie

之前在[仓库作业机器监控系统](http://youngsterxyf.github.io/2013/11/29/inner_warehouse_monitor_system/)项目中使用[HighCharts的时间序列数据图](http://www.highcharts.com/demo/line-time-series)来绘制机器CPU使用率、内存使用量、网络流量趋势变化图等，这些图在IE下却没有正常显示，IE也没有报错，按理说HighCharts的IE兼容性是较好的，不会出现这种问题，
最后查明原因---确实不是HighCharts的问题，而是由于IE下JavaScript的Date对象缺少一种构造函数导致的。

IE中JavaScript的Date对象不支持**时间字符串**作为参数的构造函数，仅有如下[三种构造函数](http://msdn.microsoft.com/zh-cn/library/ie/cd9w2te4.aspx)：

    :::text
    dateObj = new Date()
    dateObj = new Date(dateVal)
    dateObj = new Date(year, month, date[, hours[, minutes[, seconds[,ms]]]]) 

其他浏览器中除了这三种之外，[还有一种](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date):

    :::js
    dateObj = new Date(dateString);

如果在IE下使用了这种构造函数，IE不会提示错误，但在调用dateObj的getMonth、getDate等等方法时返回的是**NaN**，从而导致了其他问题。

------

在我的案例中，是需要将时间字符串“xxxx-xx-xx”（如“2013-12-03”）转换成一个Date对象，为了兼容IE，我如下实现：

    :::js
    function newIEDate(dateStr) {
        // dateStr的格式：xxxx-xx-xx
        var dateParts = dateStr.split("-");
        return new Date(parseInt(dateParts[0]), parseInt(dateParts[1])-1, parseInt(dateParts[2]));
    }
    ...
    var objDate;
    if ($.browser.msie) {
        objDate = newIEDate(queryDate);
    } else {
        objDate = new Date(queryDate);
    }
    
代码中，`$.browser.msie`来自jQuery。另外，构造函数`new Date(year, month, date[, hours[, minutes[, seconds[,ms]]]])`中的**year**必须是年份全称（如1998，而不应是98），**month**参数则应在0-11（代表1月至12月）之间取值。

#### 参考资料

- [MSDN - Date 对象 (JavaScript)](http://msdn.microsoft.com/zh-cn/library/ie/cd9w2te4.aspx)
- [MDN - Date](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)
