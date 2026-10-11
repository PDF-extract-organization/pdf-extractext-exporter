from fastapi import FastAPI

from app.presentation.routers import exporter

app = FastAPI(title="pdf-extractext-exporter")
app.include_router(exporter.router)
