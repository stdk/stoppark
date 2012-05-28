from database import DataStructure

class Subscription(DataStructure):
 def __init__(self,**kwargs):
  self.attributes = ['id','name','mark','color','number','issued','valid','place']
  try: self.id = kwargs['id']
  except KeyError: self.id = ''
  self.name = ''
  self.mark = ''
  self.color = ''
  self.number = ''
  self.issued = ''
  self.valid = ''
  self.place = ''
