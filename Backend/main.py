from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import productos, caja
import models

#Inicializamos la aplicacion
app = FastAPI(title="Sistema de Carnicería")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #Permite peticiones desde cualquier origen (ideal para desarrollo)
    allow_credentials=True,
    allow_methods=["*"],  #Permite todos los métodos: GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  #Permite todos los encabezados
)

#Creacion de la tabla (si no existe)
Base.metadata.create_all(bind=engine)

#Inclusion de las rutas
app.include_router(productos.router)
app.include_router(caja.router)

#Ruta raiz de prueba
@app.get("/")
def root():
    return {"message": "API de carnicería funcionando correctamente"}
