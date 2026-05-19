from dataclasses import dataclass
from typing import Optional

@dataclass
class MenuItem:
    id:           int
    category_id:  int
    name:         str
    base_price:   float
    description:  Optional[str] = None
    image_path:   Optional[str] = None
    is_available: int           = 1
    is_featured:  int           = 0
    category_name: Optional[str] = None  # JOIN từ categories