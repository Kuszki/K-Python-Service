from mysql.connector import connect
from threading import RLock

import ssl, sys, os, json

class fileSystem:

	STR_ERROR_OTHER  = "Wystąpił nieoczekiwany błąd"

	QUERY_GETDIRLIST = "SELECT id, path, number FROM dirlist";
	QUERY_GETFILELIST = "SELECT id, name, stat, date_cre, date_add, date_mod FROM doclist WHERE did = %s"

	def __init__(self, root, dbconf):

		self.root = root
		self.locker = RLock()
		self.database = connect(**dbconf)

	def getDirs(self):

		with self.locker:

			try:
				cur = self.database.cursor(buffered = True)
				cur.execute(self.QUERY_GETDIRLIST)

			except: raise Exception(500, self.STR_ERROR_OTHER)
			else: return cur.fetchall()
			finally: cur.close()

	def getFiles(self, uid):

		with self.locker:

			try:
				cur = self.database.cursor(buffered = True)
				cur.execute(self.QUERY_GETFILELIST, (uid,))

			except: raise #Exception(500, self.STR_ERROR_OTHER)
			else: return cur.fetchall()
			finally: print(cur.statement); cur.close()

	def getList(self, params):

		if not "id" in params: return self.getDirs()
		else: return self.getFiles(int(params["id"][0]))
