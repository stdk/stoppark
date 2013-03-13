# -*- coding: utf8 -*-
from viewer import Viewer
from editor import Editor
from http import register_handler,runserver
from models import GStatus,LStatus,Card,TicketView,Config,Tariff,EventsView,PaymentView,Terminal,User
from database_upload import DatabaseUploader
from server_side import ServerSideEditor

register_handler('/lstatus' ,  Viewer( LStatus.data_provider() ) )
register_handler('/card'    ,  Editor( Card.data_provider() ) )
register_handler('/gstatus' ,  Viewer( GStatus.data_provider() ) )
register_handler('/ticket'  ,  Viewer( TicketView.data_provider() ) )
register_handler('/config'  ,  Editor( Config.data_provider(invert=True) ) )
register_handler('/tariff'  ,  Editor( Tariff.data_provider() ) )
register_handler('/events'  ,  Viewer( EventsView.data_provider() ) )
register_handler('/payment' ,  Viewer( PaymentView.data_provider() ) )
register_handler('/terminal',  Editor( Terminal.data_provider() ) )
register_handler('/user'    ,  Editor( User.data_provider(), secure = True ) )
register_handler('/upload'  ,  DatabaseUploader() )

runserver()
