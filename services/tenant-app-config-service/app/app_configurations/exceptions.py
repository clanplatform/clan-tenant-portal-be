from fastapi import HTTPException


class ConfigNotFound(HTTPException):
    def __init__(self, config_key: str = ""):
        detail = f"Configuration key '{config_key}' not found" if config_key else "Configuration not found"
        super().__init__(status_code=404, detail=detail)
