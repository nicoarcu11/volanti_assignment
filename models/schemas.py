from pydantic import BaseModel
from typing import Optional

class OrderExtraction(BaseModel):
    has_order_id: bool
    order_id: Optional[str] = None

class ProductSearchExtraction(BaseModel):
    needs_query: bool
    query: Optional[str] = None

class DeriveToHumanExtraction(BaseModel):
    reason: str

class ToolExecutor(BaseModel):
    tools: list[str]