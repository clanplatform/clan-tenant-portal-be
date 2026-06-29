from fastapi import HTTPException, status


class TenantNotFound(HTTPException):
    def __init__(self, detail: str = "Tenant not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TenantAlreadyExists(HTTPException):
    def __init__(self, detail: str = "Tenant already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class TenantInvalidStatus(HTTPException):
    def __init__(self, detail: str = "Invalid tenant status"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
