# -*- coding: utf8 -*-
from ctypes import *

class SizeException(Exception):
 def __init__(self,required,given):
  self.message = 'Insufficcient data: %s/%s' % (required,given)

class InitMixin(object):
 def __init__(self,**kwargs):
  [ setattr(self,key,value) for (key,value) in kwargs.iteritems() if key in [ name for (name,ctype) in self._fields_ ] ]

class BaseStructure(Structure,InitMixin):
 _pack_ = 1
 def __init__(self,**kwargs):
  data = kwargs.get('raw_data',None)
  if data:
   data_length = len(data)
   if data_length > sizeof(self): raise SizeException(sizeof(self),data_length)
   memmove(addressof(self),data,len(data))
  InitMixin.__init__(self,**kwargs)

 short = False
 def __repr__(self):
  if self.short: return '[ ' + ','.join(['%s:%s' % (name,getattr(self,name)) for (name,ctype) in self._fields_]) + ' ]'
  else: return  '\n'.join(['%s:%s' % (name,getattr(self,name)) for (name,ctype) in self._fields_])
 __str__ = __repr__

class TARIF(BaseStructure):
 short = True
 _fields_ = [('summ',c_uint32),
             ('count',c_uint32)]
#print 'TARIF',sizeof(TARIF)

class INTERVAL(BaseStructure):
 short = True
 _fields_ = [('S',c_uint16),
             ('M',c_uint16),
             ('H',c_uint32),
             ('D',c_uint32)]
#print 'INTERVAL',sizeof(INTERVAL)

class TIME(BaseStructure):
 short = True
 _fields_ = [('S',c_uint8),
             ('M',c_uint8),
             ('H',c_uint8),
             ('D',c_uint8),
             ('Mn',c_uint8),  
             ('Y',c_uint16)]
#print 'TIME',sizeof(TIME)

class COUNT(BaseStructure):
 short = True
 _fields_ = [('Whole',c_uint32),
             ('Year',c_uint32),
             ('Month',c_uint32),
             ('Week',c_uint16),
             ('Day',c_uint16),
             ('Smena',c_uint16),
             ('Dir',c_uint8),]
 def __str__(self):
  return '%s | %s | %s | %s | %s | %s' % (self.Smena,self.Day,self.Week,self.Month,self.Year,self.Whole)

 def array(self):
  return [ self.Smena,self.Day,self.Week,self.Month,self.Year,self.Whole]

#print 'COUNT',sizeof(COUNT)

class PLACE(BaseStructure):
 short = True
 _fields_ = [('Free',c_uint32),
             ('All',c_uint32),
             ('flags',c_uint8)]
 def __str__(self):
  return '%i/%i' % (self.Free,self.All)
#print 'PLACE',sizeof(PLACE)

class REPORT(BaseStructure):
 short = True
 _fields_ = [('H',TARIF),
             ('D',TARIF),
             ('M',TARIF),
             ('St',TARIF),
             ('Time',TIME),
             ('ParkManLast',c_char*20), 
             ('ParkManCur',c_char*20)]
#print 'REPORT',sizeof(REPORT)

class PRINT(BaseStructure):
 short = True
 _fields_ = [('All',c_uint32),
             ('Smena',c_uint16)]
#print 'PRINT',sizeof(PRINT)

class STATUS(BaseStructure):
 def __init__(self,**kwargs):
  BaseStructure.__init__(self,**kwargs)
  self.addr = kwargs.get('addr','None')
 
 def array(self):
  return [ self.addr,'%s | %s' % (self.InAdr,self.OutAdr) ] + self.InCounter.array() + self.OutCounter.array() + self.Payed.array() + [ str(self.PayPost), str(self.PaySingle), str(self.Year), str(self.Place) ]

 _fields_ = [('Stat',c_uint8),
             ('InAdr',c_uint8),
             ('OutAdr',c_uint8),
             ('InCounter',COUNT),
             ('OutCounter',COUNT),
             ('Payed',COUNT),
             ('PayPost',c_uint16),
             ('PaySingle',c_uint16),
             ('Year',c_uint8),
             ('Place',PLACE),
             ('Report',REPORT),
             ('Print',PRINT),
             ('CRC',c_uint8)]
#print 'STATUS',sizeof(STATUS)

class BLOCKDATA(Union,InitMixin):
 _fields_ = [('status',STATUS)]
#print 'BLOCKDATA',sizeof(BLOCKDATA)

class BLOCK(BaseStructure):
 _fields_ = [('id',c_char*8),('data',BLOCKDATA)]
#print 'BLOCK',sizeof(BLOCK)

def test_status():
 """
 >>> s = create_connection( (test_server,100) )
 >>> obj = test_status()
 >>> s.send(buffer(obj)[:]) == sizeof(BLOCK)
 True
 """
 status = STATUS(Stat=0xFF,InAdr=74,OutAdr=82,PayPost=108,PaySingle=250,Year=12)
 status.InCounter = COUNT(Smena=1,Day=2,Week=3,Month=4,Year=100,Whole=1000)
 status.OutCounter = COUNT(Smena=1,Day=2,Week=3,Month=4,Year=100,Whole=1000)
 status.Payed = COUNT(Smena=1,Day=2,Week=3,Month=4,Year=100,Whole=1000)

 return BLOCK(id="randomID",data=BLOCKDATA(status=status))

if __name__=='__main__':
 import doctest
 from sys import argv
 from socket import create_connection 
 doctest.testmod(extraglobs={'test_server'       : argv[1],
                             'create_connection' : create_connection })

