/**
 * Created by Administrator on 2017/2/25.
 */

$(function () {
    $('#datetimepicker-from').datetimepicker({
        format: 'HH:mm',
        locale: 'zh-cn',
        ignoreReadonly: true
    });
    $('#datetimepicker-to').datetimepicker({
        format: 'HH:mm',
        locale: 'zh-cn',
        ignoreReadonly: true
    });
});



$(document).ready(function () {

    $('.form-launch')
        .bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            fields: {
                start_address: {
                    validators: {
                        notEmpty: {
                            message: '请输入出发地'
                        },
                        stringLength: {
                            min: 2,
                            max: 20,
                            message: '出发地应在2至20位之间'
                        }
                    }
                },
                end_address: {
                    validators: {
                        notEmpty: {
                            message: '请输入目的地'
                        },
                        stringLength: {
                            min: 2,
                            max: 20,
                            message: '目的地应在2至20位之间'
                        }
                    }
                },
                start_time: {
                    validators: {
                        notEmpty: {
                            message: '请输入订单时间'
                        },
                    }
                },
                end_time: {
                    validators: {
                        notEmpty: {
                            message: '请输入订单自动失效时间,超过这个时间未被接的订单将失效'
                        },
                        // callback: {
                        //     message: '时间不正确',
                        //     callback: function(value, validator) {
                        //         //如果校验失败  return false; 校验成功 return true;
                        //         var items = value.split(':');
                        //         return value == sum;
                        //     }
                        // }
                    }
                },
                description:{
                    validators: {
                        stringLength: {
                            max: 50,
                            message: '备注不能超过50字'
                        }
                    }
                }

            }
        })//下面必须重写表单，因为bootstrapValidator靠这个来识别提交事件
        .on('success.form.bv', function (e) {

            e.preventDefault();
            var form = $(e.target);

            var form_data = form.serializeArray();
            var start_time_raw = form_data[2]['value'];
            var end_time_raw = form_data[3]['value'];
            var now = new Date();
            var today = (now.getMonth()+1) +"/"+ now.getDate() +"/"+ now.getFullYear();
            var start_time_stamp = Date.parse(today + " "+ start_time_raw);
            var end_time_stamp = Date.parse(today + " "+ end_time_raw);
            form_data[2]['value'] = start_time_stamp/1000;
            form_data[3]['value'] = end_time_stamp/1000;

            $.post(form.prop('action'),form_data, function (data) {

                if (data[0] === "true") {
                    var redirectUrl = '/';
                    location.href = redirectUrl;
                    // $('input').val('');
                } else {

                    var errmsg = data[1];
                    function make_danger(msg) {
                        return $('<div class="alert alert-danger fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + msg + '</div>');
                    }

                    if (errmsg === 'not_login') {
                        tip = make_danger('您的登录状态已失效,请重新登录')
                    }else if (errmsg === 'db_connect_error'){
                        tip = make_danger('数据库连接错误,请联系管理员')
                    }else if (errmsg === 'time_error'){
                        tip = make_danger('时间参数不合法')
                    }else if (errmsg === 'start_address_error'){
                        tip = make_danger('出发地不合法')
                    }else if (errmsg === 'end_address_error'){
                        tip = make_danger('目的地不合法')
                    }else if (errmsg === 'description_error'){
                        tip = make_danger('备注不合法')
                    }else if (errmsg === 'start_time later than end_time'){
                        tip = make_danger('不允许订单时间迟于失效时间')
                    }else if (errmsg === 'unknown'){
                        tip = make_danger('未知错误')
                    } else {
                        tip = make_danger('登录失败,错误信息读取失败')
                    }

                    form.children('.tip').html(tip);
                }

            }, 'json');

        });

    $('.cardview-btn').bind('click',function () {
        $('.modal-title').text("取消订单");
        $('.modal-body p').text("你确定要取消这个订单?");
        $('#modal-negative-button').css('display','');
        $('#modal-positive-button').bind('click',function () {
            $('#modal-positive-button').unbind('click');
            var order_id = $('#order_id_val').text();

            var post_data = {
                order_id: order_id
            };

            $.post('/order_cancel',post_data, function (data) {

                if (data[0] === "true") {

                    $('.modal-title').text("成功");
                    $('.modal-body p').text("订单取消成功");
                    $('#modal-negative-button').css('display','none');
                    $('#modal-positive-button').bind('click',function () {
                        $('#modal-positive-button').unbind('click');
                        var redirectUrl = '/';
                        location.href = redirectUrl;
                    });
                    $('#myModal').modal('hide').queue(function () {
                        $('#myModal').modal('show');//弹出模态对话框
                    })



                    // $('input').val('');
                } else {

                    var errmsg = data[1];
                    var errhint;

                    if (errmsg === 'not_login') {
                        errhint = make_danger('您的登录状态已失效,请重新登录')
                    }else if (errmsg === 'db_connect_error'){
                        errhint = make_danger('数据库连接错误,请联系管理员')
                    }else if (errmsg === 'order_id_error'){
                        errhint = make_danger('订单参数不合法')
                    }else if (errmsg === 'user_not_allowed'){
                        errhint = make_danger('您的用户没有该权限')
                    }else if (errmsg === 'state_not_allowed'){
                        errhint = make_danger('当前订单状态不允许取消')
                    }else if (errmsg === 'unknown'){
                        errhint = make_danger('未知错误')
                    } else {
                        errhint = make_danger('登录失败,错误信息读取失败')
                    }


                    $('.modal-title').text("失败");
                    $('.modal-body p').text("订单取消失败,错误信息:" + errhint);
                    $('#modal-negative-button').css('display','none');
                    $('#myModal').modal('hide').queue(function () {
                        $('#myModal').modal('show');//弹出模态对话框
                    })

                }

            }, 'json');

        });
        $('#myModal').modal('show');//弹出模态对话框
    });

});