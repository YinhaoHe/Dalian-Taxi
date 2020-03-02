$(document).ready(function () {

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
                }
            }
        })//下面必须重写表单，因为bootstrapValidator靠这个来识别提交事件
        .on('success.form.bv', function (e) {

            e.preventDefault();
            var form = $(e.target);

            $.post(form.prop('action'), form.serialize(), function (data) {

                if (data[0] === "true") {
                    var redirectUrl = '/';
                    location.href = redirectUrl
                } else {

                    var errmsg = data[1];
                    function make_danger(msg) {
                        return $('<div class="alert alert-danger fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + msg + '</div>');
                    }

                    if (errmsg === 'wrong_password') {
                        tip = make_danger('密码错误')
                    }else if (errmsg === 'db_connect_error'){
                        tip = make_danger('数据库连接错误,请联系管理员')
                    }else if (errmsg === 'user_not_exist'){
                        tip = make_danger('您的手机号未注册,请先注册')
                    }else if (errmsg === 'unknown'){
                        tip = make_danger('未知错误')
                    } else {
                        tip = make_danger('登录失败,错误信息读取失败')
                    }

                    form.children('.tip').html(tip);
                    $('input[name="password"]').val('');

                }

            }, 'json');

        });

});