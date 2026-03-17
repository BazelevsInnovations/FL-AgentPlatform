from functools import lru_cache

from fl_platform.config import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()
