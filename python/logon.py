from mysql.connector import connect

from datetime import datetime, timedelta
from hashlib import sha256
from threading import RLock

import uuid, ssl, sys, os

class httpSession:

	def __init__(self, name, user, uid, addr, admin = False, timeout = 0):

		self.name = name
		self.dbid = user
		self.uuid = uid
		self.addr = addr
		self.admin = admin

		self.timeout = timedelta(minutes = 5) if timeout <= 0 else timedelta(minutes = timeout)
		self.time = datetime.now()

	def is_expired(self):

		return self.time + self.timeout < datetime.now()

	def is_admin(self):

		return self.admin and self.is_valid()

	def is_valid(self):

		return self.parent.validate(self.name, self.uuid, self.addr)

	def on_refresh(self):

		self.time = datetime.now()

	def get_expdate(self):

		return self.time + self.timeout

	def get_expsecs(self):

		return (self.get_expdate() - datetime.now()).seconds

class httpLogon:

	STR_ERROR_PASSWD = "Wprowadzono błędną nazwę użytkownika lub hasło"
	STR_ERROR_MULTI  = "Wybrany użytkownik jest już zalogowany do systemu"
	STR_ERROR_NOTLOG = "Użytkownik nie jest zalogowany"
	STR_ERROR_OTHER  = "Wystąpił nieoczekiwany błąd"

	STR_SUCCESS_LOGIN  = "Zalogowano do systemu"
	STR_SUCCESS_LOGOUT = "Wylogowano z systemu"

	QUERY_GETUSER = "SELECT id, admin, timeout FROM users WHERE name = %s AND pass = %s"

	def __init__(self, dbconf):

		self.database = connect(**dbconf, autocommit = True)
		self.timeout = timedelta(minutes = 5)
		self.locker = RLock()
		self.sessions = dict()

		httpSession.parent = self

	def session(self, user, uid, addr):

		with self.locker:

			try: obj = self.sessions[user]
			except: return None

			if obj.uuid == uid and obj.addr == addr:
				return obj

		return None


	def validate(self, user, uid, addr):

		if not user or not addr or not uid: return False

		with self.locker:

			if not user in self.sessions: return False
			else: session = self.sessions[user]

			if session.is_expired(): return False

			if addr != session.addr: return False
			elif uid != session.uuid: return False
			else: return True

	def login(self, user, addr, passwd):

		if not user or not addr or not passwd: raise Exception(403, self.STR_ERROR_PASSWD)

		with self.locker:

			if user in self.sessions:
				if self.sessions[user].is_expired(): del self.sessions[user]
				else: raise Exception(403, self.STR_ERROR_MULTI)

			if type(passwd) == str: passwd = passwd.encode("utf-8")

			try:
				pw = sha256(passwd).hexdigest()
				cur = self.database.cursor(buffered = True)
				cur.execute(self.QUERY_GETUSER, (user, pw))

			except: raise Exception(403, self.STR_ERROR_OTHER)
			else: rows = cur.fetchall()
			finally: cur.close()

			if len(rows) != 1: raise Exception(403, self.STR_ERROR_PASSWD)
			else:
				etime = int(rows[0][2])
				admin = bool(rows[0][1])
				dbid = int(rows[0][0])
				uid = str(uuid.uuid4())

			self.sessions[user] = httpSession(user, dbid, uid, addr, admin, etime)

			return "text/plain", self.STR_SUCCESS_LOGIN, { "session": uid }

	def logout(self, user):

		if not user: raise Exception(403, self.STR_ERROR_NOTLOG)

		with self.locker:

			try: del self.sessions[user]
			except: raise Exception(403, self.STR_ERROR_NOTLOG)
			else: return "text/plain", self.STR_SUCCESS_LOGOUT, { "session": "" }
