"""
Main application entrypoint module to start up webserver
"""
import logging
from werkzeug.serving import run_simple
from .wsgi import application

logging.getLogger().setLevel(logging.INFO)
run_simple('0.0.0.0', 8080, application, use_reloader=True)
