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
            
            # Debug endpoint direto
            if b"/debug-info" in scope.get("raw_path", b"") or b"debug" in headers.get(b"x-matched-path", b""):
                header_dict = {k.decode("latin1", "ignore"): v.decode("latin1", "ignore") for k, v in headers.items()}
                body = str({"headers": header_dict, "raw_scope": str(scope)}).encode("utf-8")
                await send({"type": "http.response.start", "status": 200, "headers": [[b"content-type", b"application/json"]]})
                await send({"type": "http.response.body", "body": body})
                return

            # Procura em todos os possíveis headers de proxy da Vercel
            for h in [b"x-matched-path", b"x-vercel-forwarded-path", b"x-forwarded-uri", b"x-invoke-path", b"x-now-route-matches"]:
                val = headers.get(h)
                if val:
                    decoded = val.decode("utf-8", "ignore").split("?")[0]
                    if decoded and not decoded.endswith(".py") and not decoded == "/api/index":
                        scope["path"] = decoded
                        break

        await self.asgi_app(scope, receive, send)

app = VercelPathMiddleware(fastapi_app)
