from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import verify_api_key

router = APIRouter(prefix="/incidents", tags=["incident-logs"], dependencies=[Depends(verify_api_key)])


@router.post("/{incident_id}/logs", response_model=schemas.IncidentLogOut)
def add_log(incident_id: int, log: schemas.IncidentLogCreate, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    new_log = models.IncidentLog(incident_id=incident_id, note=log.note)
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/{incident_id}/logs", response_model=list[schemas.IncidentLogOut])
def get_logs(incident_id: int, db: Session = Depends(get_db)):
    return db.query(models.IncidentLog).filter(models.IncidentLog.incident_id == incident_id).all()