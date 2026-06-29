from fastapi import HTTPException, status


class PlanNotFound(HTTPException):
    def __init__(self, detail: str = "Subscription plan not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PlanAlreadyExists(HTTPException):
    def __init__(self, detail: str = "Subscription plan with this code already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
