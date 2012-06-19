from json import dumps
from cherrypy import expose

class Viewer(object):
 def __init__(self,provider):
  self.provider = provider
  provider.load()
 
 @expose
 def data(self,**kw):
  return dumps({'aaData': self.provider.aaData(True) })

 @expose
 def update(self):  
  self.provider.load()
  return 'success'