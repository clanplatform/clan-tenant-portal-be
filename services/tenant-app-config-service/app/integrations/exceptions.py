from fastapi import HTTPException


class IntegrationNotFound(HTTPException):
    def __init__(self, integration_id: str = ""):
        detail = (
            f"Integration '{integration_id}' not found"
            if integration_id
            else "Integration not found"
        )
        super().__init__(status_code=404, detail=detail)
