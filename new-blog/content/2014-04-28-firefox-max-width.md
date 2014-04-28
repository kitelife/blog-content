Title: Firefox中“max-width:100%”不兼容问题
Date: 2014-04-28
Author: youngsterxyf
Slug: max-width-in-firefox
Tags: CSS, 浏览器兼容, JavaScript

这个博客是基于“[Pelican](http://docs.getpelican.com/en/3.3.0/) + [Markdown](http://wowubuntu.com/markdown/) +
[定制的my-gum主题](https://github.com/youngsterxyf/my-pelican-themes/tree/master/my-gum)”的。定制的主题将博文正文页面的
右边栏去掉，这导致在Firefox等浏览器中，正文中大的图片会突破正文块的宽度，高度也得不到限制，显示效果非常差。

其原因是：Markdown的[图片区块元素](http://wowubuntu.com/markdown/#img)`![Alt
text](/path/to/img.jpg)`渲染成HTML元素的结果为 -

    :::html
    <p>
        <img src="/path/to/img.jpg" alt="Alt text"></img>
    </p>

`<p>`元素内的元素是行内(inline)元素。主题my-gum使用的CSS框架[gumby](http://gumbyframework.com/)对img元素是使用`max-width:
100%`将图片的最大宽度限制为父元素的宽度。但[在Firefox中max-width对于行内元素并不会生效(all elements but non-replaced 
inline elements, table rows, and row
groups)](https://developer.mozilla.org/en-US/docs/Web/CSS/max-width)，所以造成了显示问题。

网络上有人说可以用`width: 100%`替代之，但`width: 100%`和`max-width: 100%`的区别是：`width: 100%`是将所有指定元素的宽度
拉伸或收缩到和父元素的宽度一致，而`max-width:
100%`则是如果指定元素的宽度不超过父元素的宽度，则大小不变，如果超过了父元素的宽度，则将宽度收缩为父元素的宽度。如果使用`width:
100%`，那么我博文中的图片，即使再小，都会被拉伸为正文的宽度，自然是不会好看的。

我的想法是：既然使用CSS不能解决这个问题，那就尝试使用Javascript。当图片加载完毕后，将图片宽度与正文宽度做比较，如果
图片宽度大于正文宽度，则为该图片设置`width: 100%`。唯一不完美的地方是某些大图片加载完毕之前的宽度很大，比较难看。

代码如下所示：

    :::javascript
    $(function() {
        var entryContentWidth = $('.row').width();

        $('.entry-content img').on('load', function(){
            if($(this).width() > entryContentWidth) {
                $(this).width('100%');
            }
        });
    });


### 参考资料

- [Image mysteriously ignoring max-width in Firefox & IE](http://stackoverflow.com/questions/14550356/image-mysteriously-ignoring-max-width-in-firefox-ie)
- [is <p\> a block-level or inline-level element?](http://stackoverflow.com/questions/2789727/is-p-a-block-level-or-inline-level-element)
- [MDN - max-width](https://developer.mozilla.org/en-US/docs/Web/CSS/max-width)
- [JQuery - load event](https://api.jquery.com/load-event/)
