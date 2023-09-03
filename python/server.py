from http.server import ThreadingHTTPServer

from handler import httpHandler
from logon import httpLogon

import ssl, sys, os, json

db_config = json.load(open("dbconfig.json", "r"))

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.verify_mode = ssl.CERT_REQUIRED;
ssl_context.load_cert_chain("certs/pki/issued/server.crt", "certs/pki/private/server.key")
ssl_context.load_verify_locations("certs/pki/ca.crt")

server = ThreadingHTTPServer(("localhost", 8081), httpHandler)

server.socket = ssl_context.wrap_socket(server.socket, server_side = True)
server.logon = httpLogon(db_config)
server.root = dict()
server.handlers = dict()

server.root["js"] = "scripts"
server.root["css"] = "styles"
server.root["html"] = "slites"
server.root["docs"] = "data"

server.handlers["/logon.var"] = lambda u, p, d, c: server.logon.login(d.get("user"), u.get("addr"), d.get("pass"))
server.handlers["/logout.var"] = lambda u, p, d, c: server.logon.logout(u.get("user"))

server.handlers["/islogon.var"] = lambda u, p, d, c: ("text/plain", server.logon.validate(u.get("user"), u.get("uuid"), u.get("addr")), None)
server.handlers["/getuser.var"] = lambda u, p, d, c: ("text/plain", u.get("user"), None)

try: server.serve_forever()
except KeyboardInterrupt: pass

server.server_close()
