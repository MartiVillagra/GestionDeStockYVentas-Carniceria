from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Producto
from schemas import ProductoCreate, ProductoOut
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/productos", tags=["Productos"])

#Aqui estamos abriendo una dependencia que abre y cierra la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[ProductoOut]) #Aqui obtenemos la lista de productos que pusimos en el archivo schemas
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos

#Cree este get para traer un producto por su id, si el id no existe devuelve un error 404
@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id_producto == producto_id).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto

#Y aqui creamos un producto nuevo, y devuelve 201 created con el objeto creado
@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(prod: ProductoCreate, db: Session = Depends(get_db)):
    nuevo = Producto(**prod.dict())
    try:
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)  # refresca campos automáticos 
    except SQLAlchemyError as e:
        db.rollback() #en caso de error, rollback mantiene la integridad de la base de datos
        raise HTTPException(status_code=500, detail="Error al crear el producto")
    return nuevo

#cree esta ruta para actualizar un producto existente
@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, datos: ProductoCreate, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id_producto == producto_id).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    # setattr sirve para asignar valores de forma automatica sin tener que estar haciendolo uno por uno
    for key, value in datos.dict().items():
        setattr(producto, key, value)

    try:
        db.commit()
        db.refresh(producto)
    except SQLAlchemyError:
        db.rollback() #en caso de error, rollback mantiene la integridad de la base de datos
        raise HTTPException(status_code=500, detail="Error al actualizar el producto")
    return producto

#Borra productos y devuelve 204 no content si se borro correctamente
@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id_producto == producto_id).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    try:
        db.delete(producto)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el producto")
    return None

#Sirve para ajustar solo el stock (kilos o unidades) de un producto
@router.patch("/{producto_id}/stock", response_model=ProductoOut)
def ajustar_stock(producto_id: int, nuevo_stock_kilos: float = None, nuevo_stock_unidades: float = None,
                   db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id_producto == producto_id).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    if nuevo_stock_kilos is not None:
        producto.stock_kilos = nuevo_stock_kilos
    if nuevo_stock_unidades is not None:
        producto.stock_unidades = nuevo_stock_unidades

    try:
        db.commit()
        db.refresh(producto)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el stock")
    return producto
