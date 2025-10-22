
from fastapi import FastAPI
import uvicorn
import logging

from app.config.settings import settings
from app.routers import database

# Configurar logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API Documentation",
    description=settings.app_name,
    version=settings.app_version
)

# Incluir routers
app.include_router(database.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

