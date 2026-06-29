from fastapi import HTTPException


class WebhookNotFound(HTTPException):
    def __init__(self, webhook_id: str = ""):
        detail = f"Webhook '{webhook_id}' not found" if webhook_id else "Webhook not found"
        super().__init__(status_code=404, detail=detail)
