from fastapi import APIRouter, HTTPException

from app.models.demo import DemoItem, DemoCreate
from app.services import demo_service


router = APIRouter()


@router.get("/items", response_model=list[DemoItem])
def list_demo_items():
    return demo_service.list_items()


@router.get("/items/{item_id}", response_model=DemoItem)
def get_demo_item(item_id: int):
    item = demo_service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items", response_model=DemoItem, status_code=201)
def create_demo_item(payload: DemoCreate):
    return demo_service.create_item(payload)

