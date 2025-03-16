from app import app
import logging.config
import os

if not os.path.exists("Logs"):
    os.makedirs("Logs")

if not os.path.exists('app/static/img/avatars'):
    os.makedirs('app/static/img/avatars')

# system log
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(asctime)s - %(name)s -"
                                 " %(levelname)s - %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "info_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": "Logs/info.log",
                "maxBytes": 10485760,
                "backupCount": 50,
                "encoding": "utf8",
            },
            "error_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "simple",
                "filename": "Logs/errors.log",
                "maxBytes": 10485760,
                "backupCount": 20,
                "encoding": "utf8",
            },
            "debug_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": "Logs/debug.log",
                "maxBytes": 10485760,
                "backupCount": 50,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "my_module": {"level": "ERROR",
                          "handlers": ["console", "error_file_handler"],
                          "propagate": "no"}
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["error_file_handler",
                         "debug_file_handler",
                         "info_file_handler"],
        },
    }
)

# run the app
app.run(debug=True)
