import logging
from viewer import Viewer
from http import access_level

class Editor(Viewer):
 def __init__(self,provider):
  self.provider = provider
  self.provider.load()

  self.get_handlers = { 'data'   : self.get_data }

  self.post_handlers = {'edit'   : self.edit,
                        'add'    : self.add,
                        'delete' : self.delete,
                        'save'   : self.save,
                        'cancel' : self.cancel,
                        'update' : self.update }  

 @access_level(2)
 def edit(self,req):
  post = req.post_query()
  logging.debug('edit: %s' % str(post))

  try:
   value = post['value'].value
   row = int(post['row'].value)
   col = int(post['col'].value)  
   self.provider.setattr(row=row,idx=col,value=value) 
   req.ok('text/html',value)
  except KeyError as e: req.error(e)
  except ValueError as e: req.error(e)
 
 @access_level(2)
 def add(self,req):
  post = req.post_query()
  self.provider.append()
  req.ok('text/plain','+')

 @access_level(2)
 def delete(self,req):
  post = req.post_query()
  try:
   row = int(post['row'].value)
   self.provider.delete(row)
   req.ok('text/plain','+')
  except TypeError as e: req.error(e) 
  except KeyError as e: req.error(e)

 @access_level(2)
 def save(self,req):
  try:
   self.provider.save()
   req.ok('text/plain','+')
  except IOError as e: req.error(e)

 @access_level(2)
 def cancel(self,req):
  try:
   self.provider.load()
   req.ok('text/plain','+')
  except IOError as e: req.error(e)
