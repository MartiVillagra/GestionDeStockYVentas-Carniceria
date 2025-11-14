from fastapi import APIRouter, Depends, HTTPException, status
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

#esta ruta sirve para verificar si hay una sesion activa
@router.get("/sesion/activa")
def sesion_activa(db: Session = Depends(get_db)):
    sesion = db.query(CajaSesion).filter(CajaSesion.fecha_cierre == None).first()
    if sesion:
        return {"active": True, "id_sesion": sesion.id_sesion, "monto_inicial": sesion.monto_inicial}
    return {"active": False}

#aqui cree esta ruta para abrir una nueva sesion de caja, si ya hay una abierta devuelve un error
@router.post("/sesion/abrir")
def abrir_caja(data: CajaOpen, db: Session = Depends(get_db)):
    if data.monto_inicial < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto inicial no puede ser negativo"
        )
    #comprueba si ya hay una sesion abierta
    sesion_abierta = db.query(CajaSesion).filter(CajaSesion.fecha_cierre == None).first()
    if sesion_abierta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya hay una sesión de caja abierta. Primero ciérrala antes de abrir otra."
        )
    
    #crea nueva sesion
    nueva = CajaSesion(
        **data.dict()
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return {"error": False, "message": "Sesión de caja abierta exitosamente.", "id_sesion": nueva.id_sesion}

#Esta ruta registra un movimiento en la caja
@router.post("/movimiento")
def registrar_movimiento(data: MovimientoIn, db: Session = Depends(get_db)):
    if data.monto < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto del movimiento no puede ser negativo"
        )

    # Validar tipo_movimiento
    tipo = data.tipo_movimiento.lower()
    if tipo not in ("ingreso", "egreso"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de movimiento debe ser 'ingreso' o 'egreso'"
        )
    # Verificar que la sesión de caja esté activa
    sesion = db.query(CajaSesion).filter(
        CajaSesion.id_sesion == data.id_sesion,
        CajaSesion.fecha_cierre == None
    ).first()
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe una sesión activa con ese ID"
        )
    mov = MovimientoCaja(**data.dict())
    db.add(mov)
    db.commit()
    return {
        "error": False,
        "message": f"Movimiento de tipo '{tipo}' registrado correctamente."
    }


#Esta ruta cierra la secion de caja activa
@router.post("/sesion/cerrar")
def cerrar_caja(data: CajaClose, db: Session = Depends(get_db)):
    if data.monto_contado < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El monto contado no puede ser negativo"
        )
    # Buscar la sesión
    sesion = db.query(CajaSesion).filter(CajaSesion.id_sesion == data.id_sesion).first()
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró una sesión con ese ID"
        )
    #esto evita el cierre doble
    if sesion.fecha_cierre is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esa sesión ya fue cerrada"
        )
    #calcular ingresos y egresos automaticamente
    movimientos = db.query(MovimientoCaja).filter(
        MovimientoCaja.id_sesion == data.id_sesion
    ).all()

    total_ingresos = sum(m.monto for m in movimientos if m.tipo_movimiento.lower() == "ingreso")
    total_egresos = sum(m.monto for m in movimientos if m.tipo_movimiento.lower() == "egreso")

    #Monto que deberia de haber segun los registros
    monto_esperado = sesion.monto_inicial + total_ingresos - total_egresos

    #guardar datos de cierre
    sesion.fecha_cierre = datetime.now()
    sesion.monto_contado = data.monto_contado
    sesion.comentarios = data.comentarios
    db.commit()
    db.refresh(sesion)

    #calcular diferencia real 
    diferencia = round(data.monto_contado - monto_esperado, 2)  
    
    #devuelve un resumen del cierre
    return {
        "id_sesion": sesion.id_sesion,
        "fecha_cierre": sesion.fecha_cierre,
        "monto_inicial": sesion.monto_inicial,
        "ingresos": total_ingresos,
        "egresos": total_egresos,
        "monto_esperado": monto_esperado,
        "monto_contado": data.monto_contado,
        "diferencia": diferencia
    }
    

  
    
      