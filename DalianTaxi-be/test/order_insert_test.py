# decoding=utf-8
import psycopg2
import sys
import time
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")

conn = psycopg2.connect(database="dalianchuzu", user="postgres", password="postgres", host="127.0.0.1",
                                port="5432")

user_id = 2
start_address = u"大连理工大学软件学院生活区小门".encode(encoding='utf-8')
end_address = u"开发区万达".encode(encoding='utf-8')
start_time_int = 1483673400
end_time_int = 1483680600
state = 1

start_time = datetime.datetime.fromtimestamp(start_time_int)
# start_time1 = start_time_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
end_time = datetime.datetime.fromtimestamp(end_time_int)

description = u"这里是备注".encode(encoding='utf-8')
cur = conn.cursor()
cur.execute(
    u"insert into orders(launch_user_id,start_address,end_address,start_time,end_time,description,state) values (%s,%s,%s,%s,%s,%s,%s)",
    (user_id, start_address, end_address, start_time, end_time, description, state))
conn.commit()
