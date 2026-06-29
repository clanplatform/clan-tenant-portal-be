from fastapi import HTTPException, status


class InvoiceNotFound(HTTPException):
    def __init__(self, detail: str = "Invoice not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvoiceAlreadyExists(HTTPException):
    def __init__(self, detail: str = "Invoice with this number already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
