import logging

from pythonjsonlogger.json import JsonFormatter


def setup_logger() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()

    log_handler = logging.StreamHandler()
    formatter = JsonFormatter(
        fmt="[%(asctime)s %(levelname)-5s] %(message)s [%(filename)s:%(lineno)d]",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    log_handler.setFormatter(formatter)

    root_logger.addHandler(log_handler)

    # Set the logging level to "Critical" for 'asyncio' module to disable fake warnings
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)

    # Application logger
    app_logger = logging.getLogger(__name__)

    app_logger.propagate = True
    app_logger.setLevel(logging.INFO)
    app_logger.handlers.clear()

    # Uvicorn loggers
    uvicorn_loggers = [
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.access"),
        logging.getLogger("uvicorn.error"),
    ]

    for uvicorn_logger in uvicorn_loggers:
        uvicorn_logger.propagate = True
        uvicorn_logger.setLevel(logging.INFO)
        uvicorn_logger.handlers.clear()
