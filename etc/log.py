LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '%(asctime)s [%(process)5d] (%(name)s) %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'logfile': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'PLACEHOLDER',
            'when': 'W6',
            'backupCount': 26,
            'level': 'DEBUG',
            'formatter': 'basic',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'basic',
            'stream': 'ext://sys.stdout',
        },
    },
    'root': {
        # most verbose here, let handlers be the filters
        'level': 'DEBUG',
        'handlers': ['logfile', 'console'],
    },
}


def logging_config(logfile_path, logfile_level='debug', console_level='debug'):
    """Returns a copy of the logging configuration dict with the args set."""
    cfg = dict(LOGGING_CONFIG)
    cfg['handlers']['logfile']['filename'] = logfile_path
    cfg['handlers']['logfile']['level'] = logfile_level.upper()
    cfg['handlers']['console']['level'] = console_level.upper()
    return cfg
