from json import dump
from http import access_check

class Viewer(object):
 def __init__(self,provider):
  self.provider = provider
  provider.load()
  self.get_handlers = { 'data' : self.get_data }
  self.post_handlers = { 'update' : self.update }

 def get_data(self,req):
  level = access_check(req)[0]
  if not level: return req.bad_request()

  req.ok('text/html')
  cached = level == 2
  dump({'aaData': self.provider.aaData(cached) },req.wfile)

 def update(self,req):
  req.ok('text/html')
  self.provider.load()

 def handle_request(self,req,handlers):
  handlers[req.aPath[0]](req)
  #try: handlers[req.aPath[0]](req)
  #except KeyError: req.error('KeyError')
 def handle_get(self,req):
  self.handle_request(req,self.get_handlers)
 def handle_post(self,req):
  self.handle_request(req,self.post_handlers)
