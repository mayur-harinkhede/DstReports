import sys
import os

# Add root directory to sys.path so app and internal modules can be imported
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# WSGI Middleware to ensure Vercel rewrites map cleanly to Flask endpoints
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        # Strip internal Vercel function routing prefixes if present
        for prefix in ['/api/index.py', '/api/index', '/api']:
            if path.startswith(prefix):
                path = path[len(prefix):]
                break
        if not path or path == '':
            path = '/'
        environ['PATH_INFO'] = path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
