import uvicorn
from fastapi import FastAPI
from instrument_api import router as instrument_router
from vwap_api import router as vwap_router



app = FastAPI()

app.include_router(instrument_router)
app.include_router(vwap_router)

