from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Photo:
    id: int
    url: str
    title: Optional[str]
    created_at: datetime
    user_id: int
    username: str
    email: str
    like_count: int
    comment_count: int

    @property
    def creation_date_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M") 