Title: 关于我
Date: 2013-11-02
Author: youngsterxyf
Slug: aboutme

[个人简历](../assets/uploads/files/resume.pdf)


<div class="github-card" data-user="youngsterxyf"></div>
<script src="../assets/github-cards/widget.js"></script>


<div id="coderwall"></div>
<script type="text/javascript">
$(function() {
    var appendCoderwallBadge = function(){
        var coderwallJSONurl ="http://www.coderwall.com/youngsterxyf.json?callback=?"
          , size = 40
          ;

        $.getJSON(coderwallJSONurl, function(data) {
            $.each(data.data.badges, function(i, item){
                var a = $("<a>")
                    .attr("href", "http://www.coderwall.com/youngsterxyf/")
                    .attr("target", "_blank")
                    ;

                $("<img>").attr("src", item.badge)
                    .attr("float", "left")
                    .attr("title", item.name + ": " + item.description)
                    .attr("alt", item.name)
                    .attr("height", size)
                    .attr("width", size)
                    .hover(
                        function(){ $(this).css("opacity", "0.6"); }
                      , function(){ $(this).css("opacity", "1.0"); }
                    )
//                    .click( function(){ window.location = "http://www.coderwall.com/youngsterxyf/"; })
                    .appendTo(a)
                    ;
                $("#coderwall").append(a);
            });
        });
    };

    appendCoderwallBadge();
});
</script>
