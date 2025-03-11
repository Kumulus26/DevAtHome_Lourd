from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    email: str
    profile_image: Optional[str]
    created_at: Optional[datetime] = None
    comment_count: int = 0
    like_count: int = 0
    photo_count: int = 0
    role: int = 1  # Default role is 1 (regular user), 2 is admin

    @property
    def creation_date_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "" 