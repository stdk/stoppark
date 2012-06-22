from json import dumps
from http import access_check,access_level

class Viewer(object):
 def __init__(self,provider):
  self.provider = provider
  provider.load()
  self.handlers = { 
   'GET'  : { 'data' : self.get_data },
   'POST' : { 'update' : self.update }
   }

 def get_data(self,request):
  aaData = dumps({'aaData': self.provider.aaData(True) })
  return request.ok([request.content_type['html']],aaData)

 @access_level(2)
 def update(self,request):
  self.provider.load()
  return request.ok()
