from mysql.connector import connect
from threading import RLock

import ssl, sys, os, json, time

class fileSystem:

	STR_ERROR_OTHER  = "Wystąpił nieoczekiwany błąd"

	QUERY_GETDIRLIST = "SELECT id, path, number FROM dirlist";
	QUERY_GETFILELIST = "SELECT id, name, type, stat, date_cre, date_add, date_mod FROM doclist WHERE did = %s ORDER BY id LIMIT %s, %s"

	QUERY_GETDIRNUM = "SELECT COUNT(*) FROM paths"
	QUERY_GETFILENUM = "SELECT COUNT(*) FROM documents"
	QUERY_GETFILENUMIN = "SELECT COUNT(*) FROM documents WHERE path_id = %s"

	def __init__(self, root, dbconf):

		self.database = connect(**dbconf)
		self.locker = RLock()
		self.dbconf = dbconf
		self.root = root

	def getDirs(self):

		try:
			database = connect(**self.dbconf)
			cursor = database.cursor(buffered = True)
			cursor.execute(self.QUERY_GETDIRLIST)

		except: raise Exception(500, self.STR_ERROR_OTHER)
		else: return cursor.fetchall()
		finally:
			cursor.close()
			database.close()

	def getDirsNum(self):

		try:
			database = connect(**self.dbconf)
			cursor = database.cursor(buffered = True)
			cursor.execute(self.QUERY_GETDIRNUM)

		except: raise Exception(500, self.STR_ERROR_OTHER)
		else: return int(cur.fetchall()[0][0])
		finally:
			cursor.close()
			database.close()

	def getFiles(self, uid, page, count = 50):

		try:
			database = connect(**self.dbconf)
			cursor = database.cursor(buffered = True)
			cursor.execute(self.QUERY_GETFILELIST, (uid, count*page, count))

		except: raise Exception(500, self.STR_ERROR_OTHER)
		else: return cursor.fetchall()
		finally:
			cursor.close()
			database.close()

	def getFilesNum(self, uid):

		try:
			database = connect(**self.dbconf)
			cursor = database.cursor(buffered = True)

			if uid == None: cursor.execute(self.QUERY_GETFILENUM)
			else: cursor.execute(self.QUERY_GETFILENUMIN, (uid,))

		except: raise Exception(500, self.STR_ERROR_OTHER)
		else: return int(cursor.fetchall()[0][0])
		finally:
			cursor.close()
			database.close()

	def getList(self, params):

		try: page = int(params["page"][0])
		except: page = 0
		else: page = max(page - 1, 0)

		try: count = int(params["count"][0])
		except: count = 50

		try: uid = int(params["id"][0])
		except: uid = None

		if uid == None: return self.getDirs()
		else: return self.getFiles(uid, page, count)

	def getCount(self, params):

		try: uid = int(params["id"][0])
		except: uid = None
		finally: return self.getFilesNum(uid)

