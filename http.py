# -*- coding: utf8 -*-
from tempfile import NamedTemporaryFile
from gevent.wsgi import WSGIServer
from commands import getoutput
from cgi import FieldStorage
from string import Template
from base64 import b64decode,b64encode
from hashlib import md5
from models import User

HOST = getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
PORT = 2000

TEMPLATES_FOLDER = 'ui'
AUTH_ZONE = 'STOPPARK'

class memoized(object):
 '''Decorator. Caches a function's return value each time it is called.
 If called later with the same arguments, the cached value is returned 
 (not reevaluated).
 '''
 def __init__(self,func):
  self.func = func
  self.cache = {}
  
 def __call__(self, *args,**kw):
  key = hash(str( (args,kw) ))
  try:
   return self.cache[key]
  except KeyError:
   print 'memoized call to %s' % (self.func.__name__)
   value = self.func(*args,**kw)
   self.cache[key] = value
   return value

 def __get__(self, obj, objtype):
  '''Support instance methods.'''
  return functools.partial(self.__call__, obj)

@memoized
def template(path,**kw):
  return Template(open(TEMPLATES_FOLDER + path).read()).substitute(**kw)

def access(auth_header):
 username,password = b64decode(auth_header.split()[1]).split(':') if auth_header else ('anonymous','')
 users = User.filter(name=username)
 if not len(users): return (0,None)
 user = users[0]
 return (user.level,user.name) if user.password == b64encode(md5(password).digest()) else(0,None)

def access_check(request):
 auth_header = request.env.get('HTTP_AUTHORIZATION',None)
 return access(auth_header) if auth_header else (0,None)

#applicable only to class members with request as a second parameter
def access_level(level):
 def decorator(func):
  def wrapper(self,req):
   if access_check(req)[0] < level: return req.forbidden('Access denied')  
   return func(self,req)
  return wrapper
 return decorator

def auth(request):
 location = 'http://{0}:{1}/'.format(HOST,PORT)
 request.start_response(request.FOUND,[
  ('Set-Cookie','logout=true'),
  ('Location',location)
 ])
 return ''

def index(request):
 if request.env.get('HTTP_COOKIE','') == 'logout=true':
  return request.auth(AUTH_ZONE,[('Set-Cookie','logout=false')])

 access = access_check(request)
 if not access[0]: return request.auth(AUTH_ZONE)

 request.start_response(request.OK,[request.content_type['html']])
 args = { 'host' : HOST, 'user' : access[1], 'level' : {1:'Пользователь',2:'Администратор'}[access[0]] }
 return [template('/index.html',**args)]

class CustomFieldStorage(FieldStorage):
 def make_file(self,binary=None):
  return NamedTemporaryFile("w+b",dir='data',delete=False)

class Request(object):
 OK           = '200 OK'
 FOUND        = '302 Found'
 BAD_REQUEST  = '400 Bad Request'
 UNAUTHORIZED = '401 Unauthorized'
 FORBIDDEN    = '403 Forbidden'
 NOT_FOUND    = '404 Not Found'
 NOT_ALLOWED  = '405 Method not allowed'
 SERVER_ERROR = '500 Internal Server Error'

 content_type = {
  'html' : ('Content-Type', 'text/html; charset=utf-8'),
  'json' : ('Content-Type', 'application/json; charset=utf-8'),
  'plain': ('Content-Type', 'text/plain; charset=utf-8')
 }

 def __init__(self,env,start_response):
  self.env = env
  self.start_response = start_response

 def post_query(self):
  return CustomFieldStorage(fp=self.env['wsgi.input'],environ=self.env)

 def auth(self,realm,ext_headers=[]):
  headers = [('WWW-Authenticate','Basic realm="{0}"'.format(realm))]
  self.start_response(self.UNAUTHORIZED,headers + ext_headers)
  return []

 def not_found(self):
  self.start_response(self.NOT_FOUND,[])
  return []

 def method_not_allowed(self):
  self.start_response(self.NOT_ALLOWED,[])
  return []

 def bad_request(self,exception):
  self.start_response(self.BAD_REQUEST,[self.content_type['plain']])
  return [repr(exception)] 

 def forbidden(self,exception = ''):
  self.start_response(self.FORBIDDEN,[self.content_type['plain']])
  return [str(exception)]

 def server_error(self,exception):
  self.start_response(self.SERVER_ERROR,[self.content_type['plain']])
  return [repr(exception)] 

 def ok(self,headers=[],data=''):
  self.start_response(self.OK,headers)
  return [data]

handlers = {
  'GET' : {'/' : index, '/auth' : auth },
  'POST': { }  
}

def transform_handlers(path,handlers):
 return dict( (
  method,
  dict( ('{0}/{1}'.format(path,name),handler)
        for name,handler in method_handlers.iteritems() )
 ) for method,method_handlers in handlers.iteritems() )

def register_handler(path,obj):
 obj_handlers = transform_handlers(path,obj.handlers)
 [ handlers[method].update(obj_method_handlers)
   for method,obj_method_handlers in obj_handlers.iteritems() ]

def application(env, start_response):
 request = Request(env,start_response)
 method_handlers = handlers.get(env['REQUEST_METHOD'],None)
 if not method_handlers:
  return request.method_not_allowed()
 handler = method_handlers.get(env['PATH_INFO'],Request.not_found)
 return handler(request)
 
def runserver():
 print 'Serving on {0}:{1}...'.format(HOST,PORT)
 WSGIServer((HOST, PORT), application,log=None).serve_forever()
