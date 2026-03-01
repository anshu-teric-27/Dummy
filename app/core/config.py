from functools import lru_cache


class Settings:
    project_name: str = "Python Demo API"
    api_v1_prefix: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()

