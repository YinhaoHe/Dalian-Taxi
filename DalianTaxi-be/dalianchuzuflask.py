# decoding=utf-8
# -*- coding: utf-8 -*-
import random

from flask import Flask, session, request, redirect, render_template, url_for, abort
import psycopg2
import sys
import hashlib
import os
import redis
import time
import datetime
import json
import top.api
import re

from psycopg2.pool import ThreadedConnectionPool

app = Flask(__name__)

reload(sys)
sys.setdefaultencoding("utf-8")

pg_pool = ThreadedConnectionPool(minconn=4, maxconn=100, database="dalianchuzu", user="postgres", password="postgres",
                                 host="127.0.0.1", port="5432")


@app.route('/', methods=['GET'])
def index():
    if 'token' not in session:
        return render_template('login.html')
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    user_id = r.get(session['token'])
    if user_id is None:
        return render_template('login.html')

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return render_template('main.html', model="[]")
        cur = conn.cursor()
        cur.execute(
            "SELECT start_address,end_address,start_time,end_time,description,state,take_user_id,id FROM orders where launch_user_id = %s and state in (1,2) and now() < end_time ORDER BY id ASC",
            (user_id,))
        rows = cur.fetchall()  # all rows in table

        active_orders = []
        for row in rows:
            order = {}
            order["start_address"] = row[0]
            order["end_address"] = row[1]
            order["start_time"] = int(time.mktime(row[2].timetuple()))  # int类型
            order["end_time"] = int(time.mktime(row[3].timetuple()))  # int类型
            order["description"] = row[4]
            order["state"] = row[5]  # int类型
            order["take_user_id"] = row[6]  # int类型或null
            order["order_id"] = row[7]
            active_orders.append(order)
        # 根据user_id查phone
        cur.execute(
            "SELECT phone FROM users where id = %s",
            (user_id,))
        rows = cur.fetchall()  # all rows in table
        if len(rows) < 1:
            return render_template('main.html', model=json.dumps(active_orders))
        phone = rows[0][0]

        return render_template('main.html', model=json.dumps(active_orders), phone=phone)

    except Exception, e:
        print Exception, ":", e
        return render_template('main.html', model="")
    finally:
        cur.close()
        pg_pool.putconn(conn)

        # return 'Hello!' + user_id


# API
@app.route('/login', methods=['POST'])
def login():
    phone = request.form['phone'].encode(encoding='utf-8')
    password_user = request.form['password'].encode(encoding='utf-8')

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return '["false","db_connect_error"]'
        cur = conn.cursor()
        cur.execute(
            "SELECT password,salt,id FROM users where phone = %s", (phone,))
        rows = cur.fetchall()  # all rows in table

        if len(rows) < 1:
            # print phone
            # print password_user
            return '["false","user_not_exist"]'

        password_db = rows[0][0]
        salt = rows[0][1]
        user_id = rows[0][2]
        if hashlib.sha256(password_user + salt).hexdigest() == password_db:
            # 验证通过,生成并分发token
            token = os.urandom(24).encode('base-64')
            session.permanent = True
            # app.permanent_session_lifetime = datetime.timedelta(days=7) # 服务器redis中已经设了失效时间，此处不必
            session['token'] = token

            # 通过python操作redis缓存
            pool = redis.ConnectionPool(host='localhost', port=6379)
            r = redis.Redis(connection_pool=pool)
            r.set(token, str(user_id), ex=604800)
            return '["true"]'

        else:
            # 验证失败,密码错误
            # print hashlib.sha256(password_user + salt).hexdigest()
            # print password_db
            return '["false","wrong_password"]'

    except Exception, e:
        print Exception, ":", e
        return '["false","unknown"]'
    finally:
        cur.close()
        pg_pool.putconn(conn)


@app.route('/logout')
def logout():
    if 'token' in session:
        # remove the phone from the session if it's there
        pool = redis.ConnectionPool(host='localhost', port=6379)
        r = redis.Redis(connection_pool=pool)
        r.delete(session['token'])
        session.pop('token', None)

    return redirect(url_for('index'))


@app.route('/register/do', methods=['POST'])
def register_do():
    phone = request.form['phone'].encode(encoding='utf-8')
    code = request.form['code'].encode(encoding='utf-8')

    if phone is None or phone == "":
        return '["false","need_phone"]'

    if not re.match(r"^\d{11}$", phone, re.M | re.I):
        return '["false","phone_format_error"]'

    if code is None or phone == "":
        return '["false","need_phone_code"]'

    if not re.match(r"^\d{6}$", code, re.M | re.I):
        return '["false","phone_code_format_error"]'

    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    rand_code = r.get("dalianchuzu.phone_code." + phone)


    if rand_code is None:
        return '["false","did_not_get_phone_code"]'
    if rand_code != code:
        return '["false","phone_code_not_correct"]'


    password_user = request.form['password'].encode(encoding='utf-8')

    try:
        salt = os.urandom(24)
        password_db = hashlib.sha256(password_user + salt).hexdigest()

        conn = pg_pool.getconn()
        if conn is None:
            return '["false","db_connect_error"]'
        cur = conn.cursor()
        cur.execute(u"insert into users(phone,password,salt,is_driver) values (%s,%s,%s,%s)",
                    (phone, password_db, salt, False))
        conn.commit()

        # # 生成并分发token
        # token = os.urandom(24).encode('base-64')
        # session['token'] = token
        #
        # # 通过python操作redis缓存
        # r.set(token, str(user_id), ex=604800)
        return '["true"]'

    except Exception, e:
        if "duplicate key value" in str(e) and "uq_phone" in str(e):
            return '["false","phone_already_exist"]'

        print Exception, ":", e
        return '["false","unknown"]'
    finally:
        cur.close()
        pg_pool.putconn(conn)


@app.route('/register/get-code', methods=['POST'])
def get_code():
    phone = request.form['phone'].encode(encoding='utf-8')
    if phone is None or phone == "":
        return '["false","need_phone"]'

    if not re.match(r"^\d{11}$", phone, re.M | re.I):
        return '["false","phone_format_error"]'

    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    phone_code_time = r.get("dalianchuzu.phone_code_time." + phone)

    if phone_code_time is not None and int(time.time()) - int(phone_code_time) < 60:
        return '["false","please_wait"]'

    appkey = 23689114
    secret = "efd12ea0c5875a0c7be607637a4e2789"

    req = top.api.AlibabaAliqinFcSmsNumSendRequest()
    req.set_app_info(top.appinfo(appkey, secret))

    req.format = "json"
    req.sms_type = "normal"
    req.sms_free_sign_name = "个人测试"
    rand_code = str(random.randrange(100000, 1000000))
    req.sms_param = json.dumps({
        "code": rand_code
    })
    req.rec_num = phone
    req.sms_template_code = "SMS_53225241"
    try:
        resp = req.getResponse()
        print("send_message_success:" + phone)
        print(resp)

        r.set("dalianchuzu.phone_code." + phone, rand_code, ex=600)
        r.set("dalianchuzu.phone_code_time." + phone, int(time.time()), ex=600)

        return '["true"]'
    except Exception, e:
        print (e)
        return '["false","send_fail"]'


# API
# need token
@app.route('/launch', methods=['POST'])
def launch():
    if 'token' not in session:
        return '["false","not_login"]'
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    user_id = r.get(session['token'])
    if user_id is None:
        return '["false","not_login"]'

    start_address = request.form['start_address'].encode(encoding='utf-8')
    end_address = request.form['end_address'].encode(encoding='utf-8')
    description = request.form['description'].encode(encoding='utf-8')
    try:
        start_time_int = int(request.form['start_time'])
        end_time_int = int(request.form['end_time'])
        if start_time_int > end_time_int:
            return '["false","start_time later than end_time"]'
    except ValueError, e:
        return '["false","time_error"]'

    if start_address is None or start_address == "" or len(start_address) > 50:
        return '["false","start_address_error"]'
    if end_address is None or end_address == "" or len(end_address) > 50:
        return '["false","end_address_error"]'
    if description is None or description == "" or len(description) > 130:
        return '["false","description_error"]'

    start_time = datetime.datetime.fromtimestamp(start_time_int)
    end_time = datetime.datetime.fromtimestamp(end_time_int)

    state = 1

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return '["false","db_connect_error"]'
        cur = conn.cursor()
        cur.execute(
            u"insert into orders(launch_user_id,start_address,end_address,start_time,end_time,description,state) values (%s,%s,%s,%s,%s,%s,%s)",
            (user_id, start_address, end_address, start_time, end_time, description, state))
        conn.commit()
        return '["true"]'
    except Exception, e:
        print Exception, ":", e
        return '["false","unknown"]'
    finally:
        cur.close()
        pg_pool.putconn(conn)


# API
# need token
@app.route('/order_cancel', methods=['POST'])
def cancel():
    if 'token' not in session:
        return '["false","not_login"]'
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    user_id = r.get(session['token'])
    if user_id is None:
        return '["false","not_login"]'

    try:
        order_id = int(request.form['order_id'].encode(encoding='utf-8'))
    except ValueError, e:
        return '["false","order_id_error"]'

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return '["false","db_connect_error"]'
        cur = conn.cursor()
        cur.execute(
            "SELECT state FROM orders where id = %s and launch_user_id = %s", (order_id, user_id))
        rows = cur.fetchall()  # all rows in table

        if len(rows) < 1:
            return '["false","user_not_allowed"]'

        state = rows[0][0]
        if state != 1 and state != 2:
            return '["false","state_not_allowed"]'

        cur.execute(
            u"update orders set state = -2 where id = %s", (order_id,))
        conn.commit()
        return '["true"]'

    except Exception, e:
        print Exception, ":", e
        return '["false","unknown"]'
    finally:
        cur.close()
        pg_pool.putconn(conn)


def make_status_false(msg):
    return json.dumps({
        "status": False,
        "msg": msg
    })


# mobile
# API
@app.route('/api/user/login', methods=['POST'])
def api_login():
    phone = request.form['phone'].encode(encoding='utf-8')
    password_user = request.form['password'].encode(encoding='utf-8')

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "SELECT password,salt,id,is_driver FROM users where phone = %s", (phone,))
        rows = cur.fetchall()  # all rows in table

        if len(rows) < 1:
            return make_status_false("user_not_exist")

        password_db = rows[0][0]
        salt = rows[0][1]
        user_id = rows[0][2]
        is_driver = rows[0][3]

        if not is_driver:
            return make_status_false("user_not_allowed")

        if hashlib.sha256(password_user + salt).hexdigest() == password_db:
            print '1'
            # 验证通过,生成并分发token
            token = os.urandom(24).encode('base-64').replace('\n', '')
            # 解决redis里多出\n的问题

            # 通过python操作redis缓存
            pool = redis.ConnectionPool(host='localhost', port=6379)
            r = redis.Redis(connection_pool=pool)
            r.set(token, str(user_id), ex=604800)
            print '2'
            return json.dumps({
                "status": True,
                "data": {
                    "token": token,
                }
            })
            print '3'
        else:
            return make_status_false("wrong_password")

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


# mobile
# API
@app.route('/api/order/maxid', methods=['POST'])
def api_maxid():
    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM orders ORDER BY id DESC limit 1")
        rows = cur.fetchall()  # all rows in table

        if len(rows) < 1:
            return json.dumps({
                "data": 0
            })

        max_id = rows[0][0]
        return json.dumps({
            "data": max_id
        })

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


# mobile
# API
@app.route('/api/order/search/before', methods=['POST'])
def api_order_search_before():
    try:
        order_id = int(request.form['order_id'].encode(encoding='utf-8'))
        order_id_init = int(request.form['order_id_init'].encode(encoding='utf-8'))
        num = int(request.form['num'].encode(encoding='utf-8'))
        last_row_number = int(request.form['last_row_number'].encode(encoding='utf-8'))
    except ValueError, e:
        return make_status_false("format_error")

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "select * from (select row_number() over() as rn,full_state.id,pool_state.id as id_pool,pool_state.state,pool_state.start_time,pool_state.end_time,pool_state.description,pool_state.start_address,pool_state.end_address,users_launch.phone as launch_user_phone,users_take.phone as take_user_phone from orders as full_state left join orders as pool_state on (full_state.id = pool_state.id and pool_state.state = 1 and now() < pool_state.end_time) inner join users as users_launch on pool_state.launch_user_id = users_launch.id left join users as users_take on pool_state.take_user_id = users_take.id order by pool_state.start_time asc) as temp_1 where rn > %s and id_pool is not null and id_pool <= %s limit %s;",
            (last_row_number, order_id_init, num))
        rows = cur.fetchall()  # all rows in table

        last_row_number_new = 0

        orders = []
        for row in rows:
            order = {}
            order["order_id"] = row[1]
            # order["state"] = row[3]  # int类型
            order["start_time"] = int(time.mktime(row[4].timetuple()) * 1000)  # int类型
            order["end_time"] = int(time.mktime(row[5].timetuple()) * 1000)  # int类型
            order["description"] = row[6]
            order["start_address"] = row[7]
            order["end_address"] = row[8]
            order["launch_user_phone"] = row[9]
            order["take_user_phone"] = row[10]  # int类型或null
            orders.append(order)
            last_row_number_new = row[0]

        return json.dumps({
            "status": True,
            "data": orders,
            "last_row_number": last_row_number_new
        })

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


# mobile
# API
@app.route('/api/order/search/after', methods=['POST'])
def api_order_search_after():
    try:
        order_id = int(request.form['order_id'].encode(encoding='utf-8'))
    except ValueError, e:
        return make_status_false("format_error")

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "select orders.id,state,start_time,end_time,description,start_address,end_address,users_launch.phone as launch_user_phone,users_take.phone as take_user_phone from orders inner join users as users_launch on orders.launch_user_id = users_launch.id left join users as users_take on orders.take_user_id = users_take.id where orders.state = 1 and orders.id > %s and now() < end_time order by orders.start_time asc;",
            (order_id,))
        rows = cur.fetchall()  # all rows in table

        last_row_number_new = 0

        orders = []
        for row in rows:
            order = {}
            order["order_id"] = row[0]
            # order["state"] = row[1]  # int类型
            order["start_time"] = int(time.mktime(row[2].timetuple()) * 1000)  # int类型
            order["end_time"] = int(time.mktime(row[3].timetuple()) * 1000)  # int类型
            order["description"] = row[4]
            order["start_address"] = row[5]
            order["end_address"] = row[6]
            order["launch_user_phone"] = row[7]
            order["take_user_phone"] = row[8]  # int类型或null
            orders.append(order)

        return json.dumps({
            "status": True,
            "data": orders,
            "last_row_number": last_row_number_new
        })

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


# mobile
# API
@app.route('/api/order/states', methods=['POST'])
def api_order_states():
    return json.dumps({
        "data": [
            {
                "id": 1,
                "name": u"待接单"
            },
            {
                "id": 2,
                "name": u"已接单"
            },
            {
                "id": 3,
                "name": u"已完成"
            },
            {
                "id": -1,
                "name": u"已超时"
            },
            {
                "id": -1,
                "name": u"发单者已取消"
            }
        ]
    })


# mobile
# API
# token
@app.route('/api/order/active', methods=['POST'])
def api_order_active():
    if 'token' not in request.form:
        return make_status_false("need_token")
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    user_id = r.get(request.form['token'])
    if user_id is None:
        return make_status_false("need_login")

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "select orders.id,state,start_time,end_time,description,start_address,end_address,users_launch.phone as launch_user_phone,users_take.phone as take_user_phone from orders inner join users as users_launch on orders.launch_user_id = users_launch.id inner join users as users_take on (orders.take_user_id = %s and orders.take_user_id = users_take.id) where orders.state = 2 order by orders.start_time asc;",
            (user_id,))
        rows = cur.fetchall()  # all rows in table

        orders = []
        for row in rows:
            order = {}
            order["order_id"] = row[0]
            order["state"] = row[1]  # int类型
            order["start_time"] = int(time.mktime(row[2].timetuple()) * 1000)  # int类型
            order["end_time"] = int(time.mktime(row[3].timetuple()) * 1000)  # int类型
            order["description"] = row[4]
            order["start_address"] = row[5]
            order["end_address"] = row[6]
            order["launch_user_phone"] = row[7]
            order["take_user_phone"] = row[8]  # int类型或null
            orders.append(order)

        return json.dumps({
            "status": True,
            "data": orders,
        })

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


# mobile
# API
# token
@app.route('/api/order/take', methods=['POST'])
def api_order_take():
    if 'token' not in request.form:
        return make_status_false("need_token")
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    user_id = r.get(request.form['token'])
    if user_id is None:
        return make_status_false("need_login")

    try:
        order_id = int(request.form['order_id'].encode(encoding='utf-8'))
    except ValueError, e:
        return make_status_false("format_error")

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "select state,launch_user_id from orders where id = %s",
            (order_id,))
        rows = cur.fetchall()  # all rows in table

        if len(rows) < 1:
            return make_status_false("no_proper_order")

        state = rows[0][0]
        launch_user_id = rows[0][1]

        if state != 1:
            return make_status_false("state_not_allowed")

        if launch_user_id == int(user_id):
            return make_status_false("self_not_allowed")

        cur.execute(
            "update orders set state = 2, take_user_id = %s where id = %s and now() < end_time",
            (user_id, order_id))
        conn.commit()

        return json.dumps({
            "status": True,
        })

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


# mobile
# API
# token
@app.route('/api/order/cancel', methods=['POST'])
def api_order_cancel():
    if 'token' not in request.form:
        return make_status_false("need_token")
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    user_id = r.get(request.form['token'])
    if user_id is None:
        return make_status_false("need_login")

    try:
        order_id = int(request.form['order_id'].encode(encoding='utf-8'))
    except ValueError, e:
        return make_status_false("format_error")

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "select state,take_user_id from orders where id = %s",
            (order_id,))
        rows = cur.fetchall()  # all rows in table

        if len(rows) < 1:
            return make_status_false("no_proper_order")

        state = rows[0][0]
        take_user_id = rows[0][1]

        if state != 2:
            return make_status_false("state_not_allowed")

        # 注意前方bug!从redis中取得的user_id是字符串,由于类型不一致,会被判为恒假
        if take_user_id != int(user_id):
            return make_status_false("user_not_proper")

        # 司机取消回订单池
        cur.execute(
            "update orders set state = 1, take_user_id = NULL where id = %s",
            (order_id,))
        conn.commit()

        return json.dumps({
            "status": True,
        })

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


# mobile
# API
# token
@app.route('/api/order/confirm', methods=['POST'])
def api_order_confirm():
    if 'token' not in request.form:
        return make_status_false("need_token")
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    user_id = r.get(request.form['token'])
    if user_id is None:
        return make_status_false("need_login")

    try:
        order_id = int(request.form['order_id'].encode(encoding='utf-8'))
    except ValueError, e:
        return make_status_false("format_error")

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "select state,take_user_id from orders where id = %s",
            (order_id,))
        rows = cur.fetchall()  # all rows in table

        if len(rows) < 1:
            return make_status_false("no_proper_order")

        state = rows[0][0]
        take_user_id = rows[0][1]

        if state != 2:
            return make_status_false("state_not_allowed")

        # 注意前方bug!从redis中取得的user_id是字符串,由于类型不一致,会被判为恒假
        if take_user_id != int(user_id):
            return make_status_false("user_not_proper")

        # 司机取消回订单池
        cur.execute(
            "update orders set state = 3, take_user_id = NULL where id = %s",
            (order_id,))
        conn.commit()

        return json.dumps({
            "status": True,
        })

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


# mobile
# API
# token
@app.route('/api/order/getstate', methods=['POST'])
def api_order_getstate():
    try:
        # order_ids是一个json数组
        order_ids = json.loads(request.form['order_ids'].encode(encoding='utf-8'))
    except ValueError, e:
        return make_status_false("format_error")

    try:
        conn = pg_pool.getconn()

        if conn is None:
            return make_status_false("db_connect_error")
        cur = conn.cursor()
        cur.execute(
            "select orders.id,state,users_launch.phone as launch_user_phone,users_take.phone as take_user_phone from orders inner join users as users_launch on orders.launch_user_id = users_launch.id left join users as users_take on orders.take_user_id = users_take.id where orders.id in (%s)" %
            (",".join(map(str, order_ids)),))
        rows = cur.fetchall()  # all rows in table

        orders = []
        for row in rows:
            order = {}
            order["order_id"] = row[0]
            order["state"] = row[1]  # int类型
            order["launch_user_phone"] = row[2]
            order["take_user_phone"] = row[3]  # int类型或null
            orders.append(order)

        return json.dumps({
            "status": True,
            "data": orders,
        })

    except Exception, e:
        print Exception, ":", e
        return make_status_false("unknown")
    finally:
        cur.close()
        pg_pool.putconn(conn)


app.secret_key = 'M(\x9a\xe1\xa7\xe6\xe5\xed/\x02FM\x82\xd8\xbd\xe9\x06\x83B\xa9=kb\xdb'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9090)
