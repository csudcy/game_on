
config = {
    'db': {
        'name': 'game_on',
        'host': '127.0.0.1',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',
    },
    'cherrypy': {
        'host': '0.0.0.0',
        'port': 8080,
        'static_timeout_hours': 0,
    },
    'logging': {
        'log_to_console': True,
        'log_level': 'DEBUG',
        'access_logging_enabled': False,
        'disabled_loggers': [],
    },
    'team': {
        'folder': 'C:/dev/game_on/teams'
    },
    'match': {
        'folder': 'C:/dev/game_on/matches'
    },
}
