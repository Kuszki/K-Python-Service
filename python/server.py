from http.server import ThreadingHTTPServer

from handler import httpHandler
from fsystem import fileSystem
from logon import httpLogon

import ssl, sys, os, json

db_config = json.load(open("config/database.json", "r"))

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.verify_mode = ssl.CERT_REQUIRED;
ssl_context.load_cert_chain("certs/pki/issued/server.crt", "certs/pki/private/server.key")
ssl_context.load_verify_locations("certs/pki/ca.crt")

server = ThreadingHTTPServer(("localhost", 8081), httpHandler)

server.socket = ssl_context.wrap_socket(server.socket, server_side = True)
server.logon = httpLogon(db_config)
server.fsystem = fileSystem("/data/Inne/test_docs/", db_config)
server.handlers = dict()

server.common = json.load(open("config/common.json", "r"))
server.admins = json.load(open("config/admins.json", "r"))
server.users = json.load(open("config/users.json", "r"))
server.paths = json.load(open("config/paths.json", "r"))

server.handlers["/logon.var"] = lambda u, p, d, c, i: server.logon.login(d.get("user"), i.addr, d.get("pass"))
server.handlers["/logout.var"] = lambda u, p, d, c, i: server.logon.logout(u.name)

server.handlers["/islogon.var"] = lambda u, p, d, c, i: ("text/plain", u.is_valid() if u else False, None)
server.handlers["/getuser.var"] = lambda u, p, d, c, i: ("text/plain", u.name if u else i.name if i else str(), None)

server.handlers["/getlist.var"] = lambda u, p, d, c, i: ("text/json", json.dumps(server.fsystem.getList(p), default = str), None)

try: server.serve_forever()
except KeyboardInterrupt: pass

server.server_close()
