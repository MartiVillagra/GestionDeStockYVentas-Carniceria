#Define cómo se envían/reciben los datos en la API

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductoCreate(BaseModel):
    nombre_producto: str
    categoria: str | None = None
    precio_kilo: float = Field(..., ge=0)          
    tipo_venta: str
    stock_kilos: float = Field(0.0, ge=0)
    stock_unidades: float = Field(0.0, ge=0)
    peso_unidad_kg: float = Field(0.0, ge=0)


class ProductoOut(BaseModel):
    id_producto: int
    nombre_producto: str
    categoria: str
    precio_kilo: float        
    tipo_venta: str
    stock_kilos: float
    stock_unidades: float 
    peso_unidad_kg: float
    class Config:
        orm_mode = True

class CajaOpen(BaseModel):
    id_empleado: int
    monto_inicial: float

class MovimientoIn(BaseModel):
    id_sesion: int
    tipo_movimiento: str
    monto: float
    descripcion: str

class CajaClose(BaseModel):
    id_sesion: int
    monto_contado: float
    comentarios: Optional[str] = None