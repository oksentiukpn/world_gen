import logging

from config import Config
from flask import Flask

from app.sockets import socketio


def create_app(config=Config):
    app = Flask(__name__)

    app.config.from_object(config)
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    from app.main.routes import main

    app.register_blueprint(main)

    # Initialize socketio with the app
    socketio.init_app(app)

    return app
