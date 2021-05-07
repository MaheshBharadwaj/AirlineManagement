import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()
# cur.execute('insert into user(id, email, password, name) values(?, ?, ?, ?)',
#             ('1', 'admin', generate_password_hash('<set admin password here>'), 'admin'))
conn.commit()

print('Data')
cur.execute('SELECT * FROM User')
for row in cur:
    print(row)
conn.close()
