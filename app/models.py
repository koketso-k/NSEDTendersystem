from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from .database import Base

class Tender(Base):
    __tablename__ = "tenders"

    tender_id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, index=True)  # For multi-tenant access
    title = Column(String, nullable=False)
    description = Column(String)
    deadline = Column(Date)
    province = Column(String)
    buyer = Column(String)
    budget = Column(Float)
