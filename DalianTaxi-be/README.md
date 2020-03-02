# dalianchuzu后台

## 接口

### 服务器基本信息

***服务器地址: qcloud.zhangzaizai.com***

***端口: 80***
***协议: HTTP***

### 最新版安卓客户端下载:
***url: /app/download***


### status为false时数据格式
```JSON
{
    "status": false,
    "msg": ""
}
```


### 登录:
***url: /api/user/login***

**param**
```JSON
{
    "phone": "18912345678",
    "password": "123456"
}
```

**return**
```JSON
{
    "status": true,
    "data": {
        "token": "f57eedd2a1d2446bb3baa29a50783c5c",
    }
}
```



### 订单搜索
***url: /api/order/search/before***

**param**
```JSON
{
    "order_id": 200,
    "num": 10,
    "order_id_init":20,
    "last_row_number":20,
}
```

**return**
```JSON
{
    "last_row_number":20,
    "data": [
        {
            "order_id": 1,
            "description": "红油鸡架",
            "launch_user_phone": "13567890123",
            "start_time": 1475251200000,
            "end_time": 1475251300000,
            "start_address": "食堂",
            "end_address": "综合楼四楼"
        }
    ]
}
```

***url: /api/order/search/after***
**param**
```JSON
{
    "order_id": 200,
}
```

**return**
```JSON
{
    "last_row_number":0,
    "data": [
        {
            "order_id": 1,
            "description": "红油鸡架",
            "launch_user_phone": "13567890123",
            "start_time": 1475251200000,
            "end_time": 1475251300000,
            "start_address": "食堂",
            "end_address": "综合楼四楼"
        }
    ]
}
```


### 待完成订单
***url***
***未完成的接单: /api/order/active***
司机只能接单,乘客只能发单,所以active是司机的接单
**param**
```
String token;
```

```JSON
{
    "status": true,
    "data": [
        {
            "order_id": 1,
            "description": "红油鸡架",
            "launch_user_phone": "13567890123",
            "take_user_phone": "13456789012",
            "start_time": 1475251200000,
            "end_time": 1475251300000,
            "state": 1,
            "start_address": "食堂",
            "end_address": "综合楼四楼"
        }
    ]
}
```

### 订单取消
***url: /api/order/cancel***

**param**
```
String token;
int order_id;
```

**return**
```JSON
{
    "status": true
}
```

### 接单
***url: /api/order/take***

**param**
```
String token;
int order_id;
```

**return**
```JSON
{
    "status": true
}
```

### 完成订单
***url: /api/order/confirm***

**param**
```
String token;
int order_id;
```

**return**
```JSON
{
    "status": true
}
```


### 获取订单状态
***url: /api/order/getstate***

***param***
```JSON
{
    "order_ids": [
        1,
        2
    ]
}
```

***return***
```JSON
{
    "status": true,
    "data": [
        {
            "order_id": 1,
            "state": 3,
            "launch_user_name": "abc",
            "launch_user_phone": "13456678040",
            "take_user_name": "c",
            "take_user_phone": "13567890234"
        }
    ]
}
```

### 获取订单种类信息
***url: /api/order/states***

**param** 无

**return**
```JSON
{
    "data": [
        {
            "id": 1,
            "name": "xxx"
        }
    ]
}
```


### 获取最大订单号
***url: /api/order/maxid***

**param** 无

**return**
```JSON
{
    "data": 10
}
```



* 注: 所有status为false时返回的msg内容规则如下:(String)
```
need_login 需要登录
wrong_old_pwd 旧密码错误
new_pwd_too_short 新密码过短（最少四位）
need_set_phone 需要绑定手机号
id_or_email_wrong 学号或邮箱错误
id_or_password_wrong 学号或密码错误
state_not_allowed 对应订单的状态不允许操作
user_not_proper 当前用户不允许操作该订单
self_not_allowed 不允许自己接单
no_proper_order 找不到对应的订单
phone_format 手机号格式不对
phone_exists 该手机号已被绑定
end_time 结束时间早于起始时间不被允许
price 价格为负不被允许
type 类型不存在不被允许
unknown 未知原因
not_in_white_list 不在内测白名单
```

*  注: 订单相关参数
```
int order_id; // 订单id
String launch_user_name; // 下单人
String launch_user_phone; // 接单人手机号
String take_user_name; // 接单人
String take_user_phone; // 接单人手机号
String operate_user_name; //最近此订单操作用户昵称
long operate_time; // 最近此订单操作时间
long start_time; // 开始时间
long end_time; // 失效时间
int type_id; // 订单类型id
String type_name; // 订单类型名
String description; // 订单描述
double price; // 订单价格
int state; // 订单状态
double start_latitude; //起始位置纬度
double start_longitude; //起始位置经度
double start_accuracy; // 起始位置精度
String start_address; // 起始位置地址
double end_latitude; // 终止位置纬度
double end_longitude; // 终止位置经度
double end_accuracy; // 终止位置精度
double end_address; // 终止位置地址
```

* 注: 订单状态码state
    1 待接单
    2 已接单
    3 已完成
    -1 已超时
    -2 发单者已取消



* 注: status返回值为布尔类型

* 注: 所有时间格式均为长整形, 大小为1970年1月1日 00:00:00时到指定时间的秒数

* 注: 所有页面方法均为POST

* 注: 请求参数数据类型错误或者必选数据不存在会返回404
