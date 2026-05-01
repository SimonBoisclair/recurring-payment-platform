from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes_api import router as api_router
from app.routes_public import router as public_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="RecurPay", description="Recurring Payment Platform", lifespan=lifespan)

app.include_router(api_router)
app.include_router(public_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def admin_dashboard():
    return FileResponse("static/index.html")
