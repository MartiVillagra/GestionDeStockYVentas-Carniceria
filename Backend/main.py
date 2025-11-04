from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Mensaje": "Bienvenido a la API de Gestión de Stock y Ventas de Carnicería"}