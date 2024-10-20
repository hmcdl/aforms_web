"""
Основной модуль приожения AFORMES_WEB, позволяющего осуществлять 
многодисциплинарные расчеты самолетов
"""
import asyncio
import uvicorn
from uvicorn import Server, Config
from fastapi import FastAPI
from asyncio.windows_events import ProactorEventLoop
from app.database import engine, Base

from app.users.router import router, empty_router
from app.simulations.router import router as sim_router

# loop = asyncio.ProactorEventLoop()
# asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)
app.include_router(empty_router)
app.include_router(sim_router)

# class ProactorServer(Server):
#     def run(self, sockets=None):
#         loop = ProactorEventLoop()
#         asyncio.set_event_loop(loop) # since this is the default in Python 3.10, explicit selection can also be omitted
#         asyncio.run(self.serve(sockets=sockets))




# if __name__ == "__main__":
#     config = Config(app="app.main:app", host="localhost", port=8000, reload=True)
#     server = ProactorServer(config=config)
#     server.run()
    
#     # uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    loop = ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True))
    