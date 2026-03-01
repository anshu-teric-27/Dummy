from typing import List

from app.models.demo import DemoItem, DemoCreate


_ITEMS: List[DemoItem] = [
    DemoItem(id=1, name="First item", description="Example payload"),
    DemoItem(id=2, name="Second item", description="Another example"),
]


def list_items() -> List[DemoItem]:
    return _ITEMS


def get_item(item_id: int) -> DemoItem | None:
    for item in _ITEMS:
        if item.id == item_id:
            return item
    return None


def create_item(payload: DemoCreate) -> DemoItem:
    next_id = max((item.id for item in _ITEMS), default=0) + 1
    new_item = DemoItem(id=next_id, **payload.dict())
    _ITEMS.append(new_item)
    return new_item

