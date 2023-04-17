from dataclasses import field, dataclass
from datetime import datetime
from typing import Optional
from itertools import count
import uuid

def get_new_uuid() -> str:
  return str(uuid.uuid1())

@dataclass(frozen=True)
class Win:
  title: Optional[str]
  description: Optional[str]
  impact: Optional[str]
  winDate: Optional[str]
  favorite: bool = False
  created_at: datetime = field(default_factory=datetime.utcnow)
  tags: list[str] = field(default_factory=list)
  id: str = field(default_factory=get_new_uuid)

@dataclass(frozen=True)
class User:
  firstName: str
  lastName: str
  email: str
  password: bytes
  industry: str
  jobTitle: str
  wins: list[dict] = field(default_factory=list)
