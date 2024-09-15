from pydantic import BaseModel

class Simulation(BaseModel):
    id: int
    title : str
    owner_id : int

    class Config:
        orm_mode = True

class SimulationCreate(BaseModel):
    title : str

class foobar_schema(BaseModel):
    k: int
    d: int

class conver_args(BaseModel):
    iters: int = 1
    simulation: int = 1
    aeroratio: float = 1.5