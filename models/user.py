from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id:            int
    full_name:     str
    email:         str
    role:          str
    phone:         Optional[str]    = None
    avatar_path:   Optional[str]    = None
    is_active:     int              = 1
    created_at:    Optional[datetime] = None
    last_login:    Optional[datetime] = None