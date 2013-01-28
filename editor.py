from viewer import Viewer
from http import access_level

class Editor(Viewer):
 def __init__(self,provider,secure = False):
  super(Editor,self).__init__(provider,cache = True,secure = secure)

  self.handlers['POST'].update({
   'edit'   : self.edit,
   'add'    : self.add,
   'delete' : self.delete,
   'save'   : self.save,
   'cancel' : self.cancel,
  })

 @access_level(2)
 def edit(self,request):
  post = request.post_query()

  try:
   value = post['value'].value
   row = int(post['row'].value)
   col = int(post['col'].value)  
   self.provider.setattr(row=row,idx=col,value=value) 
   return request.ok([request.content_type['html']],value)
  except KeyError as e: return request.bad_request(e)
  except ValueError as e: return request.bad_request(e)

 @access_level(2)
 def add(self,request):
  self.provider.append()
  return request.ok()

 @access_level(2)
 def delete(self,request):
  post = request.post_query()
  try:
   row = int(post['row'].value)
   self.provider.delete(row)
   return request.ok()
  except TypeError as e: return request.bad_request(e)
  except KeyError as e: return request.bad_request(e)

 @access_level(2)
 def save(self,request):
  try:
   self.provider.save()
   return request.ok()
  except IOError as e: return request.server_error(e)

 @access_level(2)
 def cancel(self,request):
  try:
   self.provider.load()
   return request.ok()
  except IOError as e: return request.server_error(e)
