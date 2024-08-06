from pydantic import BaseModel

class Simulation(BaseModel):
    id: int
    title : str
    owner_id : int

    class Config:
        orm_mode = True