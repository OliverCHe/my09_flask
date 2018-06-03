function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    vue_comment_list = new Vue({
        el:".comment_list_con",
        delimiters:["[[", "]]"],
        data:{
            comment_list: []
        }
    });
    load_comment();

    // 收藏
    $(".collection").click(function () {
        $.post("/collect/" + $("#news_id").val(), {
            "csrf_token": $("#csrf_token").val(),
            "action": 1
        }, function (data) {
            if (data.result == 2){
                $('.login_btn').click();
            }
            else if(data.result == 3){
                $(".collected").show();
                $(".collection").hide();
            }
        })
       
    })

    // 取消收藏
    $(".collected").click(function () {
        $.post("/collect/" + $("#news_id").val(), {
            "csrf_token": $("#csrf_token").val(),
            "action": 2
        }, function (data) {

            if (data.result == 3){
                $(".collected").hide();
                $(".collection").show();
            }
        })
     
    })

        // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();

        $.post("/comment/add", {
            "csrf_token": $("#csrf_token").val(),
            "comment_content": $(".comment_input").val(),
            "news_id": $("#news_id").val()
        }, function (data) {
            if (data.result == 1){
                alert("请输入评论内容")
            }

            else if (data.result == 4){
                $(".comment_input").val('');
                $(".comment").text(data.comment_count);
                $(".comment_count span").text(data.comment_count);
                load_comment();
            }
        })

    })

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            var action = 1;
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                action = 2;
                // $this.removeClass('has_comment_up')
            }else {
                // $this.addClass('has_comment_up')
                action = 1;
            }

            $.post("/commentup/" + $this.attr("commentid"), {
                "action": action,
                "csrf_token": $("#csrf_token").val()
            }, function (data) {
                if(data.result == 3){
                    $('.login_btn').click();
                }
                else if(data.result == 1){
                    if(action==1){
                        $this.addClass('has_comment_up')
                    }

                    else if(action==2){
                        $this.removeClass('has_comment_up')
                    }
                    $this.find('em').text(data.nice_count)
                }
            })

        }

        if(sHandler.indexOf('reply_sub')>=0)
        {
            var $this = $(this);
            $.post("/commentback/" + $this.attr('commentid'), {
                "comment_content": $this.prev().val(),
                "news_id": $("#news_id").val(),
                "csrf_token": $("#csrf_token").val()
            }, function (data) {
                if(data.result == 2){
                    alert("请填写评论回复")
                }
                else if(data.result == 3){
                    $('.login_btn').click();
                }
                else if(data.result == 1){
                    load_comment();
                    $this.prev().val('');
                    $this.parent().hide();
                }
            })
        }
    })

        // 关注当前新闻作者
    $(".focus").click(function () {

    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    });
})


function load_comment() {
    $.get("/comment/list/" + $("#news_id").val(), function (data) {
        if(data.result == 2){
            vue_comment_list.comment_list = data.comment_list
        }
    })
}