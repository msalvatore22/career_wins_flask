from dataclasses import field, dataclass
from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId

@dataclass(frozen=True)
class Win:
  title: Optional[str]
  description: Optional[str]
  impact: Optional[str]
  winDate: Optional[str]
  favorite: bool = False
  created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class User:
  full_name: str
  email: str
  wins: list[dict] = field(default_factory=list)
