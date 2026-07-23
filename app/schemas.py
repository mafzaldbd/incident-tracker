from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---- Server schemas ----

class ServerBase(BaseModel):
    name: str
    ip: Optional[str] = None

class ServerCreate(ServerBase):
    pass   # same fields as base, for now — but kept separate in case create needs differ later

class ServerOut(ServerBase):
    id: int
    status: str
    last_checked: Optional[datetime] = None

    class Config:
        from_attributes = True   # lets Pydantic read data straight off a SQLAlchemy object


# ---- Incident schemas ----

class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: Optional[str] = "medium"

class IncidentCreate(IncidentBase):
    server_id: int

class IncidentOut(IncidentBase):
    id: int
    server_id: int
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---- Incident Log schemas ----

class IncidentLogCreate(BaseModel):
    note: str

class IncidentLogOut(BaseModel):
    id: int
    incident_id: int
    note: str
    created_at: datetime

    class Config:
        from_attributes = True