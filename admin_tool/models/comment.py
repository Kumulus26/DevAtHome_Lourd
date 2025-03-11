from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Comment:
    id: int
    content: str
    created_at: datetime
    user_id: int
    photo_id: int
    username: str
    user_profile_image: Optional[str]
    photo_url: str
    photo_title: Optional[str]

    @property
    def creation_date_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M") 