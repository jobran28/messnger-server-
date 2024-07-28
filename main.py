from fastapi import FastAPI
import uvicorn
from webhook import router as webhook_router

app = FastAPI()

app.include_router(webhook_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
