from fastapi import FastAPI, status, HTTPException, Request
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from enum import Enum
from typing import Optional

carriers = [
    {"id": 1, "code": "GHN", "name": "Giao Hang Nhanh", "max_weight_capacity": 5000, "status": "ACTIVE"},
    {"id": 2, "code": "GHTK", "name": "Giao Hang Tiet Kiem", "max_weight_capacity": 3000, "status": "ACTIVE"},
    {"id": 3, "code": "VTP", "name": "Viettel Post", "max_weight_capacity": 10000, "status": "SUSPENDED"}
]

shipments = [
    {
        "id": 1,
        "carrier_id": 1,
        "order_reference": "ORD-2026-001",
        "total_weight": 4200,
        "dispatch_date": "2026-07-01",
        "shift": "MORNING"
    }
]

app = FastAPI()

class StatusEnum(str, Enum):
    active = "ACTIVE"
    inactive = "INACTIVE"
    suspended = "SUSPENDED"

class Carrier(BaseModel):
    id: Optional[int] = None
    code: str = Field(...)
    name: str = Field(...,min_length = 3)
    max_weight_capacity: int = Field(...,gt = 0)
    status: StatusEnum = Field(default=StatusEnum.suspended)


@app.post("/carriers", response_model=Carrier, status_code=status.HTTP_201_CREATED)
def add_carrier(carrier: Carrier):
    if any(c["code"] == carrier.code for c in carriers):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code bị trùng"
        )
    carrier.id = carriers[-1]["id"] + 1
    new_carrier = carrier.model_dump()
    carriers.append(new_carrier)
    return carrier