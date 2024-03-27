import atexit
import datetime as dt
import json
import logging
import logging.handlers
from ssl import SSLContext
from typing import Tuple, override

import httpx

_LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in _LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class WarningAndBelowFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO


class ErrorAndAboveFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.ERROR


class SeparateThreadQueueHandler(logging.handlers.QueueHandler):
    def __init__(self):
        super().__init__()
        self.listener.start()
        atexit.register(self.listener.stop)


class CustomHttpHandler(logging.Handler):
    _client: httpx.Client

    def __init__(
        self,
        url: str,
        secure: bool = False,
        credentials: Tuple[str, str] | None = None,
        context: SSLContext | None = None,
        level: int | str = 0,
    ) -> None:
        super().__init__(level)
        self._get_connection(url, secure, credentials, context)
        return

    def _get_connection(
        self,
        url: str,
        secure: bool = False,
        credentials: Tuple[str, str] | None = None,
        context: SSLContext | None = None,
    ) -> None:
        self._client = httpx.Client(
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return

    def emit(self, record: logging.LogRecord) -> None:
        self._client.put(json=record.__dict__)
        return
