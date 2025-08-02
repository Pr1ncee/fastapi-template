from enum import Enum, unique
from functools import lru_cache
from operator import attrgetter

from src.core.config import general_config


@unique
class BaseEnum(Enum):
    @classmethod
    @lru_cache(general_config.LRU_CACHE_MAX_SIZE)
    def values(cls) -> tuple:
        return tuple(map(attrgetter("value"), cls))

    @classmethod
    @lru_cache(general_config.LRU_CACHE_MAX_SIZE)
    def names(cls) -> tuple:
        return tuple(map(attrgetter("name"), cls))

    @classmethod
    @lru_cache(general_config.LRU_CACHE_MAX_SIZE)
    def items(cls) -> tuple:
        return tuple(zip(cls.values(), cls.names(), strict=False))

    @classmethod
    @lru_cache(general_config.LRU_CACHE_MAX_SIZE)
    def members(cls) -> dict:
        return dict(cls.items())

    @classmethod
    def dict(cls) -> dict:
        return {c.name: c.value for c in cls}
