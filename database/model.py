from dataclasses import field, dataclass
from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId
from itertools import count


@dataclass(frozen=True)
class Win:
  title: Optional[str]
  description: Optional[str]
  impact: Optional[str]
  winDate: Optional[str]
  favorite: bool = False
  created_at: datetime = field(default_factory=datetime.utcnow)
  id: int = field(default_factory=count().__next__, init=False)

@dataclass(frozen=True)
class User:
  full_name: str
  email: str
  password: str
  wins: list[dict] = field(default_factory=list)
