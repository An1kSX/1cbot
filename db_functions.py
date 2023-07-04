import sqlite3


db = sqlite3.connect('database.db', check_same_thread = False)
sql = db.cursor()





def new_user(user_id):
	sql.execute('SELECT * FROM users WHERE id = ?', (user_id, ))
	_user = sql.fetchone()
	if _user is None:
		sql.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (user_id, 'menu', 1, None, None, 0, None, None))
		db.commit()


def state_change(user_id, state):
	sql.execute('UPDATE users SET state = ? WHERE id = ?', (state, user_id))
	db.commit()


def state_get(user_id):
	sql.execute('SELECT state FROM users WHERE id = ?', (user_id, ))
	return sql.fetchone()[0]


def get_plea_num(user_id):
	sql.execute('SELECT plea_num FROM users WHERE id = ?', (user_id, ))
	return sql.fetchone()[0]


def increase_plea_num(user_id):
	sql.execute('SELECT plea_num FROM users WHERE id = ?', (user_id, ))
	_num = sql.fetchone()[0]
	sql.execute('UPDATE users SET plea_num = ? WHERE id = ?', (_num+1, user_id))
	db.commit()


def set_mail(user_id, mail):
	sql.execute('UPDATE users SET mail = ? WHERE id = ?', (mail, user_id))
	db.commit()


def set_phone_number(user_id, phone_number):
	sql.execute('UPDATE users SET phone_number = ? WHERE id = ?', (phone_number.replace('998', '').replace('+', ''), user_id))
	db.commit()


def clear_number(user_id):
	sql.execute('UPDATE users SET phone_number = ? WHERE id = ?', (None, user_id))
	db.commit()


def get_phone_number(user_id):
	sql.execute('SELECT phone_number FROM users WHERE id = ?', (user_id, ))
	return sql.fetchone()[0]


def get_mail(user_id):
	sql.execute('SELECT mail FROM users WHERE id = ?', (user_id, ))
	return sql.fetchone()[0]


def authorize_user(user_id):
	sql.execute('UPDATE users SET authorized = 1 WHERE id = ?', (user_id, ))
	db.commit()

def is_authorized(user_id):
	sql.execute('SELECT authorized FROM users WHERE id = ?', (user_id, ))
	return sql.fetchone()[0]


def set_plea_type(user_id, type_):
	sql.execute('UPDATE users SET plea_type = ? WHERE id = ?', (type_, user_id))
	db.commit()


def set_plea_info(user_id, info):
	sql.execute('UPDATE users SET plea_info = ? WHERE id = ?', (info, user_id))
	db.commit()


def clear_plea_type_and_info(user_id):
	sql.execute('UPDATE users SET plea_info = ? WHERE id = ?', (None, user_id))
	db.commit()
	sql.execute('UPDATE users SET plea_type = ? WHERE id = ?', (None, user_id))
	db.commit()


def get_plea_info(user_id):
	sql.execute('SELECT plea_info FROM users WHERE id = ?', (user_id, ))
	return sql.fetchone()[0]


def get_plea_type(user_id):
	sql.execute('SELECT plea_type FROM users WHERE id = ?', (user_id, ))
	return sql.fetchone()[0]