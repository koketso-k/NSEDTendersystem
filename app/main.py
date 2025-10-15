from fastapi import FastAPI
from app.routers import tenders
from app.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tender Insight Hub - Phase 2")

app.include_router(tenders.router)
