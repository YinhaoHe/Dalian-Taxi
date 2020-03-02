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
cur = conn.cursor()
cur.execute(
    "SELECT start_address,end_address,start_time,end_time,description,state,take_user_id FROM orders where launch_user_id = %s",
    (user_id,))
rows = cur.fetchall()  # all rows in table

print rows
