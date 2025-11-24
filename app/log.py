import structlog
from structlog import processors
from structlog.typing import Processor

from app.settings import settings

SHARED_PROCESSORS: list[Processor] = [
    structlog.contextvars.merge_contextvars,
    processors.CallsiteParameterAdder(
        [
            processors.CallsiteParameter.MODULE,
            processors.CallsiteParameter.FUNC_NAME,
            processors.CallsiteParameter.LINENO,
            processors.CallsiteParameter.PROCESS,
            processors.CallsiteParameter.THREAD,
            processors.CallsiteParameter.THREAD_NAME,
        ]
    ),
    processors.add_log_level,
    processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    processors.TimeStamper(fmt="iso", utc=True),
]


def init_log() -> None:
    if settings.USE_CONSOLE_LOG:
        ps = SHARED_PROCESSORS + [
            structlog.dev.ConsoleRenderer()
        ]
    else:
        ps = SHARED_PROCESSORS + [
            processors.dict_tracebacks,
            processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=ps,
        wrapper_class=structlog.make_filtering_bound_logger(
            settings.LOG_LEVEL
        ),
    )
