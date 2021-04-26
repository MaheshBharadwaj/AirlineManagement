import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()
# cur.execute('insert into user(id, email, password, name) values(?, ?, ?, ?)',
#             ('1', 'admin', generate_password_hash('admin'), 'admin'))
# cur.execute('insert into user(id, email, password, name) values(?, ?, ?, ?)',
#             (2, 'test2@mail.com', '123', 'mahesh'))
# cur.execute('insert into user(id, email, password, name) values(?, ?, ?, ?)',
#             (3, 'test3@mail.com', '123', 'suresh'))

conn.commit()

print('Data')
cur.execute('SELECT * FROM User')
for row in cur:
    print(row)
conn.close()
