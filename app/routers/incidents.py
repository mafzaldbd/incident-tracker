from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import verify_api_key

router = APIRouter(prefix="/incidents", tags=["incidents"], dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=schemas.IncidentOut)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    server = db.query(models.Server).filter(models.Server.id == incident.server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    new_incident = models.Incident(
        server_id=incident.server_id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident


@router.get("/", response_model=list[schemas.IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(models.Incident).all()


@router.patch("/{incident_id}", response_model=schemas.IncidentOut)
def update_incident_status(incident_id: int, status: str, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = status
    db.commit()
    db.refresh(incident)
    return incident

@router.delete("/{incident_id}")
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    db.query(models.IncidentLog).filter(models.IncidentLog.incident_id == incident_id).delete()
    db.delete(incident)
    db.commit()
    return {"detail": f"Incident {incident_id} and its logs deleted"}