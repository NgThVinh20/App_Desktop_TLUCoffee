from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class OrderItem:
    id:         int
    order_id:   int
    item_id:    int
    item_name:  str
    unit_price: float
    quantity:   int
    subtotal:   float
    note:       Optional[str] = None

@dataclass
class Order:
    id:             int
    order_code:     str
    user_id:        int
    subtotal:       float
    total_amount:   float
    status:         str
    payment_method: str
    table_number:   Optional[int]       = None
    discount:       float               = 0
    tax:            float               = 0
    note:           Optional[str]       = None
    created_at:     Optional[datetime]  = None
    items:          List[OrderItem]     = None
    staff_name:     Optional[str]       = None  # JOIN từ users