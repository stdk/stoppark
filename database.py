from sqlite3 import connect as sqlite3_connect,Row as sqlite3_row,OperationalError,ProgrammingError
from itertools import izip

DATABASE_FILENAME = 'data/db.db3'

class Connection(object):
 def __init__(self,filename):
  self.connection = None
  self.open(filename)

 def open(self,filename = DATABASE_FILENAME, replace = False):
  if self.connection and replace: self.close()
  if not self.connection:
   self.connection = sqlite3_connect(filename,isolation_level = 'DEFERRED')
   self.connection.text_factory = str
   self.connection.row_factory = sqlite3_row
   self._cursor = self.connection.cursor() 
  else:
   print 'Connection already open'

 def test(self):
  from models import test_models
  test_models()

 def close(self):
  if self.connection: self.connection.close()
  self.connection = None

 def cursor(self):
  return self._cursor

 def commit(self):
  return self.connection.commit()

 def rollback(self):
  return self.connection.rollback()

 def __enter__(self):
  return self.connection.__enter__()
 
 def __exit__(self, *args):
  return self.connection.__exit__(*args)
 

class ModelDataProvider(object):
 def __init__(self,cls):
  self.cls = cls
  self.data = []
  self.modified = set()
 
 def aaData(self,cached):
  data = self.data if cached else self.cls.all()
  return [ record.array(only_visible=True) for record in data ]
 
 def load(self):
  self.modified.clear()    
  self.data = self.cls.all()
 
 def save(self):
  [ record.save() for record in self.modified ]
  self.cls.connection.commit()
  ret = [ record.array(only_visible=True) for record in self.modified ]
  self.load()
  return ret
 
 def append(self):
  obj = self.cls()
  self.data.append( obj )
  self.modified.add( obj )
 
 def delete(self,row):
  self.data[row].delete()
  self.modified.discard(self.data[row])
  del self.data[row]  
 
 def setattr(self,row=None,idx=None,value=None):
  if idx:
   obj,field = self.data[row],self.cls.visible_fields[idx]
   setattr(obj,field,value)
   self.modified.add(obj)
   return getattr(obj,field)

class InvertModelDataProvider(object):
 def __init__(self,cls):
  self.cls = cls
  self.record = None

 def aaData(self,cached):
  return [ [ field,getattr(self.record,field) ] for field in self.cls.visible_fields ]

 def load(self):
  self.record = self.cls.all()[0]

 def save(self):
  self.record.save()
  self.cls.connection.commit()
  self.load()
 
 def setattr(self,row,idx,value):
  setattr(self.record,self.cls.visible_fields[row],value)
  return value

class MetaModel(type):
 def __new__(cls, name, bases, dict):

  all_fields = sorted( [ key for key,value in dict.iteritems() if hasattr(value,'idx') ], key = lambda k:dict[k].idx )
  fields = [key for key in all_fields if hasattr(dict[key],'definition')]
  field_definitions = ','.join( ( '%s %s' % ( key,dict[key].definition() ) for key in fields ) )
  visible_fields = [key for key in all_fields if dict[key].visible]
  create_query = 'create table if not exists %s (%s)' % (name,field_definitions)
  select_query = 'select * from %s' %(name)
  save_query = '%%s into %s(%s) values(%s)' % (name,','.join(fields),','.join('?' * len(fields)))
  delete_query = 'delete from %s' % (name)

  try: 
    pk_name = [key for key in all_fields if hasattr(dict[key],'primary_key')][0]
    dict['pk_name'] = pk_name
    dict['pk'] = property(MetaModel.get_pk,MetaModel.set_pk)
  except IndexError: print 'There is no primary key defined for:',name

  dict['fields']         = fields
  dict['visible_fields'] = visible_fields
  dict['create_query']   = create_query
  dict['select_query']   = select_query
  dict['replace_query']  = save_query % ('replace',)
  dict['insert_query']   = save_query % ('insert',)
  dict['delete_query']   = delete_query

  dict['create']        = classmethod(MetaModel.create)
  dict['all']           = classmethod(MetaModel.all)
  dict['filter']        = classmethod(MetaModel.filter)
  dict['data_provider'] = classmethod(MetaModel.data_provider)
  dict['save']    = MetaModel.save
  dict['delete']  = MetaModel.delete
  dict['array']   = MetaModel.array
 
  return type.__new__(cls, name, bases, dict)

 def __call__(cls,row = None,*args,**kw):
  '''
  MetaClass constructor for all derived classes 
  Supports 3-step field initialization:
  1. Normal class constructor initialization.
  2. Initializing fields via keyword arguments (**kw) using setattr.
  3. Initializing fields using *args (array of (key,value) tuples) directly to object __dict__
  '''
  obj = super(MetaModel, cls).__call__()
  [ setattr(obj,key,kw.get(key,None)) for key in cls.fields if key not in obj.__dict__ ]
  if row: [obj.__dict__.__setitem__(key,row[key]) for key in row.keys()] 
  return obj

 @staticmethod
 def get_pk(self):
  return getattr(self,self.pk_name)

 @staticmethod
 def set_pk(self,value):
  setattr(self,self.pk_name,value)

 @staticmethod
 def array(self,only_visible = False,**kw):
  keys = self.visible_fields if only_visible else self.fields
  return [ getattr(self,key) for key in keys ]

 @staticmethod
 def save(self):
  cursor = self.connection.cursor()
  query = self.replace_query if self.pk != None else self.insert_query
  cursor.execute(query,self.array())
  if self.pk == None: self.pk = cursor.lastrowid

 @staticmethod
 def delete(self):
  cursor = self.connection.cursor()
  clause = ' where %s="%s"' % (self.pk_name,self.pk)
  query = self.delete_query + clause
  cursor.execute(query)

 @staticmethod
 def create(cls):
  cursor = cls.connection.cursor()
  cursor.execute( cls.create_query )
  cls.connection.commit()

 @staticmethod
 def objects_from_query(cls,query,izip=izip):
  cursor = cls.connection.cursor()
  try:
   cursor.execute(query)
   return [cls(row) for row in cursor]  
  except (ProgrammingError,OperationalError) as e:
   from traceback import print_exc
   print '-'*60
   print 'Executing:',query
   print_exc()
   print '-'*60

 @staticmethod
 def all(cls):
  return MetaModel.objects_from_query(cls,cls.select_query)

 @staticmethod
 def filter(cls,**kw):
  clause = ' and '.join( '%s="%s"' % (key,value) for key,value in kw.iteritems() )
  query = ' where '.join( (cls.select_query,clause) )
  return MetaModel.objects_from_query(cls,query)  

 @staticmethod
 def data_provider(cls,invert=False):
  if invert: return InvertModelDataProvider(cls)
  else: return ModelDataProvider(cls)

class Field(object):
 visible = True

 def idx_gen():
  idx = 0
  while True:
   yield idx
   idx += 1
 idx_gen = idx_gen()

 def __init__(self):
  self.idx = self.idx_gen.next()

class SqlField(Field):
 typename = 'text'

 def __init__(self,**kwargs):
  super(SqlField,self).__init__()
  self.sql =  { 'primary_key':'primary key','not_null':'not null' }
  self.arg = [ 'visible','idx' ]
  [setattr(self,key,value) for (key,value) in kwargs.iteritems() if key in self.sql or key in self.arg]
 def definition(self):
  return ' '.join( (self.typename,' '.join([self.sql[key] for key in self.sql if hasattr(self,key)])) )

class TextField(SqlField):
 typename = 'text'

class BlobField(SqlField):
 typename = 'blob'

class IntField(SqlField):
 typename = 'integer'

class VirtualField(Field,property):
 def __init__(self,*args):
  Field.__init__(self)
  property.__init__(self,*args)

class Model(object):
 __metaclass__ = MetaModel
 connection = Connection(DATABASE_FILENAME)
