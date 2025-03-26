import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


storage = {
    1: Item(name="phone", price=9999.999),
    2: Item(name="Plane", price=10000000.0)
}


@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}


@app.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    print(item_id)
    if item_id not in storage:
        raise HTTPException(status_code=404, detail='Not found.')
    return storage[item_id]


@app.post("/items/")
def create_item(item: Item) -> int:
    item_id = max(storage.keys()) + 1 if storage else 1
    storage[max(storage.keys()) + 1] = item
    return item_id

@app.update("/items/{item_id}")
def update_item(item_id: int) -> Item:
    if item_id not in storage:
        raise HTTPException(status_code=404, detail='Not found.')



uvicorn.run(app, host="0.0.0.0", port=8888)