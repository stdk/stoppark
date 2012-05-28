from database import DataStructure

class BoardConfig(DataStructure):
 def __init__(self,**kwargs):
  self.attributes = ['gates','tickets','mode','lcd_contract','lcd_bright','dev','place_num','free_time','pay_time']
  self.val = ''
  self.gates = ''
  self.tickets = ''
  self.tarif_type = ''
  self.tarif = ''
  self.startup_timer = ''
  self.mode = ''
  self.lcd_contrast = ''
  self.lcd_bright = ''
  self.dev = ''
  self.proc_timeout = ''
  self.in_pulse_timeout = ''
  self.out_pulse_timeout = ''
  self.reserv_timeout = ''
  self.place_num = ''
  self.free_time = ''
  self.pay_time = ''
  self.tempo = ''
  self.tarif_name = ''
  self.user_str = ''

class BoardStatus(DataStructure):
 def __init__(self,**kwargs):
  self.attributes = ['id','post','in_counter','out_counter','payed','pay_post','pay_single','year','place']
  try: self.id = kwargs['id']
  except KeyError: self.id = ''
  self.post = ''
  self.in_counter = ''
  self.out_counter = ''
  self.payed = ''
  self.pay_post = ''
  self.pay_single = ''
  self.year = ''
  self.place = ''
