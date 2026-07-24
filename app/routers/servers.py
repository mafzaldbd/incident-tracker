from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import verify_api_key

router = APIRouter(prefix="/servers", tags=["servers"], dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=schemas.ServerOut)
def create_server(server: schemas.ServerCreate, db: Session = Depends(get_db)):
    new_server = models.Server(name=server.name, ip=server.ip)
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    return new_server


@router.get("/", response_model=list[schemas.ServerOut])
def list_servers(db: Session = Depends(get_db)):
    return db.query(models.Server).all()


@router.get("/{server_id}", response_model=schemas.ServerOut)
def get_server(server_id: int, db: Session = Depends(get_db)):
    server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.delete("/{server_id}")
def delete_server(server_id: int, db: Session = Depends(get_db)):
    server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Delete related incidents first (and their logs) to avoid a foreign key error
    incidents = db.query(models.Incident).filter(models.Incident.server_id == server_id).all()
    for incident in incidents:
        db.query(models.IncidentLog).filter(models.IncidentLog.incident_id == incident.id).delete()
    db.query(models.Incident).filter(models.Incident.server_id == server_id).delete()

    db.delete(server)
    db.commit()
    return {"detail": f"Server {server_id} and its related incidents/logs deleted"}