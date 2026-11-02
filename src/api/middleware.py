import re, time, uuid
from src.observability import context as obs

_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
SKIP_PATHS = {"/health"}


class RequestLogMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] in SKIP_PATHS:
            return await self.app(scope, receive, send)

        headers = dict(scope.get("headers", []))
        incoming = headers.get(b"x-request-id", b"").decode()
        rid = incoming if _SAFE_ID.match(incoming) else uuid.uuid4().hex

        ctx = obs.start(
            request_id=rid,
            source="http",
            method=scope["method"],
            route=scope["path"],
        )
        t0 = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                ctx["status"] = message["status"]
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-request-id", rid.encode())
                ]
            elif (
                message["type"] == "http.response.body"
                and message.get("body")
                and "ttfb_ms" not in ctx
            ):
                ctx["ttfb_ms"] = round((time.perf_counter() - t0) * 1000)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            ctx["error_type"] = type(e).__name__
            ctx.setdefault("status", 500)
            raise
        finally:
            obs.emit(ctx, round((time.perf_counter() - t0) * 1000))