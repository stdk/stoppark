from viewer import Viewer
from cherrypy import expose

class Editor(Viewer):
 def __init__(self,provider):
  self.provider = provider
  self.provider.load()

 @expose
 def edit(self,row,col,value,id):
  print row,col,value
  self.provider.setattr(row=int(row),idx=int(col),value=value) 
  return value
  
 @expose
 def add(self):
  self.provider.append()
  return 'success'
 
 @expose
 def delete(self,row):
  self.provider.delete(int(row))
  return 'success'
 
 @expose
 def save(self):
  self.provider.save()
  return 'success'
 
 @expose
 def cancel(self):
  self.provider.load()
  return 'success'