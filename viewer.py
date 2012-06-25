from json import dumps

class Viewer(object):
 def __init__(self,provider,cache = False):
  self.provider = provider
  self.cache = cache
  provider.load()
  self.handlers = { 
   'GET'  : { 'data' : self.get_data },
   'POST' : {}
   }

 def get_data(self,request):
  aaData = dumps({'aaData': self.provider.aaData(self.cache) })
  return request.ok([request.content_type['html']],aaData)