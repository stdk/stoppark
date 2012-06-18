# -*- coding: utf8 -*-
import logging
from commands import getoutput
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
from cgi import FieldStorage
from httplib import HTTPConnection
from string import Template
from base64 import b64decode,b64encode
from hashlib import md5
from models import User

HOST = getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
PORT = 2000

OK                = 200
FOUND             = 302
BAD_REQUEST       = 400
UNAUTHORIZED      = 401
NOT_FOUND         = 404

TEMPLATES_FOLDER = 'ui'

class AuthZone(object):
 @staticmethod
 def auth_zone_generator(base,period):
  i = 0
  while True:
   yield (base + str(i))
   i = (i + 1) % period

 def __init__(self,base,period):
  self.generator = AuthZone.auth_zone_generator(base,period)
  self._value = self.generator.next()

 def next(self):
  self._value = self.generator.next()
  return self._value

 def value(self):
  return self._value

class AuthZoneFixed(object):
 def __init__(self,base):
  self._value = base
 def next(self):
  return self._value
 def value(self):
  return self._value

#AUTH_ZONE = AuthZone('STOPPARK',10)
AUTH_ZONE = AuthZoneFixed('STOPPARK')

def use_template(name,parameters):
 return Template().substitute(**parameters) 

class BaseRequestHandler(BaseHTTPRequestHandler):
 def log_message(self,format,*args):
  log_format = '%s ' + format
  log_args = ( self.address_string(), ) + args
  logging.info(log_format % log_args)
 def not_found(self):
  self.send_response(NOT_FOUND)
  self.send_header('Content-type','text/plain')
  self.end_headers()
  self.wfile.write('Not found')
 
 def bad_request(self):
  self.send_response(BAD_REQUEST)
  self.end_headers()
 
 def ok(self,content_type):
  self.send_response(OK)
  self.send_header('Content-type',content_type)
  self.end_headers()
  
 def auth(self,realm):
  self.send_response(UNAUTHORIZED)
  self.send_header('WWW-Authenticate','Basic realm="%s"' % (realm))
  self.end_headers()

 def error(self,exception):
  logging.error('%s: %s' % (exception.__class__.__name__,exception))
  self.send_response(BAD_REQUEST)
  self.send_header('Content-type','text/html')
  self.end_headers()
  
 def redirect(self,path):
  self.send_response(FOUND)
  location = 'http://%s:%s%s' % (HOST,PORT,path)
  self.send_header('Location',location)
  self.end_headers()
 
 def parse_path(self):
  pure_path,query_string = (self.path+'?').split('?')[:2]
  return pure_path,query_string 
  
 @staticmethod 
 def parse_query_string(s):
  return dict( ( (pair+'=').split('=')[:2] for pair in s.split('&') ) )   
  
 def post_query(self):
  return FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'] })

 def get_query(self):
  pure_path,query_string = self.parse_path()
  return self.parse_query_string(query_string)

def version(self):
 self.ok('text/plain')
 self.wfile.write('0.4.2')

def access_check(self):
 auth_header = self.headers.get('Authorization')
 username,password = b64decode(auth_header.split()[1]).split(':') if auth_header else ('anonymous','')
 users = User.filter(name=username)
 if not len(users): return (0,None)
 user = users[0]
 return (user.level,user.name) if user.password == b64encode(md5(password).digest()) else(0,None)

#applicable only to class members with request as a second parameter
def access_level(level):
 def decorator(func):
  def wrapper(self,req):
   if access_check(req)[0] < level: return req.bad_request()  
   return func(self,req)
  return wrapper
 return decorator

def auth(self):
 self.send_response(FOUND)
 self.send_header("Set-Cookie","logout=true")
 location = 'http://%s:%s%s' % (HOST,PORT,'')
 self.send_header('Location',location)
 self.end_headers() 

def index(self):
 cookie = self.headers.get("Cookie")
 if cookie == 'logout=true':
  self.send_response(UNAUTHORIZED)
  self.send_header("Set-Cookie","logout=false")
  self.send_header('WWW-Authenticate','Basic realm="%s"' % (AUTH_ZONE.value()))
  self.end_headers()
  return

 access = access_check(self)
 if not access[0]: return self.auth(AUTH_ZONE.value())
 
 self.ok('text/html')
 args = { 'host' : HOST, 'user' : access[1], 'level' : {1:'Пользователь',2:'Администратор'}[access[0]] }
 self.wfile.write(Template(open(TEMPLATES_FOLDER+'/index.html').read()).substitute(**args))

get_handlers = { '' : index,'auth' : auth, 'version' : version }
post_handlers = {}

def register_handler(path,handler):
 get_handlers[path] = handler.handle_get
 post_handlers[path] = handler.handle_post

class RequestHandler(BaseRequestHandler):
 def handle_request(self,handlers):
  path,query_string = self.parse_path()
  self.aPath = path.split('/')[1:]
  handler = handlers.get(self.aPath[0],BaseRequestHandler.not_found)
  self.aPath = self.aPath[1:]
  handler(self)

 def do_GET(self):
  self.handle_request(get_handlers)

 def do_POST(self):
  self.handle_request(post_handlers)

def runserver():
 server_class = HTTPServer
 httpd = server_class((HOST, PORT), RequestHandler)
 logging.info('Server Starts [%s:%s]' % (HOST,PORT) )
 try:
  httpd.serve_forever()
 except KeyboardInterrupt:
  pass
 httpd.server_close()
 logging.info('Server Stops [%s:%s]' % (HOST,PORT) )
