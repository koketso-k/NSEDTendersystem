from pydantic import BaseModel
from datetime import date
from typing import Optional

class TenderBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    province: Optional[str] = None
    buyer: Optional[str] = None
    budget: Optional[float] = None

class TenderCreate(TenderBase):
    team_id: int  # Required when creating

class TenderUpdate(TenderBase):
    pass

class TenderOut(TenderBase):
    tender_id: int
    team_id: int

    class Config:
        orm_mode = True
