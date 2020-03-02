# -*- coding: utf-8 -*-
import top.api
import json

# url = "http://gw.api.taobao.com/router/rest"
# port = 80
from top.api.base import TopException

appkey = 23689114
secret = "efd12ea0c5875a0c7be607637a4e2789"

req = top.api.AlibabaAliqinFcSmsNumSendRequest()
req.set_app_info(top.appinfo(appkey, secret))

req.format = "json"
req.sms_type = "normal"
req.sms_free_sign_name = "个人测试"
req.sms_param = json.dumps({
    "code": '1000'
})
req.rec_num = "18969577872"
req.sms_template_code = "SMS_53225241"
try:
    resp = req.getResponse()
    print(resp)
except Exception, e:
    print (e)

# success response
# {u'alibaba_aliqin_fc_sms_num_send_response': {u'result': {u'model': u'106337561070^1108616946416', u'success': True, u'err_code': u'0'}, u'request_id': u'iv1eira3xlpo'}}