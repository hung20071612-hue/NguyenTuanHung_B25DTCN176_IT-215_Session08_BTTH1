from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

app = FastAPI()
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

class Carrier(BaseModel):
    code: str
    name: str = Field(..., min_length=3)
    max_weight_capacity: int = Field(..., gt=0)
    status: str

class Shipment(BaseModel):
    carrier_id: int
    order_reference: str
    total_weight: int = Field(..., gt=0)
    dispatch_date: date
    shift: str

@app.post("/carriers", status_code=status.HTTP_201_CREATED)
def add_carrier(carrier: Carrier):
    for c in carriers:
        if c["code"].upper() == carrier.code.upper():
            raise HTTPException(status_code=400, detail="Mã code đã tồn tại")
        
    new_carrier = {
        "id": len(carriers) + 1,
        "code": carrier.code,
        "name": carrier.name,
        "max_weight_capacity": carrier.max_weight_capacity,
        "status": carrier.status
    }
    carriers.append(new_carrier)
    return {
        "message": "Thêm đối tác thành công",
        "data": carriers
    }

@app.get("/carriers")
def list_carriers(keyword: Optional[str] = Query(None), status_filter: Optional[str] = Query(None),min_weight: Optional[int] = Query(None)):
    results = carriers
    if keyword:
        results = [c for c in results if keyword.lower() in c["code"].lower() or keyword.lower() in c["name"].lower()]
    if status_filter:
        results = [c for c in results if c["status"] == status_filter]
    if min_weight:
        results = [c for c in results if c["max_weight_capacity"] >= min_weight]
        return results
    
@app.get("/carriers/{carrier_id}")
def get_carrier(carrier_id: int):
    carrier = next((c for c in carriers if c["id"] == carrier_id), None)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    return carrier

@app.put("/carriers/{carrier_id}")
def update_carrier(carrier_id: int, carrier_update: Carrier):
    carrier = next((c for c in carriers if c["id"] == carrier_id), None)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    carrier["code"] = carrier_update.code
    carrier["name"] = carrier_update.name
    carrier["max_weight_capacity"] = carrier_update.max_weight_capacity
    carrier["status"] = carrier_update.status    
    return carrier

@app.delete("/carriers/{carrier_id}")
def delete_carrier(carrier_id: int):
    carrier = next((c for c in carriers if c["id"] == carrier_id), None)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    carriers.remove(carrier)
    return {
        "message": "Xóa đối tác thành công",
        "data": carriers
    }
    
    
@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(shipment: Shipment):
    matches = [c for c in carriers if c["id"] == shipment.carrier_id]
    if not matches:
        raise HTTPException(status_code=404, detail="Carrier không tồn tại")
    carrier = matches[0]
    if carrier["status"] != "ACTIVE":
        raise HTTPException(status_code=400, detail="Đối tác không hoạt động")
    if shipment.total_weight <= 0:
        raise HTTPException(status_code=400, detail="Khối lượng phải lớn hơn 0")
    if shipment.total_weight > carrier["max_weight_capacity"]:
        raise HTTPException(status_code=400, detail="Khối lượng vượt quá tải trọng cho phép")
    for s in shipments:
        if (s["carrier_id"] == shipment.carrier_id and s["dispatch_date"] == str(shipment.dispatch_date) and s["shift"] == shipment.shift):
            raise HTTPException(status_code=400, detail="Đối tác đã có chuyến giao hàng trong ca này")

    new_shipment = {
        "id": len(shipments) + 1,
        "carrier_id": shipment.carrier_id,
        "order_reference": shipment.order_reference,
        "total_weight": shipment.total_weight,
        "dispatch_date": str(shipment.dispatch_date),
        "shift": shipment.shift,
    }
    shipments.append(new_shipment)
    return {
        "message": "Thêm chuyến giao hàng thành công",
        "data": shipments
    }

@app.get("/shipments")
def list_shipments():
    return shipments