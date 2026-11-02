import contextvars, time, uuid
from contextlib import contextmanager
import structlog


#Initializing the contextvars
_ctx=contextvars.ContextVar("finsight_request_ctx",default=None)
log=structlog.get_logger("finsight.request")

def start(**kwargs):
    d = dict(kwargs)
    _ctx.set(d)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=d.get("request_id"))
    return d

def set_fields(**kw):
    d = _ctx.get()
    if d is not None:
        d.update(kw)

def incr(key):
    d = _ctx.get()
    if d is not None:
        d[key] = d.get(key, 0) + 1

def emit(ctx, latency_ms):
    failed = ctx.get("error_type") or ctx.get("status", 200) >= 500
    (log.error if failed else log.info)("request_summary", latency_ms=latency_ms, **ctx)

@contextmanager
def request_scope(source, **fields):
    """For non-HTTP entry points (MCP tools, scripts)."""
    ctx = start(request_id=uuid.uuid4().hex, source=source, **fields)
    t = time.perf_counter()
    try:
        yield ctx
    except Exception as e:
        ctx["error_type"] = type(e).__name__
        raise
    finally:
        emit(ctx, round((time.perf_counter() - t) * 1000))