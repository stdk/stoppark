# -*- coding: utf8 -*-
from string import Template
from database import Connection,Model,DATABASE_FILENAME
from socket import create_connection
from http import access_level

TEMPLATE = '''
${message}
<form enctype="multipart/form-data" method="POST" action="/upload/" >
 <input type="file" name="file" /><input id="submit" type="submit" />
</form>
'''

class DatabaseUploader(object):
 def __init__(self):
  self.handlers = { 
   'GET'  : { '' : self.get },
   'POST' : { '' : self.post }
   }

 INITIAL_MESSAGE = 'Выберите файл базы данных на Вашем компьютере и загрузите его на сервер:'
 SUCCESS_MESSAGE = 'Загрузка завершена успешно.'
 FAIL_MESSAGE    = 'Не удалось загрузить файл базы данных'

 @access_level(2)
 def get(self,request,message = None):
  if not message: message = self.INITIAL_MESSAGE
  request.start_response(request.OK,[request.content_type['html']])
  return Template(TEMPLATE).substitute({'message' : message})

 @access_level(2)
 def post(self,request):
  try:
   new_db = request.post_query()['file']

   target_filename = DATABASE_FILENAME + '.new'

   # There is special behaviour in python 2.7 (only ?) FieldStorage class.
   # It doesnt create file using make_file when its size is less than 1000,
   # using StringIO object instead.
   # But since we need file with real filename in FIRMWARE_PATH anyway,
   # we should create this file and dump there contents of current file object.
   # Criteria for this can be either ininstance(firmware.file,NamedTemporaryFile)
   # or hasattr(firmware.file,"name")   
   if hasattr(new_db.file,'name'): 
    from os import rename,chmod
    rename(new_db.file.name,target_filename)
    chmod(target_filename,0744)
   else:
    open(target_filename,'wb').write(new_db.file.read())

   Model.connection.open(target_filename,replace=True)
   Model.connection.test()
   Model.connection.close()

   rename(target_filename,DATABASE_FILENAME)

   #to complete database change process we should reopen db connection in mid.py via special command it can accept
   create_connection(('127.0.0.1',101)).send('>>>reset')  

   return self.get(request,self.SUCCESS_MESSAGE)
  except Exception as e:
   message = '%s: [%s]: %s' % (self.FAIL_MESSAGE,e.__class__.__name__,e)
   return self.get(request,message) 
  finally:
   Model.connection.open(DATABASE_FILENAME,replace=True)
