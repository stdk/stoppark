# -*- coding: utf8 -*-
import cherrypy
from commands import getoutput
from string import Template
from viewer import Viewer
from editor import Editor
from models import GStatus,LStatus,Card,TicketView,Config,Tariff,EventsView,PaymentView,Terminal

#hack to make ResponseEncoder work correctly when deciding charset in Content-Type header
cherrypy.lib.encoding.ResponseEncoder.encoding = 'utf-8'

settings = { 
	'global': {
		'server.socket_port' : 2000,
		'server.socket_host': getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:],
		'server.socket_file': "",
		'server.socket_queue_size': 5,
		'server.protocol_version': "HTTP/1.1",
		'server.log_to_screen': True,
		'server.log_file': "",
		'server.reverse_dns': False,
		'server.thread_pool': 5,
		'server.environment': "development",
		#'tools.encode.on':True, 
		#'tools.encode.encoding':'utf8',
		# 'tools.sessions.on': True
	}
}
cherrypy.config.update(settings)

class Root(object):
 @cherrypy.expose
 # @cherrypy.tools.response_headers([('Content-Type', 'text/html; charset=utf-8')])
 def index(self):
  cherrypy.response.headers['Content-Type'] = "text/html; charset=utf-8" 
  args = { 'host' : cherrypy.server.socket_host, 'user' : 'admin', 'level' : 'Администратор' }
  return Template(open('ui/index.html').read()).substitute(**args)

root = Root()

root.gstatus  = Viewer( GStatus.data_provider() )
root.lstatus  = Viewer( LStatus.data_provider() )
root.card     = Editor( Card.data_provider() )
root.ticket   = Viewer( TicketView.data_provider() )
root.config   = Editor( Config.data_provider(invert=True) )
root.events   = Viewer( EventsView.data_provider() )
root.payment  = Viewer( PaymentView.data_provider() )
root.terminal = Editor( Terminal.data_provider() )
root.tariff   = Editor( Tariff.data_provider() )

cherrypy.quickstart(root)