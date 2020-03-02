# decoding=utf-8
import psycopg2
import hashlib
import os

try:
    salt = os.urandom(24)
    password_db = hashlib.sha256('138895'+salt).hexdigest()
    print salt
    print password_db

    conn = psycopg2.connect(database="dalianchuzu", user="postgres", password="postgres", host="127.0.0.1",
                            port="5432")
    cur = conn.cursor()
    cur.execute(u"insert into users(phone,password,salt,is_driver) values (%s,%s,%s,%s)",
                ('13889578601', password_db, salt, True))
    conn.commit()
except Exception, e:
    print Exception, ":", e
finally:
    cur.close()
    conn.close()

#
# phone = '18969577872'
# try:
#     conn = psycopg2.connect(database="dalianchuzu", user="postgres", password="postgres", host="127.0.0.1",
#                             port="5432")
#
#     cur = conn.cursor()
#     cur.execute(
#         "SELECT password,salt FROM users where phone = %s", (phone,))
#     rows = cur.fetchall()  # all rows in table
#
#     password_db = rows[0][0]
#     salt = rows[0][1]
#
#     print salt
#     print password_db
#
#     print hashlib.sha256('mstsss9g'+salt).hexdigest()
#
# except Exception, e:
#     print Exception, ":", e
#
# finally:
#     cur.close()
#     conn.close()
