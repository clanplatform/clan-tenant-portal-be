from fastapi import HTTPException, status


class SubscriptionNotFound(HTTPException):
    def __init__(self, detail: str = "Tenant subscription not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class SubscriptionAlreadyExists(HTTPException):
    def __init__(self, detail: str = "An active subscription already exists for this tenant"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
