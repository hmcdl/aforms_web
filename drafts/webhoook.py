from fastapi import FastAPI, Request
import uvicorn


app = FastAPI()

@app.get("/")
async def home():
    return {"message": "Hello World"}

@app.post("/webhook")
async def receive_webhook(request: Request):
    r = request
    print(r.client.host, r.client.port)
    data = await request.body()
    # address = request.
    # Process your data here
    print (data)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000,)