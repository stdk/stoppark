#!/bin/python
# -*- coding: utf8 -*-
import config

from viewer import Viewer
from editor import Editor
from http import register_handler,runserver
from models import GStatus,LStatus,Card,Ticket,Config,Tariff,Events,Payment

register_handler('lstatus', Viewer( LStatus.data_provider() ) )
register_handler('card'   , Editor( Card   .data_provider() ) )
register_handler('gstatus', Viewer( GStatus.data_provider() ) )
register_handler('ticket' , Editor( Ticket .data_provider() ) )
register_handler('config' , Editor( Config .data_provider(invert=True) ) )
register_handler('tariff' , Editor( Tariff .data_provider() ) )
register_handler('events' , Viewer( Events .data_provider() ) )
register_handler('payment', Viewer( Payment.data_provider() ) )

runserver()
