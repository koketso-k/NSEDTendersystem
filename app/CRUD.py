from sqlalchemy.orm import Session
from . import models, schemas

def create_tender(db: Session, tender: schemas.TenderCreate):
    db_tender = models.Tender(**tender.dict())
    db.add(db_tender)
    db.commit()
    db.refresh(db_tender)
    return db_tender

def get_tenders(db: Session, team_id: int):
    return db.query(models.Tender).filter(models.Tender.team_id == team_id).all()

def get_tender(db: Session, tender_id: int):
    return db.query(models.Tender).filter(models.Tender.tender_id == tender_id).first()

def update_tender(db: Session, tender_id: int, tender: schemas.TenderUpdate):
    db_tender = get_tender(db, tender_id)
    if db_tender:
        for key, value in tender.dict(exclude_unset=True).items():
            setattr(db_tender, key, value)
        db.commit()
        db.refresh(db_tender)
    return db_tender

def delete_tender(db: Session, tender_id: int):
    db_tender = get_tender(db, tender_id)
    if db_tender:
        db.delete(db_tender)
        db.commit()
    return db_tender
