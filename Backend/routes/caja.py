from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import CajaSesion, MovimientoCaja
from schemas import CajaOpen, MovimientoIn, CajaClose
from sqlalchemy import and_, func
from datetime import datetime

router = APIRouter(prefix="/caja", tags=["Caja"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sesion/activa")
def sesion_activa(db: Session = Depends(get_db)):
    sesion = db.query(CajaSesion).filter(CajaSesion.fecha_cierre == None).first()
    if sesion:
        return {"active": True, "id_sesion": sesion.id_sesion, "monto_inicial": sesion.monto_inicial}
    return {"active": False}

@router.post("/sesion/abrir")
def abrir_caja(data: CajaOpen, db: Session = Depends(get_db)):
    sesion_abierta = db.query(CajaSesion).filter(CajaSesion.fecha_cierre == None).first()
    if sesion_abierta:
        return {"error": True, "message": "Ya hay una sesión abierta"}
    nueva = CajaSesion(
        **data.dict(),
        fecha_apertura=datetime.now()
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"error": False, "id_sesion": nueva.id_sesion}

@router.post("/movimiento")
def registrar_movimiento(data: MovimientoIn, db: Session = Depends(get_db)):
    mov = MovimientoCaja(**data.dict())
    db.add(mov)
    db.commit()
    return {"error": False, "message": "Movimiento registrado"}

@router.post("/sesion/cerrar")
def cerrar_caja(data: CajaClose, db: Session = Depends(get_db)):
    sesion = db.query(CajaSesion).filter(CajaSesion.id_sesion == data.id_sesion).first()
    if not sesion:
        return {"error": True, "message": "Sesión no encontrada"}
    sesion.fecha_cierre = datetime.now()
    sesion.monto_contado = data.monto_contado
    sesion.comentarios = data.comentarios
    db.commit()
    return {"error": False, "balance": {"diferencia": (data.monto_contado - sesion.monto_inicial)}} 
