#!/bin/python
from structure import *
from commands import getoutput
import asyncore
import socket
from httplib import HTTPConnection
from urllib import urlopen,urlencode
import sqlite3

def enc(s):
 try:
  return s.encode('cp1251')
 except Exception as e:
  print e
  return 'None'

def dec(s):
 try:
  return s.decode('cp1251')
 except Exception as e:
  print e
  return 'None'

conn = sqlite3.connect('data/db.db3')
conn.create_function('enc',1,enc)
conn.create_function('dec',1,dec)
conn.text_factory = str

HOST = getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
PORT = 101
BASE_PORT = 2000

class TcpServer(asyncore.dispatcher):
 def __init__(self, (host, port), handler):
  asyncore.dispatcher.__init__(self)
  self.handler = handler

  self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
  self.set_reuse_addr()
  self.bind((host, port))
  self.listen(5)
  print 'Listen on %s:%s' % (host,port)

 def handle_accept(self):
  pair = self.accept()
  if pair is None:
   print 'handle_accept: None'
   return
  else:
   sock, addr = pair
   print 'Incoming connection from %s' % repr(addr)
   handler = self.handler(sock)

class SQLHandler(asyncore.dispatcher_with_send):
 def handle_read(self):
  data = self.recv(1024)
  if data:
   print data
   try:
    c = conn.cursor()
    c.execute(data)
    counter = 0
    for row in c:
     counter += 1
     self.send('|'.join( str(field) for field in row )+'\n')
    if not counter: self.send('NONE\n')    
    conn.commit()
   except Exception as e:
    print e
    self.send('FAIL\n') 
  self.close()

sql = TcpServer( (HOST,PORT),SQLHandler)
asyncore.loop()
