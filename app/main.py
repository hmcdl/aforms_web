"""
Основной модуль приожения AFORMES_WEB, позволяющего осуществлять 
многодисциплинарные расчеты самолетов
"""
import uvicorn
from fastapi import FastAPI
from app.database import engine, Base

from app.users.router import router, empty_router
from app.simulations.router import router as sim_router 
# import app.security.security




Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)
app.include_router(empty_router)
app.include_router(sim_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)