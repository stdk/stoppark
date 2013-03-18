# -*- coding: utf8 -*-

from database import Model,TextField,IntField,VirtualField
from time import strftime
from hashlib import md5
from base64 import b64encode as enc

class LStatus(Model):
 LStatus = TextField(visible=False)
 ID = IntField(primary_key=True)
 ReportHKol = IntField()
 ReportHSum = IntField()
 ReportDKol = IntField() 
 ReportDSum = IntField()
 ReportMKol = IntField()
 ReportMSum = IntField()
 ReportStKol = IntField()
 ReportStSum = IntField()
 ReportTime = TextField()
 ParkManLast = TextField()
 ParkManCur = TextField()
 PrintedAll = IntField()
 PrintedSmena = IntField()

class Card(Model):
 def __init__(self):
  self.Card = 'Card'
  self.DTReg = strftime('%d-%m-%y') 
  self.Type = 2
  self.Status = 1

 Card = TextField(visible=False)
 ID = IntField(primary_key=True)
 Type = IntField(visible=False)

 def get_type(self):
  return {0:'служебный',1:'разовый',2:'клиент',3:'кассир',4:'админ'}.get(self.Type,'unknown')
 def set_type(self,value):
  self.Type = value
 VirtualType = VirtualField(get_type,set_type)

 CardID = TextField()
 DTReg = TextField()
 DTEnd = TextField()
 DTIn = TextField()
 DTOut = TextField()
 DriveName = TextField()
 DriveSName = TextField()
 DriveFam = TextField()
 DrivePhone = TextField()
 CarGosNom = TextField()
 CarModel = TextField()
 CarColor = TextField()
 Status = IntField(visible=False)

 def get_status(self):
  return {
    1: 'разрешен',
    2: 'утерян',
    3: 'просрочен',
    4: 'запрещен',
    5: 'выехал',
    6: 'вьехал' }.get(self.Status,'')
 def set_status(self,value):
  self.Type = value
 VirtualStatus = VirtualField(get_status,set_status)

 TarifType = IntField()
 TarifPrice = IntField(visible=False)
 TarifSumm = IntField(visible=False)

class GStatus(Model):
 LStatus = TextField(visible=False)
 ID = IntField(primary_key=True,visible=False)

 InCounterWhole = IntField()
 InCounterYear = IntField()
 InCounterMonth = IntField()
 InCounterDay = IntField()
 InCounterSmena = IntField()

 OutCounterWhole = IntField()
 OutCounterYear = IntField()
 OutCounterMonth = IntField()
 OutCounterDay = IntField()
 OutCounterSmena = IntField()

 PayedWhole = IntField()
 PayedYear = IntField()
 PayedMonth = IntField()
 PayedDay = IntField()
 PayedSmena = IntField()

 PayedPost = IntField()
 PayedSingle = IntField()

 Year = IntField(visible=False)

 PlaceFree = IntField()
 PlaceAll = IntField()

class Ticket(Model):
 def __init__(self):
  self.Ticket = 'Ticket'
 Ticket = TextField(visible=False)
 ID = IntField(primary_key=True)
 BAR = TextField()
 TypeTarif = IntField()
 PriceTarif = IntField()
 Summ = IntField()
 SummDopl = IntField()
 TimeIn = TextField()
 TimeOut = TextField()
 TimeCount = TextField()
 TimeDopl = TextField()
 Status = IntField()

class TicketView(Model):
 ID = IntField()
 BAR = TextField()
 TypeTarif = IntField()
 PriceTarif = IntField()
 Summ = IntField()
 SummDopl = IntField()
 TimeIn = TextField()
 TimeOut = TextField()
 TimeCount = TextField()
 TimeDopl = TextField()
 Status = IntField()

class Config(Model):
 def __init__(self):
  self.Config = 'Config'
 Config = TextField(visible=False)
 ID = TextField(primary_key=True,visible=False)
 PlaceNum = IntField()
 FreeTime = IntField()
 PayTime = TextField()
 TarifName1 = TextField()
 TarifName2 = TextField()
 TarifName3 = TextField()
 TarifName4 = TextField()
 UserStr1 = TextField()
 UserStr2 = TextField()
 UserStr3 = TextField()
 UserStr4 = TextField()
 UserStr5 = TextField()
 UserStr6 = TextField()
 UserStr7 = TextField()
 UserStr8 = TextField()

class User(Model):
 id       = IntField(primary_key=True)
 name     = TextField()
 
 password = TextField(visible=False)
 @VirtualField
 def v_password(self):
  return '**********'  
 @v_password.setter 
 def v_password(self,value):
  self.password = enc(md5(value).digest())

 level = IntField(visible=False)
 @VirtualField
 def v_level(self):
  return { 1 : 'Пользователь', 2 : 'Администратор' }.get(self.level,'unknown')
 @v_level.setter
 def v_level(self,value):
  self.level = value

 def __str__(self):
  return '{0}:{1}:{2}'.format(self.name,self.password,self.level)
 __repr__ = __str__

 @staticmethod
 def prepare():
  User.create()
  User(name='admin',password='pass',level=2).save()
  User(name='cs',password='sv4metro',level=1).save()
  print User.filter(name='admin')
  print User.filter(name='cs')
  def __repr__(self):
   return '%s : %s' % (self.name,self.password)

class Tariff(Model):
 id = IntField(primary_key=True)
 Name = TextField()
 Type = IntField()
 Interval = IntField()
 Cost = TextField()
 ZeroTime = TextField()
 MaxPerDay = TextField()
 Note = TextField() 

class Payment(Model):
 id = IntField(primary_key=True,visible=False)
 Payment = TextField()
 Type = IntField()
 Kassa = IntField()
 Operator = TextField()
 DTime = TextField() 
 TalonID = TextField()
 Status = IntField()
 TarifType = IntField(visible=False)
 Tarif = IntField()
 TarifKol = IntField()
 DTIn = TextField()
 DTOut = TextField()
 Summa = IntField()

class PaymentView(Model):
 Payment = TextField()
 TalonID = TextField()
 Type = IntField()
 Kassa = IntField()
 Operator = TextField()
 DTime = TextField() 
 Status = IntField()
 Tarif = IntField()
 TarifKol = IntField()
 DTIn = TextField()
 DTOut = TextField()
 Summa = IntField() 

class Events(Model):
 def __init__(self):
  self.Event = 'Event'
  
 Event = TextField(visible=False) 
 ID = IntField(primary_key=True,visible=False)
 EventName = TextField()
 DateTime = TextField()
 Terminal = IntField()
 Direction = TextField()
 Reason = TextField()
 FreePlaces = IntField()
 Card = TextField()

class EventsView(Model):
 EventName = TextField()
 DateTime = TextField()
 Terminal = IntField()
 Direction = TextField()
 Reason = TextField()
 FreePlaces = IntField() 
 Card = TextField()

class Terminal(Model):
 id = IntField(primary_key=True)
 terminal_id = IntField() 
 title = TextField()

def test_models():
 User.all()
 GStatus.all()
 LStatus.all()
 Card.all()
 Config.all()
 Tariff.all() 

if __name__ == "__main__":
  from sys import argv
  [ eval(arg) for arg in argv[1:] ]
