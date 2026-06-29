from fastapi import HTTPException


class ApiKeyNotFound(HTTPException):
    def __init__(self, key_id: str = ""):
        detail = f"API key '{key_id}' not found" if key_id else "API key not found"
        super().__init__(status_code=404, detail=detail)
