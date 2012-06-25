import logging
import logging.config

configdict = {
 'version': 1,    # Configuration schema in use; must be 1 for now
 'formatters': {
     'standard': {
         'format': ('%(asctime)s %(name)-15s '
                    '%(levelname)-8s %(message)s')}},

 'handlers': {'main': {'backupCount': 10,
                       'class': 'logging.handlers.RotatingFileHandler',
                       'filename': 'logs/log',
                       'formatter': 'standard',
                       'level': 'DEBUG',
                       'maxBytes': 1000000}
             },
 # Specify properties of the root logger
 'root': {
          'level': 'DEBUG',
          'handlers': ['main']
 },
}

# Set up configuration
#if hasattr(logging.config,'dictConfig'): logging.config.dictConfig(configdict)
#else:
# FORMAT = '%(asctime)s %(name)-15s %(levelname)-8s %(message)s'
# logging.basicConfig(format=FORMAT,level=logging.INFO)
