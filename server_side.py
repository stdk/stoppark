from json import dumps
from database import Model,MetaModel
from cgi import escape
from models import Card
import re

iSortColRegex = re.compile('iSortCol_\d+')

class DatatablesQuery(object):
 def __init__(self,model,post = None):
  self.model = model
  self.fields = model.visible_fields
  self.table = model.__name__
  if post: self.update(post)

 def update(self,post):
  self.iDisplayStart = self.get(post,'iDisplayStart')
  self.iDisplayLength = self.get(post,'iDisplayLength')
  self.sEcho = self.get(post,'sEcho')
  self.iSortingCols = self.get(post,'iSortingCols')
  self.sort_col = self.fields[self.get(post,'iSortCol_0',0)]
  self.sort_dir = self.get(post,'sSortDir_0','asc')

 def sql(self):
  args = (self.table,self.sort_col,self.sort_dir,self.iDisplayStart,self.iDisplayLength) 
  return 'select * from %s order by %s %s limit %i,%i' % args

 def sql_total_records(self):
  return 'select count(*) from %s' % (self.table,) 

 def sql_display_records(self):
  return 'select count(*) from %s' % (self.table,)

 def sql_update(self,column,id,value):
  return 'update %s set %s="%s" where id=%s' % (self.table,self.fields[column],value,id)

 def sql_delete(self,id):
  return 'delete from %s where id=%s' % (self.table,id)

 def sql_new(self):
  obj = self.model()

 def get(self,post,name,default = None):
  t = { 'i': int, 's': str }[name[0]]
  try: return t(escape(post[name].value))
  except KeyError: return default
  
 def __str__(self):
  return str( (self.sEcho,self.iDisplayStart,self.iDisplayLength,self.sort_col,self.sort_dir) )

class ServerSideEditor(object):
 def __init__(self,model = Card):
  self.model = model
  self.query = DatatablesQuery(model)
  self._total_records = self.total_records()

  self.handlers = { 
   'GET'  : { 
    'data' : self.get_data
   },
   'POST' : {
      'edit'   : self.edit,
      'add'    : self.add,
      'delete' : self.delete,
      'save'   : self.save,
      'cancel' : self.cancel,
    }
  }

 def total_records(self,update = False):
  return int(self.fetch_scalar(self.query.sql_total_records()))

 def fetch_scalar(self,query):
  print query
  return Model.connection.cursor().execute(query).next()[0]

 def execute(self,query):
  print query
  return Model.connection.cursor().execute(query)

 def get_data(self,request):
  post = request.post_query()
  self.query.update(post)
  print self.query
  
  data = MetaModel.objects_from_query(self.model,self.query.sql()) 

  aaData = dumps({
    'aaData': [ record.array(only_visible=True) for record in data ],
    'sEcho' : int(self.query.sEcho),
    'iTotalRecords': self._total_records,
    'iTotalDisplayRecords': int(self.fetch_scalar(self.query.sql_display_records()))
  })
  
  return request.ok([request.content_type['html']],aaData)

 def edit(self,request):
  post = request.post_query()
  print post

  try:
   value = escape(post['value'].value)
   column = int(post['col'].value)  
   id = int(post['id'].value)

   self.execute(self.query.sql_update(column,id,value))

   return request.ok([request.content_type['html']],value)
  except KeyError as e: return request.bad_request(e)
  except ValueError as e: return request.bad_request(e)

 def add(self,request):
  print request.post_query()

 def delete(self,request):
  post = request.post_query()
  try:
   id = int(post['id'].value)
   self.execute(self.query.sql_delete(id))
   return request.ok()
  except TypeError as e: return request.bad_request(e)
  except KeyError as e: return request.bad_request(e)
  
 def save(self,request):
  Model.connection.commit()
  return request.ok()
 
 def cancel(self,request):
  Model.connection.rollback()
  return request.ok()  