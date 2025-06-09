from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

class OperationArgs(BaseModel):
    op1: float
    op2: float

class CalculatorRequest(BaseModel):
    id: str
    operation: Literal["sum", "sub", "mult", "div"]
    args: OperationArgs

class CalculatorResponse(BaseModel):
    id: str
    status: bool
    result: Optional[float] = None
    error: Optional[str] = None

    @validator('error')
    def validate_error(cls, v, values):
        if 'status' in values:
            if values['status'] and v is not None:
                raise ValueError("Error field should be None when status is True")
            if not values['status'] and v is None:
                raise ValueError("Error field is required when status is False")
        return v

    @validator('result')
    def validate_result(cls, v, values):
        if 'status' in values:
            if values['status'] and v is None:
                raise ValueError("Result field is required when status is True")
            if not values['status'] and v is not None:
                raise ValueError("Result field should be None when status is False")
        return v

    def model_dump(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        if d['status']:
            d.pop('error', None)
        else:
            d.pop('result', None)
        return d 