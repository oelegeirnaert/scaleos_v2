# ruff: noqa
"""
ASGI config for ScaleOS project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

# Setup path and settings
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "scaleos"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# Django app
django_application = get_asgi_application()

# Your websocket ASGI app
from config.websocket import websocket_application

# Import the fully async middleware
from scaleos.websites.middleware import AsyncHostValidationMiddleware

# Wrap both HTTP and WebSocket ASGI apps with the middleware
validated_http_app = AsyncHostValidationMiddleware(django_application)
validated_websocket_app = AsyncHostValidationMiddleware(websocket_application)

# ASGI main application router
async def application(scope, receive, send):
    if scope["type"] == "http":
        await validated_http_app(scope, receive, send)
    elif scope["type"] == "websocket":
        await validated_websocket_app(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")
