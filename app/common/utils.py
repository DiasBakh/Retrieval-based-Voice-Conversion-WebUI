import hashlib
import timeit
from pathlib import Path

import wrapt
from fastapi import APIRouter
from loguru import logger

from settings import settings


def time_func(log_level: str = 'INFO'):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        start = timeit.default_timer()
        out = wrapped(*args, **kwargs)
        delta = timeit.default_timer() - start
        if instance:
            func_name = f'{instance.__class__.__name__}.{wrapped.__name__}'
        else:
            func_name = wrapped.__name__
        logger.log(log_level, "Timing|{}: {:.4f}", func_name, delta)
        return out

    return wrapper


def create_router(filename: str, **kwargs) -> APIRouter:
    folder_name = Path(filename).parent.name

    return APIRouter(
        prefix=f'/{folder_name}',
        tags=[folder_name],
        **kwargs
    )


def get_md5(obj) -> str:
    return hashlib.md5(str(obj).encode()).hexdigest()


def get_persisted(text: str) -> str:
    folder = settings.storage_folder / 'persisted'
    folder.mkdir(exist_ok=True)
    key = get_md5(text)
    path = folder / f'{key}.txt'
    logger.info(path)
    if path.exists():
        return path.read_text()
    else:
        path.write_text(text)
        return text
