function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){

    var $pop = $('.pop_con');
    var $cancel = $('.cancel');
    var $confirm = $('.confirm');
    var $error = $('.error_tip');
    var $input = $('.input_txt3');
    var sHandler = 'edit';
    var sId = 0;

    vue_category_list = new Vue({
        el:".breadcrub",
        delimiters: ["[[", "]]"],
        data:{
            category_list : []
        },
        methods:{
            add:function () {
                sHandler = 'add';
                $pop.find('h3').html('新增分类');
                $input.val('');
                $pop.show();
            },

            edit:function (e) {
                // e 指的是event当前事件对象
                $this = $(e.target);
                sHandler = 'edit';
                sId = $this.parent().siblings().eq(0).html();
                $pop.find('h3').html('修改分类');
                $pop.find('.input_txt3').val($this.parent().prev().html());
                $pop.show();
            }
        }
    });

    get_category_list();



    // $a.click(function(){
    //     sHandler = 'edit';
    //     sId = $(this).parent().siblings().eq(0).html();
    //     $pop.find('h3').html('修改分类');
    //     $pop.find('.input_txt3').val($(this).parent().prev().html());
    //     $pop.show();
    // });
    //
    // $add.click(function(){
    //     sHandler = 'add';
    //     $pop.find('h3').html('新增分类');
    //     $input.val('');
    //     $pop.show();
    // });

    $cancel.click(function(){
        $pop.hide();
        $error.hide();
    });

    $input.click(function(){
        $error.hide();
    });

    $confirm.click(function(){
        if(sHandler=='edit')
        {
            var sVal = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            $.post('/admin/news_type_edit',{
                'csrf_token': $('#csrf_token').val(),
                'name': sVal,
                'id':sId
            },function (data) {
                if(data.result==1){
                    get_list();
                    $cancel.click();
                }else if(data.result==2){
                    $error.html('此名称已经存在').show();
                }
            });
        }
        else
        {
            var sVal = $input.val();
            if(sVal=='')
            {
                $error.html('输入框不能为空').show();
                return;
            }
            else{
                $.post("/admin/news_type_add", {
                    "csrf_token": $("#csrf_token").val(),
                    "name":sVal
                },function (data) {
                    if (data.result==2){
                        $error.text("该分类已存在");
                    }
                    else if(data.result==1){
                        get_category_list();
                        $cancel.click();
                    }
                })
            }
        }

    })
});

function get_category_list() {
    $.get("admin/news_type_list", function (data) {

        if(data.result==1){
            vue_category_list.category_list = data.category_list;
        }
    })
}