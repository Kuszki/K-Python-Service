from http.server import BaseHTTPRequestHandler
from http.cookies import SimpleCookie

from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from pathlib import Path

import io, os, json, traceback, mimetypes, time

class httpRequest: pass

class httpHandler(BaseHTTPRequestHandler):

	STR_ERROR_DEFAULT = "Błąd podczas generowania zasobu"
	INT_ERROR_DEFAULT = 400

	STR_ERROR_403 = "Niedozwolona ścieżka"
	STR_ERROR_404 = "Brak wskazanego zasobu"
	STR_ERROR_405 = "Niedozwolona operacja"
	STR_ERROR_410 = "Zasób obecnie niedostępny"
	STR_ERROR_411 = "Nie podano długości zasobu"
	STR_ERROR_415 = "Niedozwolony typ zasobu"
	STR_ERROR_500 = "Wystąpił błąd po stronie serwera"

	def send_Text(self, code, mime, text, cok = None):

		if type(cok) != SimpleCookie: cok = SimpleCookie(cok)

		if type(text) == str: text = text.encode("utf-8")
		elif type(text) != bytes: text = str(text).encode("utf-8")

		self.send_response(code)
		self.send_header("Connection", "keep-alive")
		self.send_header("Content-Type", mime + "; charset=utf-8")
		self.send_header("Content-Length", len(text))

		for c in cok.values():
			self.send_header("Set-Cookie", c.output(header = ""))

		self.end_headers()
		self.wfile.write(text)

	def send_File(self, obj, mime = None, size = None, cok = None):

		if type(cok) != SimpleCookie: cok = SimpleCookie(cok)

		try:
			if mime == None: mime = mimetypes.guess_type(obj.name)[0]
			if size == None: size = os.path.getsize(obj.name)

		except:
			return self.send_Error(Exception(500, self.STR_ERROR_500, obj.name))

		self.send_response(200)
		self.send_header("Connection", "keep-alive")
		self.send_header("Content-Type", mime)
		self.send_header("Content-Length", size)

		for c in cok.values():
			self.send_header("Set-Cookie", c.output(header = ""))

		self.end_headers()

		while True:

			data = obj.read(10240)

			if not len(data): break
			else: self.wfile.write(data)

	def send_Slite(self, mime, obj, cok = None):

		if issubclass(type(obj), str): self.send_Text(200, mime, obj.encode("utf-8"), cok)
		elif issubclass(type(obj), io.IOBase): self.send_File(obj, mime, None, cok)
		else: self.send_Text(200, mime, obj, cok)

	def send_Error(self, exc, cok = None):

		print("send_Error: ", exc)
		print(traceback.format_exc())

		if len(exc.args) >= 2:
			try: code = int(exc.args[0])
			except: code = self.INT_ERROR_DEFAULT

			try: text = str(exc.args[1])
			except: text = self.STR_ERROR_DEFAULT

			try: path = str(exc.args[3])
			except: pass
			else: text = text + ": '" + path + "'"
		else:
			code = self.INT_ERROR_DEFAULT
			text = self.STR_ERROR_DEFAULT

		self.send_Text(code, "text/plain", text, cok)

	def get_Dir(self, path):

		for v in self.server.paths:
			for s in v["list"]:
				if path.endswith(s):
					return v["dir"]

		raise KeyError()

	def get_File(self, path):

		try: src = os.path.abspath(self.get_Dir(path))
		except: raise Exception(403, self.STR_ERROR_403, path)

		try: absp = Path(src + "/" + path).absolute()
		except: raise Exception(404, self.STR_ERROR_404, path)

		try: mime = mimetypes.guess_type(path)[0]
		except: mime = "text/plain"

		if not absp.is_file(): raise Exception(404, self.STR_ERROR_404, path)

		if absp.is_relative_to(src):
			try: dat = absp.open('rb')
			except: raise Exception(410, self.STR_ERROR_410, path)
			else: return mime, dat, None

		else: raise Exception(403, self.STR_ERROR_403, path)

	def get_Cname(self):

		try:
			subject = self.request.getpeercert()["subject"]
			return dict(x[0] for x in subject)["commonName"]

		except: return None

	def get_Info(self, req):

		info = httpRequest()
		info.addr = self.client_address[0]
		info.port = self.client_address[1]
		info.name = self.get_Cname()
		info.time = datetime.now()
		info.type = req

		return info

	def get_Params(self):

		parsed = urlparse(self.path)
		params = parse_qs(parsed.query)

		return parsed.path, params

	def get_User(self, cok):

		try: uid = cok["session"].value
		except: uid = None

		user = self.get_Cname()
		addr = self.client_address[0]
		session = self.server.logon.session(user, uid, addr)

		return session

	def get_Prev(self, path, logged = False, admin = False):

		if path in self.server.common: return True
		elif not logged: return False

		if admin and path in self.server.admins: return True
		if logged and path in self.server.users: return True

		return False

	def get_Redirect(self, path, logged = False, admin = False):

		if not path or path == "/": path = "/index.html"

		if not self.get_Prev(path, logged) and path.endswith(".html"): return "/logon.html"
		elif logged and path == "/logon.html": return "/index.html"
		else: return path

	def do_GET(self):

		st = time.time()

		try: cookies = SimpleCookie(self.headers.get("Cookie"))
		except: cookies = dict()

		try: path, params = self.get_Params()
		except: return self.send_Error(Exception(405, self.STR_ERROR_405, path))

		try:	user = self.get_User(cookies)
		except: user = None

		try: info = self.get_Info("post")
		except: info = None

		if user != None:
			log = user.is_valid()
			adm = user.is_admin()
		else:
			log = adm = False

		try: path = self.get_Redirect(path, log, adm)
		except: return self.send_Error(Exception(500, self.STR_ERROR_500, path))

		if not self.get_Prev(path, log, adm):
			return self.send_Error(Exception(403, self.STR_ERROR_403, path))
		elif user != None and log: user.on_refresh()

		try:

			if not path in self.server.handlers: mime, resp, cok = self.get_File(path)
			else: mime, resp, cok = self.server.handlers[path](user, params, None, cookies, info)

		except Exception as e: self.send_Error(e)
		else: self.send_Slite(mime, resp, cok)

		print("action: ", time.time() - st)

	def do_POST(self):

		try: cookies = SimpleCookie(self.headers.get("Cookie"))
		except: cookies = dict()

		try: clength = int(self.headers["content-length"])
		except: return self.send_Error(Exception(411, self.STR_ERROR_411, clength))

		try: ctype = self.headers["content-type"]
		except: return self.send_Error(Exception(415, self.STR_ERROR_415, ctype))

		try: path, params = self.get_Params()
		except: return self.send_Error(Exception(405, self.STR_ERROR_405, path))

		try:

			if ctype == "application/x-www-form-urlencoded":
				data = parse_qs(self.rfile.read(clength))
			elif ctype == "application/json":
				data = json.loads(self.rfile.read(clength))

		except: return self.send_Error(Exception(415, self.STR_ERROR_415, ctype))

		try:	user = self.get_User(cookies)
		except: user = None

		try: info = self.get_Info("post")
		except: info = None

		if user != None:
			log = user.is_valid()
			adm = user.is_admin()
		else:
			log = adm = False

		try: path = self.get_Redirect(path, log, adm)
		except: return self.send_Error(Exception(500, self.STR_ERROR_500, path))

		if not self.get_Prev(path, log, adm):
			return self.send_Error(Exception(403, self.STR_ERROR_403, path))
		elif user != None and log: user.on_refresh()

		if path in self.server.handlers:

			try: mime, resp, cok = self.server.handlers[path](user, params, data, cookies, info)
			except Exception as e: self.send_Error(e)
			else: self.send_Slite(mime, resp, cok)

		else: self.send_Error(Exception(404, self.STR_ERROR_404, path))
