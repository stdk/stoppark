from sqlite3 import connect as sqlite3_connect,Row as sqlite3_row
from itertools import izip

DATABASE_FILENAME = 'data/db.db3'

class Connection(object):
 def __init__(self,filename):
  self.connection = None
  self.open(filename)

 def open(self,filename = DATABASE_FILENAME, replace = False):
  if self.connection and replace: self.close()
  if not self.connection:
   self.connection = sqlite3_connect(filename)
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
  self.load()
 
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
   setattr(self.data[row],self.cls.visible_fields[idx],value)
   self.modified.add(self.data[row])

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
  self.load()
 
 def setattr(self,row,idx,value):
  setattr(self.record,self.cls.visible_fields[row],value)

class MetaModel(type):
 def __new__(cls, name, bases, dict):

  fields = sorted( [ key for key,value in dict.iteritems() if hasattr(value,'definition') ], key = lambda k:dict[k].idx )
  field_definitions = ','.join( ( '%s %s' % ( key,dict[key].definition() ) for key in fields ) )
  visible_fields = [key for key in fields if dict[key].visible]
  create_query = 'create table if not exists %s (%s)' % (name,field_definitions)
  #select_query = 'select %s from %s' % (','.join(fields),name)
  select_query = 'select * from %s' %(name)
  save_query = 'replace into %s(%s) values(%s)' % (name,','.join(fields),','.join('?' * len(fields)))
  delete_query = 'delete from %s' % (name)

  dict['fields']         = fields
  dict['visible_fields'] = visible_fields
  dict['create_query']   = create_query
  dict['select_query']   = select_query
  dict['save_query']     = save_query
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
  #[ obj.__dict__.__setitem__(key,value) for key,value in args ]
  if row: [obj.__dict__.__setitem__(key,row[key]) for key in row.keys()] 
  return obj

 @staticmethod
 def array(self,**kw):
  keys = self.visible_fields if kw.get('only_visible',False) else self.fields
  return [ getattr(self,key) for key in keys ]

 @staticmethod
 def save(self):
  values = self.array()
  cursor = self.connection.cursor()
  cursor.execute(self.save_query,values)
  self.connection.commit()

 @staticmethod
 def delete(self):
  cursor = self.connection.cursor()
  pk = 'id'
  clause = ' where %s="%s"' % (pk,getattr(self,pk))
  query = self.delete_query + clause
  cursor.execute(query)
  self.connection.commit()

 @staticmethod
 def create(cls):
  cursor = cls.connection.cursor()
  cursor.execute( cls.create_query )
  cls.connection.commit()

 @staticmethod
 def objects_from_query(cls,query,izip=izip):
  cursor = cls.connection.cursor()
  cursor.execute(query)
  return [cls(row) for row in cursor]  

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
 typename = 'text'
 visible = True

 def idx_gen():
  idx = 0
  while True:
   yield idx
   idx += 1
 idx_gen = idx_gen()

 def __init__(self,idx=None,**kwargs):
  self.idx = idx if idx else Field.idx_gen.next()
  self.sql =  { 'primary_key':'primary key','not_null':'not null' }
  self.arg = [ 'visible' ]
  [setattr(self,key,value) for (key,value) in kwargs.iteritems() if key in self.sql or key in self.arg]
 def definition(self):
  return ' '.join( (self.typename,' '.join([self.sql[key] for key in self.sql if hasattr(self,key)])) )

class TextField(Field):
 typename = 'text'

class BlobField(Field):
 typename = 'blob'

class IntField(Field):
 typename = 'integer'

class Model(object):
 __metaclass__ = MetaModel
 connection = Connection(DATABASE_FILENAME)
