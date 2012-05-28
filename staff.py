from database import DataStructure

class Staff(DataStructure):
 def __init__(self,**kwargs):
  self.attributes = ['id','ptype','active','org','name','tel','mark','color','number','place','issued','valid','card']
  try: self.id = kwargs['id']
  except KeyError: self.id = ''
  self.ptype = ''
  self.active = ''
  self.org = ''
  self.name = ''
  self.tel = ''
  self.mark = ''
  self.color = ''
  self.number = ''
  self.place = ''
  self.issued = ''
  self.valid = ''
  self.card = ''


