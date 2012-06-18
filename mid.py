from commands import getoutput
from asyncore import dispatcher,dispatcher_with_send,loop
from socket import AF_INET,SOCK_STREAM
from sqlite3 import connect as sqlite3_connect

ADDR = getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:] , 101
connection = sqlite3_connect('data/db.db3')
connection.text_factory = str
cursor = connection.cursor()

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
  if pair: self.handler(pair[0])

class SQLHandler(dispatcher_with_send):
 def handle_read(self):
  data = self.recv(512)
  if data:
   try:
    cursor.execute(data.decode('cp1251'))
    answer = '\n'.join( '|'.join( str(field) for field in row ) for row in cursor )
    self.send(answer.decode('utf-8').encode('cp1251')) if answer else self.send('NONE')
    connection.commit()
   except Exception as ex:
    print ex
    self.send('FAIL') 
  self.close()

sql = TcpServer( ADDR, SQLHandler)
loop()