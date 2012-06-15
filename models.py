from database import Model,TextField,IntField

from time import strftime

class LStatus(Model):
 LStatus = TextField(visible=False)
 id = IntField(primary_key=True,visible=False)
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

 Card = TextField(visible=False)
 id = IntField(primary_key=True)
 Type = IntField()
 CardID = TextField()
 DTReg = TextField()
 DTEnd = TextField()
 DriveName = TextField()
 DriveSName = TextField()
 DriveFam = TextField()
 DrivePhone = TextField()
 CarGosNom = TextField()
 CarModel = TextField()
 CarColor = TextField()
 Status = IntField()
 TarifType = IntField()
 TarifPrice = IntField()
 TarifSumm = IntField()

class GStatus(Model):
 LStatus = TextField(visible=False)
 id = IntField(primary_key=True,visible=False)

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
 id = IntField(primary_key=True)

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
 id = IntField()
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
 id = TextField(primary_key=True,visible=False)
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
 id = IntField(primary_key=True)
 name = TextField()
 password = TextField()
 level = IntField()

 @staticmethod
 def prepare():
  from hashlib import md5
  from base64 import b64encode as enc
  User.create()
  User(name='admin',password=enc(md5('pass').digest()),level=2).save()
  User(name='cs',password=enc(md5('sv4metro').digest()),level=1).save()
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

class EventsView(Model):
 EventName = TextField()
 DateTime = TextField()
 Terminal = IntField()
 Direction = TextField()
 Reason = TextField()
 FreePlaces = IntField() 

if __name__ == "__main__":
  from sys import argv
  [ eval(arg) for arg in argv[1:] ]
