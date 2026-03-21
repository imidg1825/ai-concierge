from pydantic import BaseModel
from typing import Any


class Product(BaseModel):
    category: str | None = None
    brand: str | None = None
    condition: str | None = None
    price: int | None = None
    attributes: dict[str, Any] = {}


class MessageRequest(BaseModel):
    text: str


class ProductResponse(BaseModel):
    category: str | None = None
    brand: str | None = None
    condition: str | None = None
    user_price_rub: int = 0
    attributes: dict[str, Any] = {}


class MarketResponse(BaseModel):
    query: str = ""
    min_price_rub: int = 0
    max_price_rub: int = 0
    median_price_rub: int = 0
    recommended_price_rub: int = 0


class AdResponse(BaseModel):
    title: str = ""
    description: str = ""
    recommended_price: int = 0


class MessageResponse(BaseModel):
    step: str
    message: str
    product: ProductResponse
    market: MarketResponse
    ad: AdResponse | None = None
    status: str
