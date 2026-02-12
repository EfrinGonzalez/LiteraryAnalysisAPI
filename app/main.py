from fastapi import FastAPI
from app.routes import router
from app.database import init_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Literary Analysis API",
    description="API for analyzing text, URLs, and images with sentiment analysis",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logging.info("Database initialized")

app.include_router(router)