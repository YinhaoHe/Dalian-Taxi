$(document).ready(function () {

    function make_danger(msg) {
        return $('<div class="alert alert-danger fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + msg + '</div>');
    }

    $(function () {
        /*仿刷新：检测是否存在cookie*/
        var $btn_get_code = $('#get-code');
        if ($.cookie("captcha")) {
            var count = $.cookie("captcha");

            $btn_get_code.val(count + '秒后可重新获取').attr('disabled', true);
            var resend = setInterval(function () {

                count--;
                if (count > 0) {
                    $btn_get_code.val(count + '秒后可重新获取').attr('disabled', true);
                    $.cookie("captcha", count, {path: '/', expires: (1 / 86400) * count});
                } else {
                    clearInterval(resend);
                    $btn_get_code.val("获取验证码").removeClass('disabled').removeAttr('disabled');
                }
            }, 1000);
        }else {
            $btn_get_code.val("获取验证码").removeClass('disabled').removeAttr('disabled');
        }

        /*点击改变按钮状态*/
        $btn_get_code.click(function () {



            var phone = $('input[name="phone"]').val();
            var reg = /^\d{11}$/;
            if(!reg.test(phone)){
                tip = make_danger('手机号应为11位数字');
                $('div.tip').html(tip);
                return;
            }

            var post_data ={
                phone: phone
            };
            $.post('/register/get-code',post_data, function (data) {

                if (data[0] === "true") {

                } else {

                    var errmsg = data[1];

                    if (errmsg === 'need_phone') {
                        tip = make_danger('手机号未填写')
                    }else if (errmsg === 'phone_format_error'){
                        tip = make_danger('手机号格式错误')
                    }else if (errmsg === 'send_fail'){
                        tip = make_danger('验证码发送失败')
                    }else if (errmsg === 'db_connect_error'){
                        tip = make_danger('数据库连接错误,请联系管理员')
                    }else if (errmsg === 'please_wait'){
                        tip = make_danger('操作过于频繁，请稍后再试')
                    }else if (errmsg === 'unknown'){
                        tip = make_danger('未知错误')
                    } else {
                        tip = make_danger('登录失败,错误信息读取失败')
                    }

                    $('div.tip').html(tip);
                }


            }, 'json');

            var count = 60;
            var resend = setInterval(function () {
                count--;
                if (count > 0) {
                    $btn_get_code.val(count + "秒后可重新获取");
                    $.cookie("captcha", count, {path: '/', expires: (1 / 86400) * count});
                } else {
                    clearInterval(resend);
                    $btn_get_code.val("获取验证码").removeAttr('disabled');
                }
            }, 1000);
            $btn_get_code.attr('disabled', true);
        });
    });






    $('.form-login')
        .bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            fields: {
                phone: {
                    validators: {
                        notEmpty: {
                            message: '请输入手机号'
                        },
                        stringLength: {
                            min: 11,
                            max: 11,
                            message: '手机号长度应为11位数字'
                        }
                    }
                },
                password: {
                    validators: {
                        notEmpty: {
                            message: '请输入密码'
                        },
                        stringLength: {
                            min: 6,
                            max: 25,
                            message: '密码应为6-25位'
                        }
                    }
                },
                confirm_password:{
                    validators: {
                        notEmpty: {
                            message: '请输入确认密码'
                        },
                        identical: {
                            field: 'password',
                            message: '两次输入的密码不一致'
                        }
                    }
                },
                code:{
                    validators: {
                        notEmpty: {
                            message: '请输入验证码'
                        }
                    }
                }

            }
        })//下面必须重写表单，因为bootstrapValidator靠这个来识别提交事件
        .on('success.form.bv', function (e) {

            e.preventDefault();
            var form = $(e.target);

            $.post(form.prop('action'), form.serialize(), function (data) {

                if (data[0] === "true") {
                    tip = make_danger('注册成功，去登录吧')
                    $('.form-group input').val('');
                } else {

                    var errmsg = data[1];

                    if (errmsg === 'need_phone') {
                        tip = make_danger('手机号未填写')
                    }else if (errmsg === 'phone_format_error'){
                        tip = make_danger('手机号格式错误')
                    }else if (errmsg === 'need_phone_code'){
                        tip = make_danger('手机验证码未填写')
                    }else if (errmsg === 'phone_code_format_error'){
                        tip = make_danger('手机号验证码格式错误')
                    }else if (errmsg === 'did_not_get_phone_code'){
                        tip = make_danger('验证码无效')
                    }else if (errmsg === 'phone_code_not_correct'){
                        tip = make_danger('验证码无效')
                    }else if (errmsg === 'please_wait'){
                        tip = make_danger('操作过于频繁，请稍后再试')
                    }else if (errmsg === 'phone_already_exist'){
                        tip = make_danger('该手机号已注册过，请勿重复注册')
                    }else if (errmsg === 'db_connect_error'){
                        tip = make_danger('数据库连接错误,请联系管理员')
                    }else if (errmsg === 'unknown'){
                        tip = make_danger('未知错误')
                    } else {
                        tip = make_danger('操作失败,错误信息读取失败')
                    }


                }
                form.children('.tip').html(tip);


            }, 'json');

        });
});

