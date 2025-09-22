from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Literary Analysis API")
app.include_router(router)