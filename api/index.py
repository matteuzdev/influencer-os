import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Importa a instância FastAPI ASGI
from server import app as fastapi_app

class VercelPathMiddleware:
    """
    Middleware que restaura o path original requisitado quando o Vercel
    faz rewrite interno para /api/index.py.
    """
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            # Vercel envia x-matched-path com o caminho original requisitado (ex: / ou /api/personas)
            matched_path = headers.get(b"x-matched-path") or headers.get(b"x-vercel-forwarded-path")
            if matched_path:
                decoded = matched_path.decode("utf-8").split("?")[0]
                if decoded and not decoded.endswith(".py"):
                    scope["path"] = decoded

        await self.asgi_app(scope, receive, send)

app = VercelPathMiddleware(fastapi_app)
