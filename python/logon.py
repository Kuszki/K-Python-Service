from mysql.connector import connect

from datetime import datetime, timedelta
from hashlib import sha256
from threading import RLock

import uuid, ssl, sys, os

class httpLogon:

	STR_ERROR_PASSWD = "Wprowadzono błędną nazwę użytkownika lub hasło"
	STR_ERROR_MULTI  = "Wybrany użytkownik jest już zalogowany do systemu"
	STR_ERROR_NOTLOG = "Użytkownik nie jest zalogowany"
	STR_ERROR_OTHER  = "Wystąpił nieoczekiwany błąd"

	STR_SUCCESS_LOGIN  = "Zalogowano do systemu"
	STR_SUCCESS_LOGOUT = "Wylogowano z systemu"

	def __init__(self, dbconf):

		self.timeout = timedelta(minutes = 5)
		self.database = connect(**dbconf)
		self.locker = RLock()
		self.sessions = dict()

	def validate(self, user, uid, addr):

		with self.locker:

			if not user in self.sessions: return False
			else:
				session = self.sessions[user]
				now = datetime.now()

			if session["time"] + self.timeout < now:
				del self.sessions[user]
				return False

			if addr != session["addr"]: return False
			elif uid != session["uuid"]: return False
			else: session["time"] = now; return True

	def login(self, user, addr, passwd):

		with self.locker:

			now = datetime.now()

			if user in self.sessions:
				if self.sessions[user]["time"] + self.timeout < now: del self.sessions[user]
				else: raise Exception(403, self.STR_ERROR_MULTI)

			if type(passwd) == str: passwd = passwd.encode("utf-8")

			passwd = sha256(passwd).hexdigest()
			cur = self.database.cursor(buffered = True)

			try:
				query = "SELECT id FROM users WHERE name = %s AND pass = %s";
				cur.execute(query, (user, passwd))
				rows = cur.fetchall()

			except: raise Exception(403, self.STR_ERROR_OTHER)
			finally: cur.close()

			if len(rows) != 1: raise Exception(403, self.STR_ERROR_PASSWD)
			else: uid = str(uuid.uuid4())

			session = dict()
			session["uuid"] = uid
			session["addr"] = addr
			session["time"] = now

			self.sessions[user] = session

			return "text/plain", self.STR_SUCCESS_LOGIN, { "session": uid }

	def logout(self, user):

		with self.locker:

			try: del self.sessions[user]
			except: raise Exception(403, self.STR_ERROR_NOTLOG)
			else: return "text/plain", self.STR_SUCCESS_LOGOUT, { "session": "" }
