from json import dumps
from http import access_level

class Viewer(object):
 def __init__(self,provider,cache = False,secure = False):
  self.provider = provider
  self.cache = cache
  provider.load()
  self.handlers = { 
   'GET'  : { 'data' : self.secure_get_data if secure else self.get_data },
   'POST' : {}
   }

 @access_level(2)
 def secure_get_data(self,request):
  return self.get_data(request)

 def get_data(self,request):
  aaData = dumps({'aaData': self.provider.aaData(self.cache) })
  return request.ok([request.content_type['html']],aaData)