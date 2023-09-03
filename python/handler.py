from http.server import BaseHTTPRequestHandler
from http.cookies import SimpleCookie

from urllib.parse import urlparse, parse_qs
from pathlib import Path

import io, os, magic, json, traceback

class httpHandler(BaseHTTPRequestHandler):

	STR_ERROR_DEFAULT = "Błąd podczas generowania zasobu"
	INT_ERROR_DEFAULT = 400

	STR_ERROR_403 = "Niedozwolona ścieżka"
	STR_ERROR_404 = "Brak wskazanego zasobu"
	STR_ERROR_405 = "Niedozwolona operacja"
	STR_ERROR_411 = "Nie podano długości zasobu"
	STR_ERROR_415 = "Niedozwolony typ zasobu"
	STR_ERROR_500 = "Wystąpił błąd po stronie serwera"

	def send_Text(self, code, mime, text, cookie = None):

		if type(cookie) != SimpleCookie: cookie = SimpleCookie(cookie)

		if type(text) == str: text = text.encode("utf-8")
		elif type(text) != bytes: text = str(text).encode("utf-8")

		self.send_response(code)
		self.send_header("Connection", "keep-alive")
		self.send_header("Content-Type", mime + "; charset=utf-8")
		self.send_header("Content-Length", len(text))

		for c in cookie.values(): self.send_header("Set-Cookie", c.output(header = ""))

		self.end_headers()
		self.wfile.write(text)

	def send_File(self, obj, mime = None, size = None):

		if mime == None:
			try:
				mm = magic.Magic(mime = True)
				mime = mm.from_file(obj.name)
			except:
				return self.send_Error(Exception(500, self.STR_ERROR_500))

		if size == None:
			try:
				size = os.path.getsize(obj.name)
			except:
				return self.send_Error(Exception(500, self.STR_ERROR_500))

		self.send_response(200)
		self.send_header("Connection", "keep-alive")
		self.send_header("Content-Type", mime)
		self.send_header("Content-Length", size)
		self.end_headers()

		while True:
			data = obj.read(10240)

			if data == None: break
			else: self.wfile.write(data)

	def send_Slite(self, mime, obj, cok = None):

		if issubclass(type(obj), str): self.send_Text(200, mime, obj.encode("utf-8"), cok)
		elif issubclass(type(obj), io.IOBase): self.send_File(200, mime, obj, cok)
		else: self.send_Text(200, mime, obj, cok)

	def send_Error(self, exc, cok = None):

		print("send_Error: ", exc)
		print(traceback.format_exc())

		try: code = int(exc.args[0])
		except: code = self.INT_ERROR_DEFAULT

		try: text = str(exc.args[1])
		except: text = self.STR_ERROR_DEFAULT

		self.send_Text(code, "text/plain", text, cok)

	def get_File(self, path, user):

		if path == "/": path = "index.html"

		if path.endswith(".css"):
			src = self.server.root["css"]
			mime = "text/css"

		elif path.endswith(".js"):
			src = self.server.root["js"]
			mime = "text/javascript"

		elif path.endswith(".html"):
			src = self.server.root["html"]
			mime = "text/html"

		else: raise Exception(415, self.STR_ERROR_415)

		if not user["valid"] and mime == "text/html": path = "logon.html"
		elif user["valid"] and path == "/logon.html": path = "index.html"

		try: path = Path(src + "/" + path).absolute()
		except: raise Exception(404, self.STR_ERROR_404)

		if not path.is_file(): raise Exception(404, self.STR_ERROR_404)

		if path.is_relative_to(src): return mime, path.read_bytes(), None
		else: raise Exception(403, self.STR_ERROR_403)

	def get_Params(self):

		parsed = urlparse(self.path)
		params = parse_qs(parsed.query)

		return parsed.path, params

	def get_User(self, cookies):

		try:
			subject = self.request.getpeercert()["subject"]
			user = dict(x[0] for x in subject)["commonName"]

		except: user = None

		try: uid = cookies["session"].value
		except: uid = None

		addr = self.client_address[0]
		valid = self.server.logon.validate(user, uid, addr)

		return \
		{
			"valid": valid,
			"addr": addr,
			"user": user,
			"uuid": uid
		}

	def do_GET(self):

		try: cookies = SimpleCookie(self.headers.get("Cookie"))
		except: cookies = dict()

		try: path, params = self.get_Params()
		except: return self.send_Error(Exception(405, self.STR_ERROR_405))

		try:	user = self.get_User(cookies)
		except: user = None

		try:

			if not (path in self.server.handlers): mime, resp, cok = self.get_File(path, user)
			else: mime, resp, cok = self.server.handlers[path](user, params, None, cookies)

		except Exception as e: self.send_Error(e)
		else: self.send_Slite(mime, resp, cok)

	def do_POST(self):

		try: cookies = SimpleCookie(self.headers.get("Cookie"))
		except: cookies = dict()

		try: clength = int(self.headers["content-length"])
		except: return self.send_Error(Exception(411, self.STR_ERROR_411))

		try: ctype = self.headers["content-type"]
		except:  return self.send_Error(Exception(415, self.STR_ERROR_415))

		try: path, params = self.get_Params()
		except: return self.send_Error(Exception(405, self.STR_ERROR_405))

		if ctype == "application/x-www-form-urlencoded":
			data = parse_qs(self.rfile.read(clength))
		elif ctype == "application/json":
			data = json.loads(self.rfile.read(clength))

		try:	user = self.get_User(cookies)
		except: user = None

		if path in self.server.handlers:

			try: mime, resp, cok = self.server.handlers[path](user, params, data, cookies)
			except Exception as e: self.send_Error(e)
			else: self.send_Slite(mime, resp, cok)

		else: self.send_Error(Exception(405, self.STR_ERROR_405))
