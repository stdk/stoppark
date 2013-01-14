from commands import getoutput
from asyncore import dispatcher,dispatcher_with_send,loop
from socket import AF_INET,SOCK_STREAM
from database import Model
import logging
import logging.config

#ADDR = getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:] , 101

logging.config.dictConfig({
 'version': 1,    # Configuration schema in use; must be 1 for now
 'formatters': {
     'standard': {
         'format': ('%(asctime)s %(host)-15s '
                    '%(levelname)-8s %(message)s')}},

 'handlers': {'mid': { 'backupCount': 10,
                       'class': 'logging.handlers.RotatingFileHandler',
                       'filename': 'data/mid.log',
                       'formatter': 'standard',
                       'level': 'DEBUG',
                       'maxBytes': 10000000 }
             },
 # Specify properties of the root logger
 'root': {
          'level': 'DEBUG',
          'handlers': ['mid']
 },
})

class TcpServer(dispatcher):
 def __init__(self, (host, port), handler):
  dispatcher.__init__(self)
  self.handler = handler
  self.create_socket(AF_INET, SOCK_STREAM)
  self.set_reuse_addr()
  self.bind((host, port))
  self.listen(20)
  print 'Listen on %s:%s' % (host,port)

 def handle_accept(self):
  pair = self.accept()
  if pair: self.handler(pair)

class Handler(dispatcher_with_send):
 BYTES_TO_RECV = 512
 COMMAND_PREFIX = '>>>'

 COMMAND_HANDLERS = {
  'reset' : lambda: Model.connection.open(replace=True)
 }

 def __init__(self,(sock,(host,port))):
  dispatcher_with_send.__init__(self,sock)
  self.extra = { 'host': host }

 def handle_command(self,command):
  print 'handle_command',command
  try:
   self.COMMAND_HANDLERS[command]()
   self.send('OK')
  except Exception as ex:
   logging.error('%s[%s]', ex.__class__.__name__, ex, extra = self.extra)
   self.send('FAIL')
 def handle_query(self,query):
  try:
   rows = Model.connection.cursor().execute(query)
   answer = '\n'.join( '|'.join( str(field) for field in row ) for row in rows )
   logging.debug("<-[%s]",answer or 'NONE',extra=self.extra)
   self.send(answer.decode('utf-8').encode('cp1251')) if answer else self.send('NONE')
   Model.connection.commit()    
  except Exception as ex:
   logging.error('%s[%s]', ex.__class__.__name__, ex, extra = self.extra)
   self.send('FAIL') 

 def handle_read(self):
  data = self.recv(self.BYTES_TO_RECV)
  if data:
   query = data.decode('cp1251').strip()
   logging.debug('->[%s]', query, extra = self.extra)
   if query.startswith(self.COMMAND_PREFIX):
    self.handle_command(query[3:])
   else:
    self.handle_query(query)
  self.close()

sql = TcpServer( ('0.0.0.0',101), Handler)
loop()
