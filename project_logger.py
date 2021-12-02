import logging.config
import colorlog

LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'brief': { 
            'format': '[%(levelname)s] %(name)s: %(message)s'
        },
        'colored': {
			'()': 'colorlog.ColoredFormatter',
            'format': '[%(log_color)s%(levelname)-s%(reset)s] %(white)s%(message)s'

		},
    },
    'handlers': { 
        'default': { 
            'level': 'WARNING',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        
        },
        'secondary': { 
            'level': 'INFO',
            'formatter': 'colored',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr        
        },
    },
    'loggers': { 
        '': {  # root logger
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'get_ssids': { 
            'handlers': ['secondary'],
            'level': 'INFO',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
    } 
}

# Run once at startup:
logging.config.dictConfig(LOGGING_CONFIG)


