# decoding=utf-8
import psycopg2
import hashlib
import os

try:
    salt = os.urandom(24)
    password_db = hashlib.sha256('mstsss9g'+salt).hexdigest()

    conn = psycopg2.connect(database="dalianchuzu", user="postgres", password="postgres", host="127.0.0.1",
                            port="5432")
    cur = conn.cursor()
    cur.execute(u"insert into users(phone,password,salt,is_driver) values (%s,%s,%s,%s)",
                ('18969577872', password_db, salt, False))
    conn.commit()
except Exception, e:
    print Exception, ":", e
finally:
    cur.close()
    conn.close()
