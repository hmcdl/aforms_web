from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
from time import sleep

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    with open(r"/home/mikhail/Dev/Learn/aaa.txt", 'w') as f:
        f.
    # file.write(r"/home/mikhail/Dev/Learn/aaa.txt")
    return {"filename": file.filename}

@app.get("/example/")
def sync_ex():
    sleep(10)
    return "sync_ex executed"

@app.get("/example2/")
def sync_ex2():
    # sleep(10)
    return "sync_ex2 executed"

@app.get("/example3/")
async def async_ex():
    sleep(10)
    return "async_ex executed"